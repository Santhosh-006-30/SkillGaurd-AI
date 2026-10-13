"""
Low-Bandwidth and Offline Synchronization Service — Phase 14
Handles edge-buffering, store-and-forward batch telemetry, and adaptive sampling for rural/intermittent connectivity.
[SIMULATED DEMO — SIH 26245]
"""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field

@dataclass
class EdgeQueueItem:
    item_id: str
    centre_id: int
    camera_id: Optional[int]
    payload_type: str  # ATTENDANCE_HEARTBEAT | DETECTION_EVENT | OCCUPANCY_BATCH
    payload: Dict[str, Any]
    queued_at: str
    synced: bool = False
    synced_at: Optional[str] = None

class OfflineSyncManager:
    """Manages edge device buffering and asynchronous replay for remote centres."""
    def __init__(self):
        self._queue: List[EdgeQueueItem] = []
        self._max_queue_size = 500
        # Initialize with simulated edge queue items for demonstration
        self._seed_demo_edge_items()

    def _seed_demo_edge_items(self):
        demo_items = [
            {
                "centre_id": 1,
                "camera_id": 1,
                "payload_type": "OCCUPANCY_BATCH",
                "payload": {"headcount": 42, "window": "09:00-09:30", "confidence": 0.94}
            },
            {
                "centre_id": 2,
                "camera_id": 2,
                "payload_type": "ATTENDANCE_HEARTBEAT",
                "payload": {"headcount": 18, "submitted_claimed": 35, "discrepancy_alert": True}
            },
            {
                "centre_id": 3,
                "camera_id": 4,
                "payload_type": "DETECTION_EVENT",
                "payload": {"asset_type": "COMPUTER", "count_detected": 15, "missing_delta": -5}
            }
        ]
        now = datetime.now(timezone.utc).isoformat()
        for d in demo_items:
            self._queue.append(EdgeQueueItem(
                item_id=str(uuid.uuid4()),
                centre_id=d["centre_id"],
                camera_id=d["camera_id"],
                payload_type=d["payload_type"],
                payload=d["payload"],
                queued_at=now,
                synced=False
            ))

    def enqueue(self, centre_id: int, payload_type: str, payload: Dict[str, Any], camera_id: Optional[int] = None) -> EdgeQueueItem:
        if len(self._queue) >= self._max_queue_size:
            # Purge oldest synced
            self._queue = [x for x in self._queue if not x.synced]
            if len(self._queue) >= self._max_queue_size:
                self._queue.pop(0)

        item = EdgeQueueItem(
            item_id=str(uuid.uuid4()),
            centre_id=centre_id,
            camera_id=camera_id,
            payload_type=payload_type,
            payload=payload,
            queued_at=datetime.now(timezone.utc).isoformat(),
            synced=False
        )
        self._queue.append(item)
        return item

    def get_pending(self, centre_id: Optional[int] = None) -> List[EdgeQueueItem]:
        items = [x for x in self._queue if not x.synced]
        if centre_id is not None:
            items = [x for x in items if x.centre_id == centre_id]
        return items

    def sync_all(self, centre_id: Optional[int] = None) -> Dict[str, Any]:
        """Mark pending edge items as synchronized to central SOC database."""
        now = datetime.now(timezone.utc).isoformat()
        count = 0
        for item in self._queue:
            if not item.synced and (centre_id is None or item.centre_id == centre_id):
                item.synced = True
                item.synced_at = now
                count += 1

        return {
            "synced_count": count,
            "remaining_pending": len(self.get_pending(centre_id)),
            "synced_at": now
        }

    def get_adaptive_config(self, bandwidth_kbps: float = 128.0) -> Dict[str, Any]:
        """
        Dynamically calculate frame sampling and payload compression based on estimated bandwidth.
        Prevents network congestion in remote ITIs / rural centres.
        """
        if bandwidth_kbps < 256.0:
            mode = "ULTRA_LOW"
            sample_rate_fps = 0.2  # 1 frame every 5 seconds
            compression_level = "HIGH"
            max_resolution = "640x360"
            metadata_only = True
        elif bandwidth_kbps < 1024.0:
            mode = "LOW"
            sample_rate_fps = 1.0  # 1 frame per second
            compression_level = "MEDIUM"
            max_resolution = "1280x720"
            metadata_only = False
        else:
            mode = "STANDARD"
            sample_rate_fps = 5.0  # 5 frames per second
            compression_level = "LOW"
            max_resolution = "1920x1080"
            metadata_only = False

        return {
            "bandwidth_kbps": bandwidth_kbps,
            "adaptive_mode": mode,
            "sample_rate_fps": sample_rate_fps,
            "compression_level": compression_level,
            "max_resolution": max_resolution,
            "metadata_only_transmission": metadata_only,
            "edge_buffer_max_hours": 72,
            "description": f"Adaptive sampling tuned for {mode} bandwidth profile ({bandwidth_kbps} kbps)."
        }

# Global singleton
offline_sync_manager = OfflineSyncManager()
