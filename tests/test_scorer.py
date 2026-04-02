from pathlib import Path
from src.analyzer import analyze_paper
from src.scorer import save_json_log, append_to_csv, copy_pdf_to_bucket

pdf_dir = Path("data/test_pdfs")

for pdf_path in pdf_dir.glob("*.pdf"):
    # if "case-1.3" not in pdf_path.name:
    #     continue
    print(f"\nAnalyzing: {pdf_path.name}")
    record = analyze_paper(pdf_path, paper_id=pdf_path.stem)

    for qid in ["q1", "q2", "q3", "q4"]:
        criterion = getattr(record, qid)
        print(f"  {qid}: {criterion.label.value} | {criterion.confidence.value}")
        print(f"       quote: {criterion.quote}")
        print(f"       reason: {criterion.justification}")

    save_json_log(record)
    append_to_csv(record)
    copy_pdf_to_bucket(pdf_path, record)

    print(f"Score: {record.score}/4 | Bucket: {record.bucket.value} | Retry: {record.retry_used}")

print("\nAll done. Check results/logs/, results/rankings.csv, and data/ subfolders.")