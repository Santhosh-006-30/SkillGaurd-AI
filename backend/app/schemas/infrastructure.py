from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.database.models import ItemType

class InventoryItemBase(BaseModel):
    item_type: ItemType
    item_name: str = Field(..., min_length=2, max_length=200)
    sanctioned_quantity: int = Field(..., ge=0)
    minimum_required: int = Field(..., ge=0)
    zone: str = Field(default="Workshop A", max_length=100)

class InventoryItemCreate(InventoryItemBase):
    centre_id: int

class InventoryItemUpdate(BaseModel):
    item_name: Optional[str] = None
    sanctioned_quantity: Optional[int] = Field(None, ge=0)
    minimum_required: Optional[int] = Field(None, ge=0)
    zone: Optional[str] = None

class InventoryItemResponse(InventoryItemBase):
    id: int
    centre_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InventoryComplianceItem(BaseModel):
    item_type: str
    item_name: str
    zone: str
    sanctioned_quantity: int
    minimum_required: int
    detected_quantity: int
    potential_shortage: int
    compliance_percentage: float
    confidence: float
    status: str  # COMPLIANT, REVIEW, POTENTIAL_SHORTAGE, UNCERTAIN

class InventoryComplianceResponse(BaseModel):
    centre_id: int
    centre_code: str
    items: List[InventoryComplianceItem]
    overall_inventory_compliance: float
    total_shortages: int
    observation_window_minutes: int
