# ---------------------------------------------------------------------------
# Retry Failed — Re-process papers that failed due to 503 errors
# ---------------------------------------------------------------------------
# Reads the failed paper IDs, retries them with exponential backoff,
# and appends results to the existing run's rankings.csv
# ---------------------------------------------------------------------------

from __future__ import annotations
import time
import csv
import typer
from pathlib import Path
from src.analyzer import analyze_paper
from src.scorer import save_json_log, append_to_csv

app = typer.Typer()


def call_with_backoff(fn, *args, max_attempts: int = 5, wait_seconds: int = 30, **kwargs):
    for attempt in range(max_attempts):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if "503" in str(e) and attempt < max_attempts - 1:
                typer.echo(f"  503 error, waiting {wait_seconds}s before retry (attempt {attempt + 1}/{max_attempts})")
                time.sleep(wait_seconds)
                continue
            raise


@app.command()
def retry(
    run_id: str = typer.Option(..., help="Run ID of the failed run e.g. full_run_001"),
    input_dir: Path = typer.Option(..., help="Folder where source PDFs live"),
) -> None:
    run_dir = Path("results") / run_id
    rankings_csv = run_dir / "rankings.csv"

    if not rankings_csv.exists():
        typer.echo(f"No rankings.csv found at {rankings_csv}")
        raise typer.Exit()

    # Load already processed paper IDs
    processed_ids: set[str] = set()
    with rankings_csv.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            processed_ids.add(row["paper_id"])

    # Find all PDFs not yet processed
    all_pdfs = sorted(input_dir.glob("*.pdf"))
    to_retry = [p for p in all_pdfs if p.stem not in processed_ids]

    typer.echo(f"Found {len(to_retry)} unprocessed papers to retry")

    succeeded = 0
    failed = []

    for pdf_path in to_retry:
        typer.echo(f"Processing: {pdf_path.name}")
        try:
            record = call_with_backoff(
                analyze_paper,
                pdf_path,
                pdf_path.stem,
            )
            save_json_log(record, run_dir)
            append_to_csv(record, run_dir)
            typer.echo(f"  Done. Score: {record.score}/4 | Bucket: {record.bucket.value}")
            succeeded += 1
        except Exception as e:
            typer.echo(f"  Failed: {e}")
            failed.append((pdf_path.name, str(e)))

    typer.echo(f"\nDone. {succeeded} succeeded, {len(failed)} failed.")
    if failed:
        typer.echo("Still failing:")
        for name, err in failed:
            typer.echo(f"  {name}: {err}")


if __name__ == "__main__":
    app()