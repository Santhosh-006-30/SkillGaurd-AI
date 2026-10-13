from typing import List, Dict, Tuple, Optional
import math
from app.ai.person_detector import BoundingBox, DetectedPerson

class AnonymousTracker:
    """
    Session-scoped anonymous multi-object tracker.
    Provides temporal consistency across sampled video frames without persistent biometric profiling.
    Uses Intersection-over-Union (IoU) spatial association with short-lived session IDs.
    """

    def __init__(self, iou_threshold: float = 0.3, max_lost_frames: int = 5):
        self.iou_threshold = iou_threshold
        self.max_lost_frames = max_lost_frames
        self.next_id = 1
        self.tracks: Dict[int, Dict] = {}  # track_id -> {bbox, lost_count, history}
        self.occupancy_history: List[int] = []

    def _compute_iou(self, boxA: BoundingBox, boxB: BoundingBox) -> float:
        xA = max(boxA.x1, boxB.x1)
        yA = max(boxA.y1, boxB.y1)
        xB = min(boxA.x2, boxB.x2)
        yB = min(boxA.y2, boxB.y2)

        interArea = max(0.0, xB - xA) * max(0.0, yB - yA)
        boxAArea = max(1.0, (boxA.x2 - boxA.x1) * (boxA.y2 - boxA.y1))
        boxBArea = max(1.0, (boxB.x2 - boxB.x1) * (boxB.y2 - boxB.y1))

        iou = interArea / float(boxAArea + boxBArea - interArea)
        return max(0.0, min(1.0, iou))

    def update(self, detected_persons: List[DetectedPerson]) -> List[DetectedPerson]:
        """
        Associate detections in current frame with active tracks.
        Assigns or updates track_id on each DetectedPerson.
        """
        updated_persons: List[DetectedPerson] = []
        assigned_tracks = set()

        for person in detected_persons:
            best_id = None
            best_iou = 0.0

            for tid, tdata in self.tracks.items():
                if tid in assigned_tracks:
                    continue
                iou = self._compute_iou(person.bbox, tdata["bbox"])
                if iou > best_iou and iou >= self.iou_threshold:
                    best_iou = iou
                    best_id = tid

            if best_id is not None:
                # Match found: update existing track
                self.tracks[best_id]["bbox"] = person.bbox
                self.tracks[best_id]["lost_count"] = 0
                assigned_tracks.add(best_id)
                person.track_id = best_id
            else:
                # New track assigned
                new_id = self.next_id
                self.next_id += 1
                self.tracks[new_id] = {
                    "bbox": person.bbox,
                    "lost_count": 0,
                }
                assigned_tracks.add(new_id)
                person.track_id = new_id

            updated_persons.append(person)

        # Increment lost count for unmatched active tracks and prune expired ones
        dead_tracks = []
        for tid in self.tracks:
            if tid not in assigned_tracks:
                self.tracks[tid]["lost_count"] += 1
                if self.tracks[tid]["lost_count"] > self.max_lost_frames:
                    dead_tracks.append(tid)

        for tid in dead_tracks:
            del self.tracks[tid]

        # Record occupancy for temporal smoothing
        self.occupancy_history.append(len(updated_persons))
        return updated_persons

    def get_smoothed_occupancy(self) -> int:
        """
        Calculate median smoothed occupancy over the session to filter transient occlusions.
        """
        if not self.occupancy_history:
            return 0
        sorted_counts = sorted(self.occupancy_history)
        mid = len(sorted_counts) // 2
        return sorted_counts[mid]
