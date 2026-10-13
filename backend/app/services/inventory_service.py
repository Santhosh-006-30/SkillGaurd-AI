from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import InventoryItem, TrainingCentre, ItemType
from app.schemas.infrastructure import InventoryItemCreate, InventoryItemUpdate

class InventoryService:
    @staticmethod
    def get_items(
        db: Session,
        centre_id: Optional[int] = None,
        item_type: Optional[ItemType] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[InventoryItem]:
        query = db.query(InventoryItem)
        if centre_id:
            query = query.filter(InventoryItem.centre_id == centre_id)
        if item_type:
            query = query.filter(InventoryItem.item_type == item_type)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_item_by_id(db: Session, item_id: int) -> Optional[InventoryItem]:
        return db.query(InventoryItem).filter(InventoryItem.id == item_id).first()

    @staticmethod
    def create_item(db: Session, obj_in: InventoryItemCreate) -> InventoryItem:
        item = InventoryItem(**obj_in.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update_item(db: Session, item_id: int, obj_in: InventoryItemUpdate) -> Optional[InventoryItem]:
        item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
        if not item:
            return None
        for field, val in obj_in.model_dump(exclude_unset=True).items():
            setattr(item, field, val)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_item(db: Session, item_id: int) -> bool:
        item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True

    @staticmethod
    def get_inventory_compliance(db: Session, centre_id: int) -> Optional[dict]:
        centre = db.query(TrainingCentre).filter(TrainingCentre.id == centre_id).first()
        if not centre:
            return None

        items = db.query(InventoryItem).filter(InventoryItem.centre_id == centre_id).all()
        if not items:
            return {
                "centre_id": centre.id,
                "centre_code": centre.centre_code,
                "items": [],
                "overall_inventory_compliance": 100.0,
                "total_shortages": 0,
                "observation_window_minutes": 15
            }

        # Simulated AI detected baseline for testing/demo compliance view
        compliance_items = []
        total_sanctioned = 0
        total_detected = 0
        total_shortages = 0

        for it in items:
            sanc = it.sanctioned_quantity
            min_req = it.minimum_required
            
            # For Centre 3 (TN-CBE-003), machine has shortage demo scenario
            if centre.centre_code == "TN-CBE-003" and it.item_type == ItemType.MACHINE:
                det = max(0, sanc - 3)
            elif centre.centre_code == "TN-CBE-002" and it.item_type == ItemType.COMPUTER:
                det = max(0, sanc - 1)
            else:
                det = sanc

            shortage = max(0, min_req - det)
            comp_pct = round((det / sanc * 100.0), 1) if sanc > 0 else 100.0

            status = "COMPLIANT"
            if shortage > 0 or comp_pct < 80.0:
                status = "POTENTIAL_SHORTAGE"
            elif comp_pct < 95.0:
                status = "REVIEW"

            compliance_items.append({
                "item_type": it.item_type.value,
                "item_name": it.item_name,
                "zone": it.zone,
                "sanctioned_quantity": sanc,
                "minimum_required": min_req,
                "detected_quantity": det,
                "potential_shortage": shortage,
                "compliance_percentage": comp_pct,
                "confidence": 0.88,
                "status": status
            })

            total_sanctioned += sanc
            total_detected += det
            total_shortages += shortage

        overall_pct = round((total_detected / total_sanctioned * 100.0), 1) if total_sanctioned > 0 else 100.0

        return {
            "centre_id": centre.id,
            "centre_code": centre.centre_code,
            "items": compliance_items,
            "overall_inventory_compliance": min(100.0, overall_pct),
            "total_shortages": total_shortages,
            "observation_window_minutes": 15
        }
