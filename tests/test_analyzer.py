from pathlib import Path
from src.analyzer import analyze_paper

pdf_path = Path("data/manual_validation/2023.dstc-1.23.pdf")

print(f"Analyzing: {pdf_path.name}")
record = analyze_paper(pdf_path, paper_id="dstc-1.23")

print(f"\n--- RESULT ---")
print(f"Score:         {record.score}/4")
print(f"Bucket:        {record.bucket.value}")
print(f"Manual review: {record.manual_review}")
print(f"Retry used:    {record.retry_used} ({record.retry_count} retries)")

print(f"\n--- CRITERIA ---")
for qid in ["q1", "q2", "q3", "q4"]:
    criterion = getattr(record, qid)
    print(f"\n{qid.upper()}")
    print(f"  Label:      {criterion.label.value}")
    print(f"  Confidence: {criterion.confidence.value}")
    print(f"  Section:    {criterion.section}")
    print(f"  Quote:      {criterion.quote}")
    print(f"  Reason:     {criterion.justification}")