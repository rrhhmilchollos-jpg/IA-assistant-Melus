"""Conversation/Chat routes for Assistant Melus"""
from fastapi import APIRouter, HTTPException, Request
from typing import List
import logging
import os
import re

from models import (
    Conversation, ConversationListItem, ConversationCreate,
    Message, MessageCreate, MessageEdit, MessageResponse, AIModel
)
from config import AI_MODELS, DEFAULT_MODEL
from utils import generate_id, utc_now, get_authenticated_user

from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

router = APIRouter(tags=["conversations"])

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')


@router.get("/models", response_model=List[AIModel])
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


@router.get("/conversations", response_model=List[ConversationListItem])
async def get_conversations(request: Request):
    """Get all conversations for authenticated user"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$lookup": {
            "from": "messages",
            "localField": "conversation_id",
            "foreignField": "conversation_id",
            "as": "messages_list"
        }},
        {"$addFields": {"message_count": {"$size": "$messages_list"}}},
        {"$project": {"messages_list": 0, "_id": 0}},
        {"$sort": {"updated_at": -1}},
        {"$limit": 100}
    ]
    
    conversations = await db.conversations.aggregate(pipeline).to_list(100)
    
    result = []
    for conv in conversations:
        result.append(ConversationListItem(
            conversation_id=conv["conversation_id"],
            title=conv["title"],
            model=conv.get("model", DEFAULT_MODEL),
            updated_at=conv["updated_at"],
            message_count=conv.get("message_count", 0),
            forked_from=conv.get("forked_from")
        ))
    
    return result


@router.post("/conversations", response_model=Conversation)
async def create_conversation(request: Request, conv_create: ConversationCreate):
    """Create new conversation or fork existing one"""
    db = request.app.state.db
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
    
    if conv_create.fork_from:
        source_conv = await db.conversations.find_one({
            "conversation_id": conv_create.fork_from,
            "user_id": user_id
        })
        
        if source_conv:
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
            
            conversation["title"] = f"Fork: {source_conv.get('title', 'Conversation')}"
            await db.conversations.update_one(
                {"conversation_id": conversation["conversation_id"]},
                {"$set": {"title": conversation["title"]}}
            )
    
    return Conversation(**conversation)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(request: Request, conversation_id: str):
    """Delete a conversation and all its messages"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    conv = await db.conversations.find_one({
        "conversation_id": conversation_id,
        "user_id": user_id
    })
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await db.conversations.delete_one({"conversation_id": conversation_id})
    await db.messages.delete_many({"conversation_id": conversation_id})
    
    return {"message": "Conversation deleted"}


@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_messages(request: Request, conversation_id: str):
    """Get all messages in a conversation"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
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


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(request: Request, conversation_id: str, message_create: MessageCreate):
    """Send message and get AI response"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    conv = await db.conversations.find_one({
        "conversation_id": conversation_id,
        "user_id": user_id
    })
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check if user has unlimited credits (owner)
    is_unlimited = user_doc.get("unlimited_credits", False) or user_doc.get("is_owner", False)
    
    if not is_unlimited and user_doc["credits"] < 100:
        raise HTTPException(
            status_code=402,
            detail="Insufficient credits. Please purchase more credits to continue."
        )
    
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
        previous_messages = await db.messages.find(
            {"conversation_id": conversation_id},
            {"_id": 0}
        ).sort("timestamp", 1).limit(20).to_list(20)
        
        model = conv.get("model", DEFAULT_MODEL)
        model_config = AI_MODELS.get(model, AI_MODELS[DEFAULT_MODEL])
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=conversation_id,
            system_message="¡Hola! Soy Assistant Melus, tu asistente de inteligencia artificial. Estoy aquí para ayudarte con cualquier pregunta o tarea que necesites. Puedo ayudarte con: responder preguntas sobre cualquier tema, ayudarte con programación y código, escribir y editar textos, analizar información, resolver problemas, y mucho más. Soy amigable, servicial y siempre respondo en español a menos que me pidas lo contrario."
        )
        
        chat.with_model(model_config["provider"], model)
        
        user_msg = UserMessage(text=message_create.content)
        ai_response = await chat.send_message(user_msg)
        
        tokens_used = int((len(message_create.content) + len(ai_response)) / 4 * 1.3)
        
        assistant_message_data = {
            "message_id": generate_id("msg"),
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": "assistant",
            "content": ai_response,
            "model": model,
            "tokens_used": tokens_used,
            "timestamp": utc_now()
        }
        await db.messages.insert_one(assistant_message_data)
        assistant_message = Message(**assistant_message_data)
        
        new_credits = user_doc["credits"] - tokens_used
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {"credits": new_credits},
                "$inc": {"credits_used": tokens_used}
            }
        )
        
        # Log usage
        await db.agent_usage.insert_one({
            "usage_id": generate_id("usage"),
            "user_id": user_id,
            "agent_type": "chat",
            "credits_used": tokens_used,
            "conversation_id": conversation_id,
            "created_at": utc_now()
        })
        
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


