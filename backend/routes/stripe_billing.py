"""
MelusAI - Stripe Billing System
Handles subscriptions, payments, and credit management
"""
from fastapi import APIRouter, Request, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import stripe
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/billing", tags=["billing"])

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_API_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")

# Plans configuration
PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "credits": 50,
        "features": ["50 credits/month", "GPT-4o model", "Basic code generation", "3 projects", "Community support"]
    },
    "pro": {
        "name": "Pro",
        "price_id": "price_pro_monthly",
        "price": 2000,  # $20.00
        "credits": -1,  # Unlimited
        "features": ["Unlimited credits", "All AI models (GPT-5.2, Claude 4.5, etc)", "Advanced code generation", "Unlimited projects", "Priority support", "All agent modes (E1, E1.5, E2)", "GitHub integration", "Custom deployments"]
    },
    "team": {
        "name": "Team",
        "price_id": "price_team_monthly",
        "price": 5000,  # $50.00
        "credits": -1,  # Unlimited
        "features": ["Everything in Pro", "Up to 5 team members", "Shared projects", "Admin dashboard", "API access", "Custom integrations", "Dedicated support", "SLA guarantee"]
    }
}

# Credit packages for one-time purchase
CREDIT_PACKAGES = [
    {"id": "credits_100", "credits": 100, "price": 500, "name": "100 Credits"},
    {"id": "credits_500", "credits": 500, "price": 2000, "name": "500 Credits"},
    {"id": "credits_1000", "credits": 1000, "price": 3500, "name": "1,000 Credits"},
    {"id": "credits_5000", "credits": 5000, "price": 15000, "name": "5,000 Credits"},
]


class CreateCheckoutRequest(BaseModel):
    plan_id: Optional[str] = None
    plan: Optional[str] = None  # Alias for plan_id
    credit_package_id: Optional[str] = None
    credits: Optional[int] = None  # Direct credits amount
    price: Optional[float] = None  # Direct price
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class WebhookEvent(BaseModel):
    type: str
    data: dict


# Helper functions
async def get_user_from_token(request: Request) -> dict:
    """Get user from session token"""
    from utils import get_authenticated_user
    return await get_authenticated_user(request, request.app.state.db)


async def update_user_credits(db, user_id: str, credits: int, action: str = "add"):
    """Update user credits"""
    if action == "add":
        await db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"credits": credits}}
        )
    elif action == "set":
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"credits": credits}}
        )


async def log_transaction(db, user_id: str, transaction_type: str, amount: int, details: dict):
    """Log billing transaction"""
    await db.transactions.insert_one({
        "user_id": user_id,
        "type": transaction_type,
        "amount": amount,
        "details": details,
        "created_at": datetime.now(timezone.utc)
    })


# Endpoints
@router.get("/config")
async def get_billing_config():
    """Get Stripe publishable key and plans"""
    return {
        "publishable_key": STRIPE_PUBLISHABLE_KEY,
        "plans": PLANS,
        "credit_packages": CREDIT_PACKAGES
    }


@router.get("/plans")
async def get_plans():
    """Get available subscription plans"""
    return {"plans": PLANS}


@router.get("/credits")
async def get_user_credits(request: Request):
    """Get current user's credit balance"""
    user = await get_user_from_token(request)
    
    return {
        "credits": user.get("credits", 1000),
        "plan": user.get("plan", "free"),
        "unlimited": user.get("unlimited_credits", False)
    }


