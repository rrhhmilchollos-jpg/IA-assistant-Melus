"""
Assistant Melus API - Main Server
Full-stack AI application generator with multi-agent architecture
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Assistant Melus API",
    description="AI-powered application generator with multi-agent architecture",
    version="2.0.0"
)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Store db in app state for routes to access
app.state.db = db

# Import routers
from routes.auth import router as auth_router
from routes.billing import router as billing_router
from routes.admin import router as admin_router
from routes.agents import router as agents_router
from routes.agents_v2 import router as agents_v2_router
from routes.projects import router as projects_router
from routes.chat import router as chat_router
from routes.voice import router as voice_router
from routes.deploy import router as deploy_router
from routes.github import router as github_router
from routes.workspace import router as workspace_router

# Include all routers with /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(billing_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(agents_router, prefix="/api")
app.include_router(agents_v2_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(voice_router, prefix="/api")
app.include_router(deploy_router, prefix="/api")
app.include_router(github_router, prefix="/api")
app.include_router(workspace_router, prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/api/")
async def root():
    return {
        "message": "Assistant Melus API",
        "version": "2.0.0",
        "features": [
            "Multi-agent app generation",
            "Credit-based system",
            "Stripe payments",
            "Admin panel"
        ]
    }


# Health check
@app.get("/api/health")
async def health_check():
    try:
        await db.command("ping")
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "operational",
        "database": db_status
    }


# Stripe webhook handler (needs to be at app level for body parsing)
@app.post("/api/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    from utils import utc_now
    
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
        webhook_url = f"{request.base_url}api/webhook/stripe"
        stripe_checkout = StripeCheckout(
            api_key=STRIPE_API_KEY,
            webhook_url=webhook_url
        )
        
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.event_type == "checkout.session.completed":
            session_id = webhook_response.session_id
            
            transaction = await db.payment_transactions.find_one(
                {"stripe_session_id": session_id},
                {"_id": 0}
            )
            
            if transaction and not transaction["processed"]:
                await db.users.update_one(
                    {"user_id": transaction["user_id"]},
                    {"$inc": {"credits": transaction["credits"]}}
                )
                
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
        
        # Handle subscription events
        elif webhook_response.event_type == "customer.subscription.created":
            # Update user subscription
            pass
        
        elif webhook_response.event_type == "customer.subscription.deleted":
            # Handle subscription cancellation
            pass
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse(status_code=400, content={"error": str(e)})


# File attachments endpoint
@app.post("/api/attachments/upload")
async def upload_attachment(request: Request):
    """Upload a file attachment"""
    import base64
    from pathlib import Path
    from utils import generate_id, utc_now, get_authenticated_user
    
    UPLOAD_DIR = Path("/app/uploads")
    UPLOAD_DIR.mkdir(exist_ok=True)
    
    ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf', '.txt', '.md', '.py', '.js', '.json', '.csv'}
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    try:
        body = await request.json()
        file_data = body.get("file_data")
        file_name = body.get("file_name", "file")
        file_type = body.get("file_type", "application/octet-stream")
        conversation_id = body.get("conversation_id")
        
        if not file_data:
            return JSONResponse(status_code=400, content={"detail": "No file data provided"})
        
        try:
            file_bytes = base64.b64decode(file_data.split(",")[-1] if "," in file_data else file_data)
        except Exception:
            return JSONResponse(status_code=400, content={"detail": "Invalid file data"})
        
        if len(file_bytes) > MAX_FILE_SIZE:
            return JSONResponse(status_code=400, content={"detail": "File too large (max 10MB)"})
        
        ext = Path(file_name).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return JSONResponse(status_code=400, content={"detail": f"File type not allowed: {ext}"})
        
        attachment_id = generate_id("att")
        safe_filename = f"{attachment_id}{ext}"
        file_path = UPLOAD_DIR / safe_filename
        
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        
        attachment_data = {
            "attachment_id": attachment_id,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "original_name": file_name,
            "stored_name": safe_filename,
            "file_type": file_type,
            "file_size": len(file_bytes),
            "file_path": str(file_path),
            "created_at": utc_now()
        }
        await db.attachments.insert_one(attachment_data)
        
        return {
            "attachment_id": attachment_id,
            "file_name": file_name,
            "file_type": file_type,
            "file_size": len(file_bytes),
            "url": f"/api/attachments/{attachment_id}"
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return JSONResponse(status_code=500, content={"detail": "Failed to upload file"})


@app.get("/api/attachments/{attachment_id}")
async def get_attachment(attachment_id: str):
    """Get an attachment file"""
    from fastapi.responses import FileResponse
    from pathlib import Path
    
    attachment = await db.attachments.find_one({"attachment_id": attachment_id}, {"_id": 0})
    
    if not attachment:
        return JSONResponse(status_code=404, content={"detail": "Attachment not found"})
    
    file_path = Path(attachment["file_path"])
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"detail": "File not found"})
    
    return FileResponse(
        path=file_path,
        filename=attachment["original_name"],
        media_type=attachment["file_type"]
    )


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
