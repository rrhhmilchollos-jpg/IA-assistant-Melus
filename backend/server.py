from fastapi import FastAPI, APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List
import uuid
import httpx

from models import (
    User, UserSession, SessionRequest, SessionResponse,
    Conversation, ConversationListItem, ConversationCreate,
    Message, MessageCreate, MessageEdit, MessageResponse, AIModel,
    CreditBalance, CreditPackage, CheckoutRequest,
    PaymentTransaction, TransactionHistory
)
from config import CREDIT_PACKAGES, FREE_CREDITS, PROMO_CODES, CREDITS_PER_DOLLAR, AI_MODELS, DEFAULT_MODEL
from utils import generate_id, utc_now, ensure_timezone, get_authenticated_user

# Import integrations
from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest, CheckoutSessionResponse
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Environment variables
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== Authentication Endpoints ====================

@api_router.post("/auth/session", response_model=SessionResponse)
async def create_session(request: Request, session_request: SessionRequest):
    """Exchange session_id from OAuth for session_token"""
    try:
        # Call Emergent Auth to get user data
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_request.session_id},
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session_id")
            
            auth_data = response.json()
        
        # Check if user exists
        user_doc = await db.users.find_one(
            {"email": auth_data["email"]},
            {"_id": 0}
        )
        
        if user_doc:
            # Update existing user
            await db.users.update_one(
                {"email": auth_data["email"]},
                {
                    "$set": {
                        "name": auth_data["name"],
                        "picture": auth_data["picture"],
                        "updated_at": utc_now()
                    }
                }
            )
            user_id = user_doc["user_id"]
        else:
            # Create new user
            user_id = generate_id("user")
            new_user = {
                "user_id": user_id,
                "email": auth_data["email"],
                "name": auth_data["name"],
                "picture": auth_data["picture"],
                "credits": FREE_CREDITS,
                "credits_used": 0,
                "created_at": utc_now(),
                "updated_at": utc_now()
            }
            await db.users.insert_one(new_user)
        
        # Create session
        session_token = auth_data.get("session_token") or generate_id("session")
        session_id = generate_id("sess")
        expires_at = utc_now() + timedelta(days=7)
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at,
            "created_at": utc_now()
        }
        await db.user_sessions.insert_one(session_data)
        
        # Get updated user data
        user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
        user = User(**user_doc)
        
        return SessionResponse(user=user, session_token=session_token)
        
    except httpx.RequestError as e:
        logger.error(f"Auth service error: {e}")
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    except Exception as e:
        logger.error(f"Session creation error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/auth/me")