@router.post("/checkout/subscription")
async def create_subscription_checkout(checkout_request: CreateCheckoutRequest, request: Request):
    """Create Stripe checkout session for subscription"""
    user = await get_user_from_token(request)
    db = request.app.state.db
    
    plan_id = checkout_request.plan_id
    if plan_id not in PLANS or plan_id == "free":
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    plan = PLANS[plan_id]
    
    try:
        # Get or create Stripe customer
        customer_id = user.get("stripe_customer_id")
        
        if not customer_id:
            customer = stripe.Customer.create(
                email=user.get("email"),
                metadata={"user_id": user["user_id"]}
            )
            customer_id = customer.id
            
            await db.users.update_one(
                {"user_id": user["user_id"]},
                {"$set": {"stripe_customer_id": customer_id}}
            )
        
        # Create checkout session
        base_url = checkout_request.success_url or request.headers.get("origin", "")
        
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"MelusAI {plan['name']} Plan",
                        "description": ", ".join(plan["features"][:3])
                    },
                    "unit_amount": plan["price"],
                    "recurring": {"interval": "month"}
                },
                "quantity": 1
            }],
            mode="subscription",
            success_url=f"{base_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/pricing",
            metadata={
                "user_id": user["user_id"],
                "plan_id": plan_id
            }
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.id
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/checkout/credits")
async def create_credits_checkout(checkout_request: CreateCheckoutRequest, request: Request):
    """Create Stripe checkout session for credit purchase"""
    user = await get_user_from_token(request)
    db = request.app.state.db
    
    package_id = checkout_request.credit_package_id
    package = next((p for p in CREDIT_PACKAGES if p["id"] == package_id), None)
    
    if not package:
        raise HTTPException(status_code=400, detail="Invalid credit package")
    
    try:
        customer_id = user.get("stripe_customer_id")
        
        if not customer_id:
            customer = stripe.Customer.create(
                email=user.get("email"),
                metadata={"user_id": user["user_id"]}
            )
            customer_id = customer.id
            
            await db.users.update_one(
                {"user_id": user["user_id"]},
                {"$set": {"stripe_customer_id": customer_id}}
            )
        
        base_url = checkout_request.success_url or request.headers.get("origin", "")
        
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": package["name"],
                        "description": f"{package['credits']:,} credits for MelusAI"
                    },
                    "unit_amount": package["price"]
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=f"{base_url}/success?session_id={{CHECKOUT_SESSION_ID}}&credits={package['credits']}",
            cancel_url=f"{base_url}/pricing",
            metadata={
                "user_id": user["user_id"],
                "package_id": package_id,
                "credits": package["credits"]
            }
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.id
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    
    db = request.app.state.db
    
    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        else:
            event = stripe.Event.construct_from(
                __import__("json").loads(payload), stripe.api_key
            )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    event_type = event["type"]
    data = event["data"]["object"]
    
    # Handle different event types
    if event_type == "checkout.session.completed":
        user_id = data.get("metadata", {}).get("user_id")
        
        if user_id:
            # Check if it's a credit purchase
            credits = data.get("metadata", {}).get("credits")
            if credits:
                await update_user_credits(db, user_id, int(credits), "add")
                await log_transaction(db, user_id, "credit_purchase", int(credits), {
                    "session_id": data["id"],
                    "amount_paid": data.get("amount_total", 0)
                })
            
            # Check if it's a subscription
            plan_id = data.get("metadata", {}).get("plan_id")
            if plan_id and plan_id in PLANS:
                plan = PLANS[plan_id]
                
                await db.users.update_one(
                    {"user_id": user_id},
                    {"$set": {
                        "plan": plan_id,
                        "subscription_id": data.get("subscription"),
                        "credits": plan["credits"] if plan["credits"] > 0 else 999999,
                        "unlimited_credits": plan["credits"] == -1
                    }}
                )
                
                await log_transaction(db, user_id, "subscription", plan["price"], {
                    "plan": plan_id,
                    "session_id": data["id"]
                })
    
    elif event_type == "customer.subscription.deleted":
        # Subscription cancelled - downgrade to free
        subscription = data
        customer_id = subscription.get("customer")
        
        user = await db.users.find_one({"stripe_customer_id": customer_id})
        if user:
            await db.users.update_one(
                {"user_id": user["user_id"]},
                {"$set": {
                    "plan": "free",
                    "subscription_id": None,
                    "unlimited_credits": False,
                    "credits": 1000
                }}
            )
    
    return {"status": "success"}


@router.get("/subscription")
async def get_subscription_status(request: Request):
    """Get user's subscription status"""
    user = await get_user_from_token(request)
    
    subscription_id = user.get("subscription_id")
    
    if subscription_id:
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "active": subscription.status == "active",
                "plan": user.get("plan", "free"),
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
        except:
            pass
    
    return {
        "active": False,
        "plan": user.get("plan", "free"),
        "current_period_end": None,
        "cancel_at_period_end": False
    }


@router.post("/subscription/cancel")
async def cancel_subscription(request: Request):
    """Cancel user's subscription"""
    user = await get_user_from_token(request)
    
    subscription_id = user.get("subscription_id")
    if not subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")
    
    try:
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
        
        return {
            "status": "cancelled",
            "cancel_at": subscription.current_period_end
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions")
async def get_transactions(request: Request, limit: int = 20):
    """Get user's transaction history"""
    user = await get_user_from_token(request)
    db = request.app.state.db
    
    transactions = await db.transactions.find(
        {"user_id": user["user_id"]}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Clean up MongoDB _id
    for t in transactions:
        t.pop("_id", None)
        if t.get("created_at"):
            t["created_at"] = t["created_at"].isoformat()
    
    return {"transactions": transactions}


@router.post("/use-credits")
async def use_credits(request: Request, amount: int = 1):
    """Use credits for an operation"""
    user = await get_user_from_token(request)
    db = request.app.state.db
    
    if user.get("unlimited_credits"):
        return {"success": True, "remaining": -1}
    
    current_credits = user.get("credits", 0)
    
    if current_credits < amount:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$inc": {"credits": -amount}}
    )
    
    return {
        "success": True,
        "used": amount,
        "remaining": current_credits - amount
    }
