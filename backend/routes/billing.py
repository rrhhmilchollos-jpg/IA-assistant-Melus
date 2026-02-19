"""Billing and Credits routes for Assistant Melus"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import List
import logging
import os

from models import (
    CreditBalance, CreditPackage, CheckoutRequest,
    TransactionHistory, SubscriptionPlan, SubscriptionResponse
)
from config import CREDIT_PACKAGES, PROMO_CODES, CREDITS_PER_DOLLAR, SUBSCRIPTION_PLANS, CURRENCY
from utils import generate_id, utc_now, get_authenticated_user

from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest, CheckoutSessionResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/credits", tags=["billing"])

STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')


@router.get("", response_model=CreditBalance)
async def get_credits(request: Request):
    """Get user's credit balance"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    return CreditBalance(
        credits=user_doc["credits"],
        credits_used=user_doc["credits_used"],
        subscription_tier=user_doc.get("subscription_tier", "free")
    )


@router.get("/transactions", response_model=List[TransactionHistory])
async def get_transaction_history(request: Request):
    """Get user's transaction history"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    transactions = await db.payment_transactions.find(
        {"user_id": user_id, "processed": True},
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    result = []
    for txn in transactions:
        result.append(TransactionHistory(
            transaction_id=txn["transaction_id"],
            amount=txn["amount"],
            credits=txn["credits"],
            status=txn["status"],
            transaction_type=txn.get("transaction_type", "credit_purchase"),
            created_at=txn["created_at"]
        ))
    
    return result


@router.get("/packages", response_model=List[CreditPackage])
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


@router.get("/subscriptions", response_model=List[SubscriptionPlan])
async def get_subscription_plans():
    """Get available subscription plans"""
    plans = []
    for plan_id, data in SUBSCRIPTION_PLANS.items():
        plans.append(SubscriptionPlan(
            plan_id=plan_id,
            name=data["name"],
            price=data["price"],
            credits_per_month=data["credits_per_month"],
            features=data["features"],
            popular=data.get("popular", False),
            stripe_price_id=data.get("stripe_price_id")
        ))
    return plans


@router.post("/validate-promo")
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


@router.post("/checkout")
async def create_checkout_session(request: Request, checkout_req: CheckoutRequest):
    """Create Stripe checkout session for purchasing credits"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    if checkout_req.package_id:
        if checkout_req.package_id not in CREDIT_PACKAGES:
            raise HTTPException(status_code=400, detail="Invalid package")
        
        package_data = CREDIT_PACKAGES[checkout_req.package_id]
        amount = package_data["price"]
        credits = package_data["credits"]
        package_id = checkout_req.package_id
        
    elif checkout_req.custom_amount:
        amount = checkout_req.custom_amount
        if amount < 1:
            raise HTTPException(status_code=400, detail="Minimum amount is $1")
        
        credits = int(amount * CREDITS_PER_DOLLAR)
        package_id = "custom"
    else:
        raise HTTPException(status_code=400, detail="Must provide package_id or custom_amount")
    
    discount = 0
    promo_code = None
    if checkout_req.promo_code:
        promo_code = checkout_req.promo_code.upper()
        if promo_code in PROMO_CODES:
            promo = PROMO_CODES[promo_code]
            if promo["active"] and amount >= promo["min_amount"]:
                discount = amount * promo["discount"]
                amount = amount - discount
    
    host_url = checkout_req.origin_url
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(
        api_key=STRIPE_API_KEY,
        webhook_url=webhook_url
    )
    
    success_url = f"{host_url}/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{host_url}/pricing"
    
    checkout_request = CheckoutSessionRequest(
        amount=amount,
        currency=CURRENCY,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": user_id,
            "package_id": package_id,
            "credits": str(credits),
            "promo_code": promo_code or "",
            "discount": str(discount),
            "transaction_type": "credit_purchase"
        }
    )
    
    session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
    
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
        "transaction_type": "credit_purchase",
        "status": "pending",
        "payment_status": "unpaid",
        "processed": False,
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    await db.payment_transactions.insert_one(transaction)
    
    return {"checkout_url": session.url, "session_id": session.session_id}


@router.post("/subscribe")
async def create_subscription(request: Request, subscription_req: dict):
    """Create Stripe subscription checkout"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    plan_id = subscription_req.get("plan_id")
    origin_url = subscription_req.get("origin_url")
    
    if plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid subscription plan")
    
    plan = SUBSCRIPTION_PLANS[plan_id]
    
    host_url = origin_url
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(
        api_key=STRIPE_API_KEY,
        webhook_url=webhook_url
    )
    
    success_url = f"{host_url}/success?session_id={{CHECKOUT_SESSION_ID}}&type=subscription"
    cancel_url = f"{host_url}/pricing"
    
    checkout_request = CheckoutSessionRequest(
        amount=plan["price"],
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        mode="subscription",
        metadata={
            "user_id": user_id,
            "plan_id": plan_id,
            "credits_per_month": str(plan["credits_per_month"]),
            "transaction_type": "subscription"
        }
    )
    
    session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
    
    subscription_record = {
        "subscription_id": generate_id("sub"),
        "user_id": user_id,
        "stripe_session_id": session.session_id,
        "plan_id": plan_id,
        "status": "pending",
        "credits_per_month": plan["credits_per_month"],
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    await db.subscriptions.insert_one(subscription_record)
    
    return {"checkout_url": session.url, "session_id": session.session_id}


@router.get("/checkout/status/{session_id}")
async def get_checkout_status(request: Request, session_id: str):
    """Check payment status and add credits if paid"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    transaction = await db.payment_transactions.find_one(
        {"stripe_session_id": session_id, "user_id": user_id},
        {"_id": 0}
    )
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction["processed"]:
        return {
            "status": transaction["status"],
            "payment_status": transaction["payment_status"],
            "credits_added": transaction["credits"]
        }
    
    webhook_url = f"{request.base_url}api/webhook/stripe"
    stripe_checkout = StripeCheckout(
        api_key=STRIPE_API_KEY,
        webhook_url=webhook_url
    )
    
    try:
        checkout_status = await stripe_checkout.get_checkout_status(session_id)
        
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
        
        if checkout_status.payment_status == "paid" and not transaction["processed"]:
            await db.users.update_one(
                {"user_id": user_id},
                {"$inc": {"credits": transaction["credits"]}}
            )
            
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


@router.get("/usage")
async def get_credit_usage(request: Request):
    """Get detailed credit usage by agent type"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Get usage grouped by agent type
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$agent_type",
            "total_credits": {"$sum": "$credits_used"},
            "total_actions": {"$sum": 1}
        }},
        {"$sort": {"total_credits": -1}}
    ]
    
    usage = await db.agent_usage.aggregate(pipeline).to_list(20)
    
    return {
        "total_credits": user_doc["credits"],
        "total_used": user_doc["credits_used"],
        "usage_by_agent": [
            {
                "agent_type": u["_id"] or "unknown",
                "credits_used": u["total_credits"],
                "actions": u["total_actions"]
            }
            for u in usage
        ]
    }