async def get_current_user(request: Request):
    """Get current authenticated user"""
    user_doc = await get_authenticated_user(request, db)
    return User(**user_doc)

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Logout user"""
    session_token = request.cookies.get("session_token")
    
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    
    response.delete_cookie(
        "session_token",
        path="/",
        secure=True,
        httponly=True,
        samesite="none"
    )
    
    return {"message": "Logged out successfully"}

# ==================== AI Models Endpoint ====================

@api_router.get("/models", response_model=List[AIModel])
async def get_available_models():
    """Get available AI models"""
    models = []
    for model_id, data in AI_MODELS.items():
        models.append(AIModel(
            model_id=model_id,
            name=data["name"],
            provider=data["provider"],
            description=data["description"],
            popular=data["popular"]
        ))
    return models

# ==================== Conversation Endpoints ====================

@api_router.get("/conversations", response_model=List[ConversationListItem])
async def get_conversations(request: Request):
    """Get all conversations for authenticated user"""
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    conversations = await db.conversations.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("updated_at", -1).to_list(100)
    
    # Get message count for each conversation
    result = []
    for conv in conversations:
        message_count = await db.messages.count_documents({
            "conversation_id": conv["conversation_id"]
        })
        result.append(ConversationListItem(
            conversation_id=conv["conversation_id"],
            title=conv["title"],
            model=conv.get("model", DEFAULT_MODEL),
            updated_at=conv["updated_at"],
            message_count=message_count,
            forked_from=conv.get("forked_from")
        ))
    
    return result

@api_router.post("/conversations", response_model=Conversation)
async def create_conversation(request: Request, conv_create: ConversationCreate):
    """Create new conversation or fork existing one"""
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    conversation = {
        "conversation_id": generate_id("conv"),
        "user_id": user_id,
        "title": conv_create.title,
        "model": conv_create.model or DEFAULT_MODEL,
        "forked_from": conv_create.fork_from,
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    
    await db.conversations.insert_one(conversation)
    
    # If forking, copy messages from source conversation
    if conv_create.fork_from:
        source_conv = await db.conversations.find_one({
            "conversation_id": conv_create.fork_from,
            "user_id": user_id
        })
        
        if source_conv:
            # Copy all messages from source
            source_messages = await db.messages.find({
                "conversation_id": conv_create.fork_from
            }, {"_id": 0}).to_list(1000)
            
            if source_messages:
                forked_messages = []
                for msg in source_messages:
                    new_msg = msg.copy()
                    new_msg["message_id"] = generate_id("msg")
                    new_msg["conversation_id"] = conversation["conversation_id"]
                    forked_messages.append(new_msg)
                
                await db.messages.insert_many(forked_messages)
            
            # Update title to indicate fork
            conversation["title"] = f"Fork: {source_conv.get('title', 'Conversation')}"
            await db.conversations.update_one(
                {"conversation_id": conversation["conversation_id"]},
                {"$set": {"title": conversation["title"]}}
            )
    
    return Conversation(**conversation)
        "updated_at": utc_now()
    }
    return Conversation(**conversation)

@api_router.delete("/conversations/{conversation_id}")
async def delete_conversation(request: Request, conversation_id: str):
    """Delete a conversation and all its messages"""
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Check if conversation belongs to user
    conv = await db.conversations.find_one({
        "conversation_id": conversation_id,
        "user_id": user_id
    })
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete conversation and all messages
    await db.conversations.delete_one({"conversation_id": conversation_id})
    await db.messages.delete_many({"conversation_id": conversation_id})
    
    return {"message": "Conversation deleted"}

# ==================== Message Endpoints ====================

@api_router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_messages(request: Request, conversation_id: str):
    """Get all messages in a conversation"""
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Verify conversation belongs to user
    conv = await db.conversations.find_one({
        "conversation_id": conversation_id,
        "user_id": user_id
    })
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await db.messages.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(1000)
    
    return [Message(**msg) for msg in messages]

@api_router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(request: Request, conversation_id: str, message_create: MessageCreate):
    """Send message and get AI response"""
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Verify conversation belongs to user
    conv = await db.conversations.find_one({
        "conversation_id": conversation_id,
        "user_id": user_id
    })
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check if user has enough credits (minimum 100 for safety)
    if user_doc["credits"] < 100:
        raise HTTPException(
            status_code=402,
            detail="Insufficient credits. Please purchase more credits to continue."
        )
    
    # Save user message
    user_message_data = {
        "message_id": generate_id("msg"),
        "conversation_id": conversation_id,
        "user_id": user_id,
        "role": "user",
        "content": message_create.content,
        "tokens_used": 0,
        "timestamp": utc_now()
    }
    await db.messages.insert_one(user_message_data)
    user_message = Message(**user_message_data)
    
    try:
        # Get conversation history for context
        previous_messages = await db.messages.find(
            {"conversation_id": conversation_id},
            {"_id": 0}
        ).sort("timestamp", 1).limit(20).to_list(20)
        
        # Initialize LLM Chat
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=conversation_id,
            system_message="¡Hola! Soy Assistant Melus, tu asistente de inteligencia artificial. Estoy aquí para ayudarte con cualquier pregunta o tarea que necesites. Puedo ayudarte con: responder preguntas sobre cualquier tema, ayudarte con programación y código, escribir y editar textos, analizar información, resolver problemas, y mucho más. Soy amigable, servicial y siempre respondo en español a menos que me pidas lo contrario."
        )
        
        # Use GPT-4o model
        chat.with_model("openai", "gpt-4o")
        
        # Send message and get response
        user_msg = UserMessage(text=message_create.content)
        ai_response = await chat.send_message(user_msg)
        
        # Calculate tokens used (rough estimation based on response length)
        # In production, you should get this from the OpenAI response metadata
        tokens_used = len(message_create.content.split()) * 1.3 + len(ai_response.split()) * 1.3
        tokens_used = int(tokens_used)
        
        # Save assistant message
        assistant_message_data = {
            "message_id": generate_id("msg"),
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": "assistant",
            "content": ai_response,
            "tokens_used": tokens_used,
            "timestamp": utc_now()
        }
        await db.messages.insert_one(assistant_message_data)
        assistant_message = Message(**assistant_message_data)
        
        # Deduct credits from user
        new_credits = user_doc["credits"] - tokens_used
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {"credits": new_credits},
                "$inc": {"credits_used": tokens_used}
            }
        )
        
        # Update conversation title if it's the first message
        if len(previous_messages) == 0:
            title = message_create.content[:50] + ("..." if len(message_create.content) > 50 else "")
            await db.conversations.update_one(
                {"conversation_id": conversation_id},
                {"$set": {"title": title, "updated_at": utc_now()}}
            )
        else:
            await db.conversations.update_one(
                {"conversation_id": conversation_id},
                {"$set": {"updated_at": utc_now()}}
            )
        
        return MessageResponse(
            user_message=user_message,
            assistant_message=assistant_message,
            tokens_used=tokens_used,
            credits_remaining=new_credits
        )
        
    except Exception as e:
        logger.error(f"AI response error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI response: {str(e)}")

@api_router.put("/messages/{message_id}", response_model=Message)
async def edit_message(request: Request, message_id: str, message_edit: MessageEdit):
    """Edit a user message"""
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Find the message
    message = await db.messages.find_one({
        "message_id": message_id,
        "user_id": user_id,
        "role": "user"
    }, {"_id": 0})
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Store original content if not already edited
    original_content = message.get("original_content", message["content"])
    
    # Update message
    await db.messages.update_one(
        {"message_id": message_id},
        {
            "$set": {
                "content": message_edit.content,
                "edited": True,
                "original_content": original_content,
                "timestamp": utc_now()
            }
        }
    )
    
    # Get updated message
    updated_message = await db.messages.find_one({"message_id": message_id}, {"_id": 0})
    return Message(**updated_message)

@api_router.post("/messages/{message_id}/regenerate", response_model=Message)
async def regenerate_message(request: Request, message_id: str):
    """Regenerate an assistant message"""
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Find the message
    message = await db.messages.find_one({
        "message_id": message_id,
        "user_id": user_id,
        "role": "assistant"
    }, {"_id": 0})
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    conversation_id = message["conversation_id"]
    
    # Get conversation
    conv = await db.conversations.find_one({
        "conversation_id": conversation_id
    }, {"_id": 0})
    
    # Check credits
    if user_doc["credits"] < 100:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Get previous messages for context
    previous_messages = await db.messages.find({
        "conversation_id": conversation_id,
        "timestamp": {"$lt": message["timestamp"]}
    }, {"_id": 0}).sort("timestamp", 1).to_list(20)
    
    try:
        # Initialize LLM Chat
        model = conv.get("model", DEFAULT_MODEL)
        model_config = AI_MODELS.get(model, AI_MODELS[DEFAULT_MODEL])
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=conversation_id,
            system_message="¡Hola! Soy Assistant Melus, tu asistente de inteligencia artificial. Estoy aquí para ayudarte con cualquier pregunta o tarea que necesites. Puedo ayudarte con: responder preguntas sobre cualquier tema, ayudarte con programación y código, escribir y editar textos, analizar información, resolver problemas, y mucho más. Soy amigable, servicial y siempre respondo en español a menos que me pidas lo contrario."
        )
        
        chat.with_model(model_config["provider"], model)
        
        # Get the user message that this is responding to
        user_msg = previous_messages[-1] if previous_messages else None
        if not user_msg or user_msg["role"] != "user":
            raise HTTPException(status_code=400, detail="Cannot find user message to regenerate response")
        
        user_message = UserMessage(text=user_msg["content"])
        ai_response = await chat.send_message(user_message)
        
        # Calculate tokens
        tokens_used = int((len(user_msg["content"]) + len(ai_response)) / 4 * 1.3)
        
        # Update message
        await db.messages.update_one(
            {"message_id": message_id},
            {
                "$set": {
                    "content": ai_response,
                    "tokens_used": tokens_used,
                    "timestamp": utc_now()
                }
            }
        )
        
        # Deduct credits
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {"credits": user_doc["credits"] - tokens_used},
                "$inc": {"credits_used": tokens_used}
            }
        )
        
        # Get updated message
        updated_message = await db.messages.find_one({"message_id": message_id}, {"_id": 0})
        return Message(**updated_message)
        
    except Exception as e:
        logger.error(f"Regenerate error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to regenerate: {str(e)}")

# ==================== Credits & Payment Endpoints ====================

@api_router.get("/credits", response_model=CreditBalance)
async def get_credits(request: Request):
    """Get user's credit balance"""
    user_doc = await get_authenticated_user(request, db)
    return CreditBalance(
        credits=user_doc["credits"],
        credits_used=user_doc["credits_used"]
    )

