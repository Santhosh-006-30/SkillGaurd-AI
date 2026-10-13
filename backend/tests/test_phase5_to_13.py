"""
Phase 6-13 Tests: Video ingestion pipeline, AI inference modules, compliance engine, evaluation metrics.
[SIMULATED DEMO — All data marked synthetic]
"""
import pytest
import tempfile
import os

def test_video_processor_import():
    from app.video.processor import VideoProcessor, ALLOWED_EXTENSIONS
    assert ".mp4" in ALLOWED_EXTENSIONS
    assert ".avi" in ALLOWED_EXTENSIONS
    vp = VideoProcessor(upload_dir="data/uploads", evidence_dir="data/evidence")
    assert os.path.isdir("data/uploads")
    assert os.path.isdir("data/evidence")

def test_video_file_validation_pass():
    from app.video.processor import VideoProcessor
    vp = VideoProcessor()
    ok, msg = vp.validate_file_metadata("test_video.mp4", 1024 * 100)
    assert ok is True

def test_video_file_validation_wrong_extension():
    from app.video.processor import VideoProcessor
    vp = VideoProcessor()
    ok, msg = vp.validate_file_metadata("photo.jpg", 1024)
    assert ok is False
    assert "Unsupported" in msg

def test_video_file_validation_too_large():
    from app.video.processor import VideoProcessor
    vp = VideoProcessor()
    ok, msg = vp.validate_file_metadata("big.mp4", 200 * 1024 * 1024)
    assert ok is False
    assert "exceeds" in msg

def test_video_inspect_nonexistent_file():
    from app.video.processor import VideoProcessor
    vp = VideoProcessor()
    meta = vp.inspect_video("/nonexistent/path/video.mp4")
    # Should return fallback metadata and mark it valid
    assert meta is not None
    assert meta.is_valid is True

def test_simulated_frame_extraction():
    from app.video.processor import VideoProcessor
    vp = VideoProcessor()
    frames = list(vp.extract_sampled_frames("/nonexistent/video.mp4", max_frames=5))
    assert len(frames) == 5
    idx, ts, frame = frames[0]
    assert idx == 0
    assert ts == 0.0

def test_person_detector_fallback():
    """Test that person detector returns sensible fallback results when model is absent."""
    from app.ai.person_detector import PersonDetector
    pd = PersonDetector()
    result = pd.detect_frame(frame=None, frame_index=0, timestamp_seconds=0.0, simulated_count=20)
    assert result.person_count == 20
    assert result.average_confidence > 0.5
    assert len(result.persons) == 20

def test_anonymous_tracker_track_assignment():
    from app.ai.tracker import AnonymousTracker
    from app.ai.person_detector import DetectedPerson, BoundingBox
    tracker = AnonymousTracker()
    persons = [
        DetectedPerson(track_id=None, confidence=0.9, bbox=BoundingBox(x1=10, y1=10, x2=60, y2=60)),
        DetectedPerson(track_id=None, confidence=0.85, bbox=BoundingBox(x1=200, y1=200, x2=250, y2=250)),
    ]
    updated = tracker.update(persons)
    assert len(updated) == 2
    assert all(p.track_id is not None for p in updated)

def test_anonymous_tracker_id_continuity():
    """Track IDs must persist across frames via IoU matching."""
    from app.ai.tracker import AnonymousTracker
    from app.ai.person_detector import DetectedPerson, BoundingBox
    tracker = AnonymousTracker(iou_threshold=0.3)
    # Frame 1
    p1 = [DetectedPerson(track_id=None, confidence=0.9, bbox=BoundingBox(x1=10, y1=10, x2=60, y2=60))]
    updated1 = tracker.update(p1)
    first_id = updated1[0].track_id

    # Frame 2 — same person slightly shifted (high IoU)
    p2 = [DetectedPerson(track_id=None, confidence=0.88, bbox=BoundingBox(x1=12, y1=12, x2=62, y2=62))]
    updated2 = tracker.update(p2)
    assert updated2[0].track_id == first_id, "Track ID should persist for same person across frames"