@router.put("/messages/{message_id}", response_model=Message)
async def edit_message(request: Request, message_id: str, message_edit: MessageEdit):
    """Edit a user message"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    message = await db.messages.find_one({
        "message_id": message_id,
        "user_id": user_id,
        "role": "user"
    }, {"_id": 0})
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    original_content = message.get("original_content", message["content"])
    
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
    
    updated_message = await db.messages.find_one({"message_id": message_id}, {"_id": 0})
    return Message(**updated_message)


@router.post("/messages/{message_id}/regenerate", response_model=Message)
async def regenerate_message(request: Request, message_id: str):
    """Regenerate an assistant message"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    message = await db.messages.find_one({
        "message_id": message_id,
        "user_id": user_id,
        "role": "assistant"
    }, {"_id": 0})
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    conversation_id = message["conversation_id"]
    
    conv = await db.conversations.find_one({
        "conversation_id": conversation_id
    }, {"_id": 0})
    
    if user_doc["credits"] < 100:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    previous_messages = await db.messages.find({
        "conversation_id": conversation_id,
        "timestamp": {"$lt": message["timestamp"]}
    }, {"_id": 0}).sort("timestamp", 1).to_list(20)
    
    try:
        model = conv.get("model", DEFAULT_MODEL)
        model_config = AI_MODELS.get(model, AI_MODELS[DEFAULT_MODEL])
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=conversation_id,
            system_message="¡Hola! Soy Assistant Melus, tu asistente de inteligencia artificial."
        )
        
        chat.with_model(model_config["provider"], model)
        
        user_msg = previous_messages[-1] if previous_messages else None
        if not user_msg or user_msg["role"] != "user":
            raise HTTPException(status_code=400, detail="Cannot find user message to regenerate response")
        
        user_message = UserMessage(text=user_msg["content"])
        ai_response = await chat.send_message(user_message)
        
        tokens_used = int((len(user_msg["content"]) + len(ai_response)) / 4 * 1.3)
        
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
        
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {"credits": user_doc["credits"] - tokens_used},
                "$inc": {"credits_used": tokens_used}
            }
        )
        
        updated_message = await db.messages.find_one({"message_id": message_id}, {"_id": 0})
        return Message(**updated_message)
        
    except Exception as e:
        logger.error(f"Regenerate error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to regenerate: {str(e)}")