@api_router.get("/credits/packages", response_model=List[CreditPackage])
async def get_credit_packages():
    """Get available credit packages"""
    packages = []
    for package_id, data in CREDIT_PACKAGES.items():
        packages.append(CreditPackage(
            package_id=package_id,
            name=data["name"],
            credits=data["credits"],
            price=data["price"],
            popular=data["popular"],
            bonus=data.get("bonus", 0),
            base_credits=data.get("base_credits")
        ))
    return packages

@api_router.post("/credits/validate-promo")
async def validate_promo_code(request: Request, promo_data: dict):
    """Validate promo code"""
    promo_code = promo_data.get("promo_code", "").upper()
    amount = promo_data.get("amount", 0)
    
    if promo_code not in PROMO_CODES:
        raise HTTPException(status_code=400, detail="Invalid promo code")
    
    promo = PROMO_CODES[promo_code]
    
    if not promo["active"]:
        raise HTTPException(status_code=400, detail="Promo code expired")
    
    if amount < promo["min_amount"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Promo code requires minimum ${promo['min_amount']} purchase"
        )
    
    discount = amount * promo["discount"]
    final_amount = amount - discount
    
    return {
        "valid": True,
        "discount": discount,
        "discount_percent": promo["discount"] * 100,
        "final_amount": final_amount,
        "original_amount": amount
    }

