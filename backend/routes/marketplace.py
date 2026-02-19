"""Marketplace routes for Melus AI - Template sharing and discovery"""
from fastapi import APIRouter, HTTPException, Request
from typing import Optional, List
import logging

from utils import generate_id, utc_now, get_authenticated_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.get("/templates")
async def get_marketplace_templates(
    request: Request,
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "popular",
    page: int = 1,
    limit: int = 20
):
    """Get public templates from marketplace"""
    db = request.app.state.db
    
    # Build query
    query = {"is_public": True, "status": "approved"}
    
    if category:
        query["category"] = category
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"tags": {"$in": [search.lower()]}}
        ]
    
    # Sort options
    sort_options = {
        "popular": [("downloads", -1), ("likes", -1)],
        "newest": [("created_at", -1)],
        "name": [("name", 1)]
    }
    
    sort_by = sort_options.get(sort, sort_options["popular"])
    
    # Get templates
    skip = (page - 1) * limit
    templates = await db.marketplace_templates.find(
        query,
        {"_id": 0}
    ).sort(sort_by).skip(skip).limit(limit).to_list(limit)
    
    # Get total count
    total = await db.marketplace_templates.count_documents(query)
    
    return {
        "templates": templates,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }


@router.get("/templates/{template_id}")
async def get_template_details(request: Request, template_id: str):
    """Get detailed template information"""
    db = request.app.state.db
    
    template = await db.marketplace_templates.find_one(
        {"template_id": template_id},
        {"_id": 0}
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Increment view count
    await db.marketplace_templates.update_one(
        {"template_id": template_id},
        {"$inc": {"views": 1}}
    )
    
    # Get author info
    author = await db.users.find_one(
        {"user_id": template["author_id"]},
        {"_id": 0, "user_id": 1, "name": 1, "email": 1}
    )
    
    template["author"] = author
    
    return template


@router.post("/templates")
async def publish_template(request: Request):
    """Publish a workspace as a marketplace template"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    workspace_id = body.get("workspace_id")
    name = body.get("name")
    description = body.get("description", "")
    category = body.get("category", "other")
    tags = body.get("tags", [])
    is_free = body.get("is_free", True)
    price = body.get("price", 0)
    
    if not workspace_id or not name:
        raise HTTPException(status_code=400, detail="workspace_id and name required")
    
    # Get workspace
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id},
        {"_id": 0}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Create template
    template_id = generate_id("tpl")
    
    template = {
        "template_id": template_id,
        "author_id": user_id,
        "workspace_id": workspace_id,
        "name": name,
        "description": description,
        "category": category,
        "tags": [t.lower() for t in tags],
        "files": workspace.get("files", {}),
        "preview_image": body.get("preview_image"),
        "is_public": True,
        "is_free": is_free,
        "price": price if not is_free else 0,
        "downloads": 0,
        "likes": 0,
        "views": 0,
        "status": "approved",  # Auto-approve for now
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    
    await db.marketplace_templates.insert_one(template)
    
    # Update workspace
    await db.workspaces.update_one(
        {"workspace_id": workspace_id},
        {"$set": {"marketplace_template_id": template_id}}
    )
    
    return {
        "template_id": template_id,
        "status": "approved",
        "message": "Template publicado exitosamente"
    }


@router.post("/templates/{template_id}/use")
async def use_template(request: Request, template_id: str):
    """Create a new workspace from a marketplace template"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Get template
    template = await db.marketplace_templates.find_one(
        {"template_id": template_id, "status": "approved"},
        {"_id": 0}
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check if paid template
    if not template.get("is_free", True):
        # Check if user has purchased
        purchase = await db.template_purchases.find_one({
            "user_id": user_id,
            "template_id": template_id
        })
        if not purchase:
            raise HTTPException(
                status_code=402,
                detail=f"Este template cuesta {template['price']} créditos"
            )
    
    # Create new workspace from template
    workspace_id = generate_id("ws")
    
    workspace = {
        "workspace_id": workspace_id,
        "user_id": user_id,
        "name": f"{template['name']} (copia)",
        "description": template.get("description", ""),
        "template_id": template_id,
        "files": template.get("files", {}),
        "versions": [{
            "version": 1,
            "files": template.get("files", {}),
            "created_at": utc_now(),
            "message": f"Creado desde template: {template['name']}"
        }],
        "current_version": 1,
        "status": "completed",
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    
    await db.workspaces.insert_one(workspace)
    
    # Increment download count
    await db.marketplace_templates.update_one(
        {"template_id": template_id},
        {"$inc": {"downloads": 1}}
    )
    
    return {
        "workspace_id": workspace_id,
        "template_name": template["name"],
        "files_count": len(template.get("files", {}))
    }


@router.post("/templates/{template_id}/like")
async def like_template(request: Request, template_id: str):
    """Like a marketplace template"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Check if already liked
    existing = await db.template_likes.find_one({
        "user_id": user_id,
        "template_id": template_id
    })
    
    if existing:
        # Unlike
        await db.template_likes.delete_one({"_id": existing["_id"]})
        await db.marketplace_templates.update_one(
            {"template_id": template_id},
            {"$inc": {"likes": -1}}
        )
        return {"liked": False}
    else:
        # Like
        await db.template_likes.insert_one({
            "user_id": user_id,
            "template_id": template_id,
            "created_at": utc_now()
        })
        await db.marketplace_templates.update_one(
            {"template_id": template_id},
            {"$inc": {"likes": 1}}
        )
        return {"liked": True}


@router.get("/categories")
async def get_categories(request: Request):
    """Get all marketplace categories"""
    return {
        "categories": [
            {"id": "landing", "name": "Landing Pages", "icon": "layout"},
            {"id": "ecommerce", "name": "E-commerce", "icon": "shopping-cart"},
            {"id": "dashboard", "name": "Dashboards", "icon": "bar-chart"},
            {"id": "portfolio", "name": "Portfolios", "icon": "user"},
            {"id": "blog", "name": "Blogs", "icon": "file-text"},
            {"id": "saas", "name": "SaaS Apps", "icon": "cloud"},
            {"id": "mobile", "name": "Mobile Apps", "icon": "smartphone"},
            {"id": "game", "name": "Games", "icon": "gamepad"},
            {"id": "tool", "name": "Tools & Utilities", "icon": "tool"},
            {"id": "other", "name": "Other", "icon": "box"}
        ]
    }


@router.get("/my-templates")
async def get_my_templates(request: Request):
    """Get templates published by current user"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    templates = await db.marketplace_templates.find(
        {"author_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return {"templates": templates}


@router.delete("/templates/{template_id}")
async def delete_template(request: Request, template_id: str):
    """Delete a marketplace template (author only)"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Check ownership
    template = await db.marketplace_templates.find_one({
        "template_id": template_id,
        "author_id": user_id
    })
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found or unauthorized")
    
    await db.marketplace_templates.delete_one({"template_id": template_id})
    
    return {"deleted": True, "template_id": template_id}


@router.post("/templates/{template_id}/purchase")
async def purchase_template(request: Request, template_id: str):
    """Purchase a paid template using credits"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Check if unlimited credits
    is_unlimited = user_doc.get("unlimited_credits", False) or user_doc.get("is_owner", False)
    
    # Get template
    template = await db.marketplace_templates.find_one(
        {"template_id": template_id, "status": "approved"},
        {"_id": 0}
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check if template is free
    if template.get("is_free", True):
        return {
            "success": True,
            "message": "Este template es gratuito",
            "already_purchased": True
        }
    
    # Check if already purchased
    existing_purchase = await db.template_purchases.find_one({
        "user_id": user_id,
        "template_id": template_id
    })
    
    if existing_purchase:
        return {
            "success": True,
            "message": "Ya tienes este template",
            "already_purchased": True
        }
    
    template_price = template.get("price", 0)
    
    # Check credits
    if not is_unlimited and user_doc["credits"] < template_price:
        raise HTTPException(
            status_code=402,
            detail=f"Necesitas {template_price} créditos. Tienes {user_doc['credits']:.2f}"
        )
    
    # Deduct credits if not unlimited
    if not is_unlimited:
        new_credits = user_doc["credits"] - template_price
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {"credits": new_credits},
                "$inc": {"credits_used": template_price}
            }
        )
    else:
        new_credits = user_doc["credits"]
    
    # Record purchase
    purchase = {
        "purchase_id": generate_id("pur"),
        "user_id": user_id,
        "template_id": template_id,
        "template_name": template.get("name"),
        "price": template_price,
        "author_id": template.get("author_id"),
        "purchased_at": utc_now()
    }
    
    await db.template_purchases.insert_one(purchase)
    
    # Pay author (80% of price goes to author)
    author_earnings = template_price * 0.80
    await db.users.update_one(
        {"user_id": template.get("author_id")},
        {
            "$inc": {
                "credits": author_earnings,
                "marketplace_earnings": author_earnings
            }
        }
    )
    
    # Update template stats
    await db.marketplace_templates.update_one(
        {"template_id": template_id},
        {
            "$inc": {
                "purchases": 1,
                "total_earnings": template_price
            }
        }
    )
    
    return {
        "success": True,
        "message": f"Template comprado por {template_price} créditos",
        "credits_remaining": new_credits,
        "purchase_id": purchase["purchase_id"]
    }


@router.get("/my-purchases")
async def get_my_purchases(request: Request):
    """Get templates purchased by current user"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    purchases = await db.template_purchases.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("purchased_at", -1).to_list(100)
    
    # Get template details for each purchase
    for purchase in purchases:
        template = await db.marketplace_templates.find_one(
            {"template_id": purchase["template_id"]},
            {"_id": 0, "name": 1, "description": 1, "category": 1, "preview_image": 1}
        )
        purchase["template"] = template
    
    return {"purchases": purchases}


@router.get("/my-earnings")
async def get_my_earnings(request: Request):
    """Get marketplace earnings for current user"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Get total earnings
    total_earnings = user_doc.get("marketplace_earnings", 0)
    
    # Get sales history
    sales = await db.template_purchases.find(
        {"author_id": user_id},
        {"_id": 0}
    ).sort("purchased_at", -1).limit(50).to_list(50)
    
    # Get templates stats
    templates = await db.marketplace_templates.find(
        {"author_id": user_id},
        {"_id": 0, "template_id": 1, "name": 1, "price": 1, "purchases": 1, "total_earnings": 1}
    ).to_list(100)
    
    return {
        "total_earnings": total_earnings,
        "sales": sales,
        "templates": templates,
        "pending_payout": total_earnings  # For now, all earnings are available
    }