@router.post("/messages/{message_id}/rollback")
async def rollback_to_message(request: Request, message_id: str):
    """Rollback conversation to a specific message"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    message = await db.messages.find_one({
        "message_id": message_id,
        "user_id": user_id
    }, {"_id": 0})
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    conversation_id = message["conversation_id"]
    
    result = await db.messages.delete_many({
        "conversation_id": conversation_id,
        "timestamp": {"$gt": message["timestamp"]}
    })
    
    await db.conversations.update_one(
        {"conversation_id": conversation_id},
        {"$set": {"updated_at": utc_now()}}
    )
    
    return {
        "rolled_back": True,
        "messages_deleted": result.deleted_count,
        "message": f"Rolled back to message {message_id}"
    }


@router.post("/conversations/{conversation_id}/summarize")
async def summarize_conversation(request: Request, conversation_id: str):
    """Generate AI summary of a conversation"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    if user_doc["credits"] < 50:
        raise HTTPException(status_code=402, detail="Insufficient credits for summary (requires 50)")
    
    conv = await db.conversations.find_one({
        "conversation_id": conversation_id,
        "user_id": user_id
    }, {"_id": 0})
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await db.messages.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(50)
    
    if len(messages) == 0:
        raise HTTPException(status_code=400, detail="No messages to summarize")
    
    conversation_text = "\n".join([
        f"{'Usuario' if m['role'] == 'user' else 'Asistente'}: {m['content'][:500]}"
        for m in messages
    ])
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"summary_{conversation_id}",
        system_message="Eres un asistente especializado en crear resúmenes concisos."
    )
    chat.with_model("openai", "gpt-4o")
    
    summary_prompt = f"""Resume la siguiente conversación en 3-5 puntos clave:

Conversación:
{conversation_text}"""
    
    summary = await chat.send_message(UserMessage(text=summary_prompt))
    
    tokens_used = 50
    new_credits = user_doc["credits"] - tokens_used
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"credits": new_credits}, "$inc": {"credits_used": tokens_used}}
    )
    
    await db.conversations.update_one(
        {"conversation_id": conversation_id},
        {"$set": {"summary": summary, "summary_at": utc_now()}}
    )
    
    return {
        "summary": summary,
        "tokens_used": tokens_used,
        "credits_remaining": new_credits
    }


@router.post("/conversations/{conversation_id}/save")
async def save_conversation(request: Request, conversation_id: str):
    """Save/bookmark a conversation"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    conv = await db.conversations.find_one({
        "conversation_id": conversation_id,
        "user_id": user_id
    })
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    is_saved = conv.get("saved", False)
    
    await db.conversations.update_one(
        {"conversation_id": conversation_id},
        {"$set": {"saved": not is_saved, "updated_at": utc_now()}}
    )
    
    return {"saved": not is_saved}


@router.get("/conversations/{conversation_id}/code")
async def get_conversation_code(request: Request, conversation_id: str):
    """Extract code blocks from conversation messages"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    conv = await db.conversations.find_one({
        "conversation_id": conversation_id,
        "user_id": user_id
    }, {"_id": 0})
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await db.messages.find(
        {"conversation_id": conversation_id, "role": "assistant"},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(100)
    
    code_blocks = []
    for msg in messages:
        content = msg.get("content", "")
        
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for lang, code in matches:
            code_blocks.append({
                "message_id": msg["message_id"],
                "language": lang or "text",
                "code": code.strip(),
                "timestamp": msg["timestamp"]
            })
    
    return {"code_blocks": code_blocks, "total": len(code_blocks)}


@router.get("/conversations/{conversation_id}/preview")
async def get_conversation_preview(request: Request, conversation_id: str):
    """Get preview info for a conversation"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    conv = await db.conversations.find_one({
        "conversation_id": conversation_id,
        "user_id": user_id
    }, {"_id": 0})
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    message_count = await db.messages.count_documents({"conversation_id": conversation_id})
    
    last_message = await db.messages.find_one(
        {"conversation_id": conversation_id},
        {"_id": 0},
        sort=[("timestamp", -1)]
    )
    
    return {
        "conversation_id": conversation_id,
        "title": conv.get("title", "Sin título"),
        "model": conv.get("model", DEFAULT_MODEL),
        "message_count": message_count,
        "ultra_mode": conv.get("ultra_mode", False),
        "saved": conv.get("saved", False),
        "summary": conv.get("summary"),
        "last_activity": last_message["timestamp"] if last_message else conv.get("created_at"),
        "created_at": conv.get("created_at")
    }
