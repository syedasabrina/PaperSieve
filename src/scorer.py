# ---------------------------------------------------------------------------
# Scorer — Persist and Route Paper Results
# ---------------------------------------------------------------------------
# Responsibilities:
#   1. Save full PaperRecord as JSON to results/logs/<paper_id>.json
#   2. Append a summary row to results/rankings.csv
#   3. Copy the PDF to the correct data/ subfolder based on bucket
#      Buckets: to_read, maybe_recheck, maybe_borderline, filtered_out
# ---------------------------------------------------------------------------


from __future__ import annotations
import json
import csv
import shutil
from pathlib import Path
from src.models import PaperRecord, FinalBucket


RESULTS_DIR = Path("results")
LOGS_DIR = RESULTS_DIR / "logs"

RANKINGS_CSV = RESULTS_DIR / "rankings.csv"
CSV_HEADERS = [
    "paper_id", "title", "score", "bucket", "manual_review", "q1_label", "q1_confidence",
    "q2_label", "q2_confidence", "q3_label", "q3_confidence", "q4_label", "q4_confidence",
    "retry_used", "retry_count", "model_version", "prompt_version", "timestamp",
]

DATA_BUCKETS: dict[FinalBucket, Path] = {
    FinalBucket.TO_READ: Path("data/to_read"),
    FinalBucket.MAYBE_RECHECK: Path("data/maybe_recheck"),
    FinalBucket.MAYBE_BORDERLINE: Path("data/maybe_borderline"),
    FinalBucket.FILTERED_OUT: Path("data/filtered_out"),
}


def save_json_log(record: PaperRecord) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR/ f"{record.paper_id}.json"
    log_path.write_text(json.dumps(record.model_dump(), indent=2, default=str))

def append_to_csv(record: PaperRecord) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    write_header = not RANKINGS_CSV.exists()

    if not write_header:
        with RANKINGS_CSV.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["paper_id"] == record.paper_id:
                    return

    with RANKINGS_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if write_header:
            writer.writeheader()
        writer.writerow({
            "paper_id": record.paper_id,
            "title": record.title,
            "score": record.score,
            "bucket": record.bucket.value,
            "manual_review": record.manual_review,
            "q1_label": record.q1.label.value,
            "q1_confidence": record.q1.confidence.value,
            "q2_label": record.q2.label.value,
            "q2_confidence": record.q2.confidence.value,
            "q3_label": record.q3.label.value,
            "q3_confidence": record.q3.confidence.value,
            "q4_label": record.q4.label.value,
            "q4_confidence": record.q4.confidence.value,
            "retry_used": record.retry_used,
            "retry_count": record.retry_count,
            "model_version": record.model_version,
            "prompt_version": record.prompt_version,
            "timestamp": record.timestamp,
        })


def copy_pdf_to_bucket(pdf_path: Path, record: PaperRecord) -> None:
    destination_dir = DATA_BUCKETS[record.bucket]
    destination_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pdf_path, destination_dir / pdf_path.name)

