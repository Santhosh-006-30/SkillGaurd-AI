from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User, UserRole, ItemType
from app.core.security import get_current_user, require_roles
from app.services.inventory_service import InventoryService
from app.schemas.infrastructure import (
    InventoryItemBase,
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    InventoryComplianceResponse
)

router = APIRouter(prefix="", tags=["Inventory & Infrastructure"])

@router.get("/inventory", response_model=dict)
def list_inventory(
    centre_id: Optional[int] = Query(None),
    item_type: Optional[ItemType] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = InventoryService.get_items(
        db, centre_id=centre_id, item_type=item_type, skip=skip, limit=limit
    )
    return {
        "success": True,
        "data": [InventoryItemResponse.model_validate(it).model_dump() for it in items]
    }

@router.get("/centres/{centre_id}/inventory", response_model=dict)
def get_centre_inventory(
    centre_id: int,
    item_type: Optional[ItemType] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = InventoryService.get_items(
        db, centre_id=centre_id, item_type=item_type, skip=skip, limit=limit
    )
    return {
        "success": True,
        "data": [InventoryItemResponse.model_validate(it).model_dump() for it in items]
    }

@router.get("/centres/{centre_id}/inventory/compliance", response_model=dict)
def get_centre_inventory_compliance(
    centre_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    compliance = InventoryService.get_inventory_compliance(db, centre_id)
    if not compliance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training centre with ID {centre_id} not found"
        )
    return {
        "success": True,
        "data": compliance
    }

@router.post("/centres/{centre_id}/inventory", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_centre_inventory_item(
    centre_id: int,
    item_base: InventoryItemBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CENTRE_OPERATOR))
):
    obj_in = InventoryItemCreate(centre_id=centre_id, **item_base.model_dump())
    item = InventoryService.create_item(db, obj_in)
    return {
        "success": True,
        "data": InventoryItemResponse.model_validate(item).model_dump()
    }

@router.put("/inventory/{item_id}", response_model=dict)
def update_inventory_item(
    item_id: int,
    item_in: InventoryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CENTRE_OPERATOR))
):
    item = InventoryService.update_item(db, item_id, item_in)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with ID {item_id} not found"
        )
    return {
        "success": True,
        "data": InventoryItemResponse.model_validate(item).model_dump()
    }

@router.delete("/inventory/{item_id}", response_model=dict)
def delete_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    deleted = InventoryService.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with ID {item_id} not found"
        )
    return {
        "success": True,
        "data": {"message": f"Inventory item {item_id} deleted successfully"}
    }
