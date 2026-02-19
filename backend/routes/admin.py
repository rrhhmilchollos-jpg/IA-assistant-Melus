"""Admin Panel routes for Assistant Melus"""
from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import os

from models import User
from config import ADMIN_EMAILS
from utils import generate_id, utc_now, get_authenticated_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


async def require_admin(request: Request):
    """Check if user is admin"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    
    if not user_doc.get("is_admin", False) and user_doc["email"] not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user_doc


@router.get("/dashboard")
async def get_admin_dashboard(request: Request):
    """Get admin dashboard data"""
    db = request.app.state.db
    await require_admin(request)
    
    # Get user stats
    total_users = await db.users.count_documents({})
    active_users_24h = await db.user_sessions.count_documents({
        "created_at": {"$gte": utc_now() - timedelta(hours=24)}
    })
    
    # Get revenue stats
    pipeline = [
        {"$match": {"processed": True, "status": "completed"}},
        {"$group": {
            "_id": None,
            "total_revenue": {"$sum": "$amount"},
            "total_transactions": {"$sum": 1}
        }}
    ]
    revenue_data = await db.payment_transactions.aggregate(pipeline).to_list(1)
    revenue = revenue_data[0] if revenue_data else {"total_revenue": 0, "total_transactions": 0}
    
    # Get today's revenue
    today_start = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
    pipeline_today = [
        {"$match": {
            "processed": True, 
            "status": "completed",
            "created_at": {"$gte": today_start}
        }},
        {"$group": {
            "_id": None,
            "today_revenue": {"$sum": "$amount"},
            "today_transactions": {"$sum": 1}
        }}
    ]
    today_data = await db.payment_transactions.aggregate(pipeline_today).to_list(1)
    today = today_data[0] if today_data else {"today_revenue": 0, "today_transactions": 0}
    
    # Get credits usage stats
    pipeline_credits = [
        {"$group": {
            "_id": None,
            "total_credits_used": {"$sum": "$credits_used"},
            "total_credits_available": {"$sum": "$credits"}
        }}
    ]
    credits_data = await db.users.aggregate(pipeline_credits).to_list(1)
    credits = credits_data[0] if credits_data else {"total_credits_used": 0, "total_credits_available": 0}
    
    # Get agent usage stats
    pipeline_agents = [
        {"$group": {
            "_id": "$agent_type",
            "total_credits": {"$sum": "$credits_used"},
            "total_actions": {"$sum": 1}
        }},
        {"$sort": {"total_credits": -1}},
        {"$limit": 10}
    ]
    agent_usage = await db.agent_usage.aggregate(pipeline_agents).to_list(10)
    
    # Get recent projects
    recent_projects = await db.projects.find(
        {},
        {"_id": 0}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    # Get subscription stats
    subscription_pipeline = [
        {"$match": {"status": "active"}},
        {"$group": {
            "_id": "$plan_id",
            "count": {"$sum": 1}
        }}
    ]
    subscriptions = await db.subscriptions.aggregate(subscription_pipeline).to_list(10)
    
    return {
        "users": {
            "total": total_users,
            "active_24h": active_users_24h
        },
        "revenue": {
            "total": revenue.get("total_revenue", 0),
            "total_transactions": revenue.get("total_transactions", 0),
            "today": today.get("today_revenue", 0),
            "today_transactions": today.get("today_transactions", 0)
        },
        "credits": {
            "total_used": credits.get("total_credits_used", 0),
            "total_available": credits.get("total_credits_available", 0)
        },
        "agent_usage": [
            {
                "agent_type": a["_id"] or "unknown",
                "credits_used": a["total_credits"],
                "actions": a["total_actions"]
            }
            for a in agent_usage
        ],
        "subscriptions": {
            s["_id"]: s["count"]
            for s in subscriptions
        },
        "recent_projects": recent_projects
    }


@router.get("/users")
async def get_all_users(request: Request, limit: int = 50, skip: int = 0):
    """Get all users"""
    db = request.app.state.db
    await require_admin(request)
    
    users = await db.users.find(
        {},
        {"_id": 0, "password_hash": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.users.count_documents({})
    
    return {
        "users": users,
        "total": total,
        "limit": limit,
        "skip": skip
    }


@router.put("/users/{user_id}")
async def update_user(request: Request, user_id: str, update_data: dict):
    """Update user data"""
    db = request.app.state.db
    await require_admin(request)
    
    # Fields that can be updated
    allowed_fields = ["credits", "is_admin", "subscription_tier", "name"]
    update = {}
    
    for field in allowed_fields:
        if field in update_data:
            update[field] = update_data[field]
    
    if not update:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    update["updated_at"] = utc_now()
    
    result = await db.users.update_one(
        {"user_id": user_id},
        {"$set": update}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "password_hash": 0})
    
    return {"message": "User updated", "user": updated_user}


@router.delete("/users/{user_id}")
async def delete_user(request: Request, user_id: str):
    """Delete a user"""
    db = request.app.state.db
    admin = await require_admin(request)
    
    # Prevent self-deletion
    if admin["user_id"] == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    result = await db.users.delete_one({"user_id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Also delete user's sessions
    await db.user_sessions.delete_many({"user_id": user_id})
    
    return {"message": "User deleted"}


@router.get("/transactions")
async def get_all_transactions(request: Request, limit: int = 100, skip: int = 0):
    """Get all transactions"""
    db = request.app.state.db
    await require_admin(request)
    
    transactions = await db.payment_transactions.find(
        {},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Enrich with user emails
    for txn in transactions:
        user = await db.users.find_one({"user_id": txn["user_id"]}, {"email": 1, "_id": 0})
        txn["user_email"] = user.get("email") if user else "unknown"
    
    total = await db.payment_transactions.count_documents({})
    
    return {
        "transactions": transactions,
        "total": total,
        "limit": limit,
        "skip": skip
    }


@router.get("/projects")
async def get_all_projects(request: Request, limit: int = 50, skip: int = 0):
    """Get all projects"""
    db = request.app.state.db
    await require_admin(request)
    
    projects = await db.projects.find(
        {},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.projects.count_documents({})
    
    return {
        "projects": projects,
        "total": total,
        "limit": limit,
        "skip": skip
    }


@router.get("/system-health")
async def get_system_health(request: Request):
    """Get system health status"""
    db = request.app.state.db
    await require_admin(request)
    
    # Check MongoDB connection
    try:
        await db.command("ping")
        mongo_status = "healthy"
    except Exception as e:
        mongo_status = f"error: {str(e)}"
    
    # Get active sessions count
    active_sessions = await db.user_sessions.count_documents({
        "expires_at": {"$gt": utc_now()}
    })
    
    # Get pending projects
    pending_projects = await db.projects.count_documents({"status": "in_progress"})
    
    return {
        "status": "operational",
        "services": {
            "mongodb": mongo_status,
            "api": "healthy"
        },
        "metrics": {
            "active_sessions": active_sessions,
            "pending_projects": pending_projects
        },
        "timestamp": utc_now().isoformat()
    }


@router.post("/settings/credit-costs")
async def update_credit_costs(request: Request, cost_data: dict):
    """Update credit costs for agents"""
    db = request.app.state.db
    await require_admin(request)
    
    # Store in settings collection
    await db.settings.update_one(
        {"setting_type": "credit_costs"},
        {
            "$set": {
                "costs": cost_data,
                "updated_at": utc_now()
            }
        },
        upsert=True
    )
    
    return {"message": "Credit costs updated", "costs": cost_data}


@router.get("/settings/credit-costs")
async def get_credit_costs(request: Request):
    """Get current credit costs"""
    db = request.app.state.db
    await require_admin(request)
    
    settings = await db.settings.find_one(
        {"setting_type": "credit_costs"},
        {"_id": 0}
    )
    
    if not settings:
        # Default costs
        return {
            "costs": {
                "design_agent": 100,
                "frontend_agent": 150,
                "backend_agent": 150,
                "database_agent": 100,
                "deploy_agent": 200,
                "chat": 50
            }
        }
    
    return settings


@router.get("/revenue/chart")
async def get_revenue_chart(request: Request, days: int = 30):
    """Get revenue chart data"""
    db = request.app.state.db
    await require_admin(request)
    
    start_date = utc_now() - timedelta(days=days)
    
    pipeline = [
        {"$match": {
            "processed": True,
            "status": "completed",
            "created_at": {"$gte": start_date}
        }},
        {"$group": {
            "_id": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": "$created_at"
                }
            },
            "revenue": {"$sum": "$amount"},
            "transactions": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    chart_data = await db.payment_transactions.aggregate(pipeline).to_list(days)
    
    return {
        "data": [
            {
                "date": d["_id"],
                "revenue": d["revenue"],
                "transactions": d["transactions"]
            }
            for d in chart_data
        ],
        "period_days": days
    }


# ============================================================================
# NEW METRICS ENDPOINTS
# ============================================================================

@router.get("/metrics/projects")
async def get_projects_metrics(request: Request):
    """Get project generation metrics"""
    db = request.app.state.db
    await require_admin(request)
    
    now = utc_now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    
    # Total projects
    total = await db.workspaces.count_documents({})
    
    # Today's projects
    today = await db.workspaces.count_documents({
        "created_at": {"$gte": today_start}
    })
    
    # This week's projects
    this_week = await db.workspaces.count_documents({
        "created_at": {"$gte": week_start}
    })
    
    # Projects by type
    pipeline = [
        {"$group": {
            "_id": "$project_type",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    by_type = await db.workspaces.aggregate(pipeline).to_list(10)
    
    return {
        "total": total,
        "today": today,
        "this_week": this_week,
        "by_type": [{"type": t["_id"] or "custom", "count": t["count"]} for t in by_type]
    }


@router.get("/metrics/sandbox")
async def get_sandbox_metrics(request: Request):
    """Get sandbox execution metrics"""
    db = request.app.state.db
    await require_admin(request)
    
    # Total executions
    total = await db.sandbox_executions.count_documents({})
    
    # Successful executions
    successful = await db.sandbox_executions.count_documents({"exit_code": 0})
    
    # Failed executions
    failed = total - successful
    
    # By method
    pipeline = [
        {"$group": {
            "_id": "$type",
            "count": {"$sum": 1}
        }}
    ]
    by_method_list = await db.sandbox_executions.aggregate(pipeline).to_list(10)
    by_method = {m["_id"]: m["count"] for m in by_method_list}
    
    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "by_method": by_method
    }


@router.get("/metrics/credits")
async def get_credits_metrics(request: Request):
    """Get credits consumption metrics"""
    db = request.app.state.db
    await require_admin(request)
    
    now = utc_now()
    week_ago = now - timedelta(days=7)
    
    # Daily credits consumption
    pipeline = [
        {"$match": {
            "created_at": {"$gte": week_ago}
        }},
        {"$group": {
            "_id": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": "$created_at"
                }
            },
            "credits": {"$sum": "$credits_used"}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    daily_raw = await db.workspaces.aggregate(pipeline).to_list(7)
    
    # Build daily data with day names
    days_of_week = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
    daily = []
    
    for d in daily_raw:
        date_obj = datetime.strptime(d["_id"], "%Y-%m-%d")
        daily.append({
            "date": d["_id"],
            "day": days_of_week[date_obj.weekday()],
            "credits": d["credits"] or 0
        })
    
    # Total consumed
    total_consumed = sum(d["credits"] for d in daily)
    daily_average = total_consumed / max(len(daily), 1)
    
    return {
        "total_consumed": total_consumed,
        "daily_average": daily_average,
        "daily": daily
    }


@router.get("/projects")
async def get_all_projects_v2(request: Request, limit: int = 50, skip: int = 0):
    """Get all workspaces/projects with user info"""
    db = request.app.state.db
    await require_admin(request)
    
    projects = await db.workspaces.find(
        {},
        {"_id": 0, "files": 0, "versions": 0}  # Exclude large fields
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Enrich with user emails and file counts
    for proj in projects:
        user = await db.users.find_one({"user_id": proj.get("user_id")}, {"email": 1, "_id": 0})
        proj["user_email"] = user.get("email") if user else "unknown"
        
        # Get file count from a separate query if needed
        workspace_full = await db.workspaces.find_one(
            {"workspace_id": proj["workspace_id"]},
            {"files": 1}
        )
        proj["file_count"] = len(workspace_full.get("files", {})) if workspace_full else 0
    
    total = await db.workspaces.count_documents({})
    
    return {
        "projects": projects,
        "total": total,
        "limit": limit,
        "skip": skip
    }

