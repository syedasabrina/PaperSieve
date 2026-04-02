from pathlib import Path
from src.analyzer import analyze_paper
from src.scorer import save_json_log, append_to_csv, copy_pdf_to_bucket

pdf_dir = Path("data/test_pdfs")
run_dir = Path("results/test_run")

for pdf_path in pdf_dir.glob("*.pdf"):
    print(f"\nAnalyzing: {pdf_path.name}")
    record = analyze_paper(pdf_path, paper_id=pdf_path.stem)

    save_json_log(record, run_dir)
    append_to_csv(record, run_dir)

    print(f"Score: {record.score}/4 | Bucket: {record.bucket.value} | Retry: {record.retry_used}")

print("\nDone. Check results/test_run/rankings.csv and results/test_run/logs/")