@api_router.post("/credits/checkout")
async def create_checkout_session(request: Request, checkout_req: CheckoutRequest):
    """Create Stripe checkout session for purchasing credits"""
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Determine if it's a package or custom amount
    if checkout_req.package_id:
        # Package purchase
        if checkout_req.package_id not in CREDIT_PACKAGES:
            raise HTTPException(status_code=400, detail="Invalid package")
        
        package_data = CREDIT_PACKAGES[checkout_req.package_id]
        amount = package_data["price"]
        credits = package_data["credits"]
        package_id = checkout_req.package_id
        
    elif checkout_req.custom_amount:
        # Custom amount purchase
        amount = checkout_req.custom_amount
        if amount < 1:
            raise HTTPException(status_code=400, detail="Minimum amount is $1")
        
        credits = int(amount * CREDITS_PER_DOLLAR)
        package_id = "custom"
    else:
        raise HTTPException(status_code=400, detail="Must provide package_id or custom_amount")
    
    # Apply promo code if provided
    discount = 0
    promo_code = None
    if checkout_req.promo_code:
        promo_code = checkout_req.promo_code.upper()
        if promo_code in PROMO_CODES:
            promo = PROMO_CODES[promo_code]
            if promo["active"] and amount >= promo["min_amount"]:
                discount = amount * promo["discount"]
                amount = amount - discount
    
    # Initialize Stripe checkout
    host_url = checkout_req.origin_url
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(
        api_key=STRIPE_API_KEY,
        webhook_url=webhook_url
    )
    
    # Create checkout URLs
    success_url = f"{host_url}/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{host_url}/pricing"
    
    # Create checkout session
    checkout_request = CheckoutSessionRequest(
        amount=amount,
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": user_id,
            "package_id": package_id,
            "credits": str(credits),
            "promo_code": promo_code or "",
            "discount": str(discount)
        }
    )
    
    session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Create payment transaction record
    transaction = {
        "transaction_id": generate_id("txn"),
        "user_id": user_id,
        "stripe_session_id": session.session_id,
        "package_id": package_id,
        "amount": amount,
        "currency": "usd",
        "credits": credits,
        "promo_code": promo_code,
        "discount": discount,
        "status": "pending",
        "payment_status": "unpaid",
        "processed": False,
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    await db.payment_transactions.insert_one(transaction)
    
    return {"checkout_url": session.url, "session_id": session.session_id}

@api_router.get("/credits/checkout/status/{session_id}")
async def get_checkout_status(request: Request, session_id: str):
    """Check payment status and add credits if paid"""
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Find transaction
    transaction = await db.payment_transactions.find_one(
        {"stripe_session_id": session_id, "user_id": user_id},
        {"_id": 0}
    )
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # If already processed, return status
    if transaction["processed"]:
        return {
            "status": transaction["status"],
            "payment_status": transaction["payment_status"],
            "credits_added": transaction["credits"]
        }
    
    # Initialize Stripe checkout
    webhook_url = f"{request.base_url}api/webhook/stripe"
    stripe_checkout = StripeCheckout(
        api_key=STRIPE_API_KEY,
        webhook_url=webhook_url
    )
    
    # Get checkout status from Stripe
    try:
        checkout_status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction
        await db.payment_transactions.update_one(
            {"stripe_session_id": session_id},
            {
                "$set": {
                    "status": checkout_status.status,
                    "payment_status": checkout_status.payment_status,
                    "updated_at": utc_now()
                }
            }
        )
        
        # If payment is complete and not yet processed, add credits
        if checkout_status.payment_status == "paid" and not transaction["processed"]:
            # Add credits to user
            await db.users.update_one(
                {"user_id": user_id},
                {"$inc": {"credits": transaction["credits"]}}
            )
            
            # Mark transaction as processed
            await db.payment_transactions.update_one(
                {"stripe_session_id": session_id},
                {"$set": {"processed": True, "updated_at": utc_now()}}
            )
            
            return {
                "status": checkout_status.status,
                "payment_status": checkout_status.payment_status,
                "credits_added": transaction["credits"]
            }
        
        return {
            "status": checkout_status.status,
            "payment_status": checkout_status.payment_status,
            "credits_added": 0
        }
        
    except Exception as e:
        logger.error(f"Checkout status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check payment status")

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        webhook_url = f"{request.base_url}api/webhook/stripe"
        stripe_checkout = StripeCheckout(
            api_key=STRIPE_API_KEY,
            webhook_url=webhook_url
        )
        
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Process webhook event
        if webhook_response.event_type == "checkout.session.completed":
            session_id = webhook_response.session_id
            
            # Find transaction
            transaction = await db.payment_transactions.find_one(
                {"stripe_session_id": session_id},
                {"_id": 0}
            )
            
            if transaction and not transaction["processed"]:
                # Add credits to user
                await db.users.update_one(
                    {"user_id": transaction["user_id"]},
                    {"$inc": {"credits": transaction["credits"]}}
                )
                
                # Mark transaction as processed
                await db.payment_transactions.update_one(
                    {"stripe_session_id": session_id},
                    {
                        "$set": {
                            "processed": True,
                            "status": "completed",
                            "payment_status": "paid",
                            "updated_at": utc_now()
                        }
                    }
                )
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse(status_code=400, content={"error": str(e)})

# ==================== Root Endpoint ====================

@api_router.get("/")
async def root():
    return {"message": "Assistant Melus API", "version": "1.0.0"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