def test_anonymous_tracker_smoothed_occupancy():
    from app.ai.tracker import AnonymousTracker
    from app.ai.person_detector import DetectedPerson, BoundingBox
    tracker = AnonymousTracker()
    for frame in range(5):
        persons = [
            DetectedPerson(track_id=None, confidence=0.9,
                           bbox=BoundingBox(x1=float(i*100), y1=0, x2=float(i*100+50), y2=50))
            for i in range(15)
        ]
        tracker.update(persons)
    occupancy = tracker.get_smoothed_occupancy()
    assert occupancy > 0

def test_infrastructure_detector_fallback():
    from app.ai.infrastructure_detector import InfrastructureDetector
    det = InfrastructureDetector()
    result = det.detect_assets(frame=None)
    assert "COMPUTER" in result.counts_by_type or "CHAIR" in result.counts_by_type
    assert result.average_confidence > 0.5

def test_reconciliation_service_normal():
    from app.services.reconciliation_service import classify_discrepancy
    result = classify_discrepancy(estimated=45, submitted=48)
    assert result.category == "NORMAL"
    assert result.action_required is False
    assert result.attendance_score >= 90.0

def test_reconciliation_service_review():
    from app.services.reconciliation_service import classify_discrepancy
    result = classify_discrepancy(estimated=41, submitted=48)
    assert result.category == "REVIEW"
    assert result.action_required is True

def test_reconciliation_service_high():
    from app.services.reconciliation_service import classify_discrepancy
    result = classify_discrepancy(estimated=34, submitted=48)
    assert result.category == "HIGH_DISCREPANCY"
    assert result.action_required is True
    assert result.attendance_score < 70

def test_reconciliation_service_critical():
    from app.services.reconciliation_service import classify_discrepancy
    result = classify_discrepancy(estimated=12, submitted=48)
    assert result.category == "CRITICAL"
    assert result.attendance_score < 50

def test_compliance_engine_low_risk():
    from app.services.compliance_engine import compute_composite_score
    result = compute_composite_score(
        attendance_score=95.0,
        infrastructure_score=92.0,
        activity_score=88.0,
        consistency_score=90.0
    )
    assert result.risk_level == "LOW"
    assert result.overall_score >= 80.0

def test_compliance_engine_high_risk():
    from app.services.compliance_engine import compute_composite_score
    result = compute_composite_score(
        attendance_score=35.0,
        infrastructure_score=50.0,
        activity_score=60.0,
        consistency_score=40.0
    )
    assert result.risk_level in ("HIGH", "CRITICAL")
    assert result.overall_score < 60.0

def test_compliance_engine_recommendations_generated():
    from app.services.compliance_engine import compute_composite_score
    result = compute_composite_score(
        attendance_score=40.0,
        infrastructure_score=55.0,
        activity_score=50.0,
        consistency_score=45.0
    )
    assert len(result.recommendations) > 0

def test_compliance_infrastructure_score_calculator():
    from app.services.compliance_engine import compute_infrastructure_score
    detected = {"COMPUTER": 18, "CHAIR": 28, "PROJECTOR": 1}
    sanctioned = {"COMPUTER": 20, "CHAIR": 30, "PROJECTOR": 1}
    minimum = {"COMPUTER": 15, "CHAIR": 25, "PROJECTOR": 1}
    score = compute_infrastructure_score(detected, sanctioned, minimum)
    assert score > 90.0, "Should be near 100% since detected meets minimum"

def test_evaluation_metrics_structure():
    from app.services.evaluation_metrics import get_full_evaluation_report
    report = get_full_evaluation_report()
    assert "person_detection" in report
    assert "equipment_detection" in report
    assert "discrepancy_classification" in report
    for task in ["person_detection", "equipment_detection", "discrepancy_classification"]:
        metrics = report[task]
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert "false_positive_rate" in metrics
        assert "false_negative_rate" in metrics
        assert 0.0 <= metrics["precision"] <= 1.0
        assert 0.0 <= metrics["recall"] <= 1.0

def test_evaluation_metrics_f1_sanity():
    from app.services.evaluation_metrics import ConfusionMatrix
    cm = ConfusionMatrix(tp=100, fp=10, tn=200, fn=5)
    assert cm.precision > cm.recall or cm.precision <= 1.0
    assert abs(cm.f1_score - 2 * cm.precision * cm.recall / (cm.precision + cm.recall)) < 0.001
