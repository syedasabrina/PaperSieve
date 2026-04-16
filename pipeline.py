# ---------------------------------------------------------------------------
# Pipeline — Full Paper Screening Orchestrator
# ---------------------------------------------------------------------------
# Responsibilities:
#   1. Accept input folder and run ID from command line
#   2. Find all PDFs in input folder
#   3. Skip papers already processed in this run (crash recovery)
#   4. For each PDF: analyze, log, append to CSV
#   5. Handle per-paper errors without stopping the full run
#   6. Show progress bar
#   7. Auto-retry unprocessed papers after a completed run
# ---------------------------------------------------------------------------

from __future__ import annotations
import typer
from pathlib import Path
from datetime import datetime, timezone
import csv
from tqdm import tqdm
from src.analyzer import analyze_paper, call_with_backoff
from src.scorer import save_json_log, append_to_csv

app = typer.Typer()


def retry_failed(run_id: str, input_dir: Path, model: str = "gemini-2.5-flash", retry_model: str = "gemini-2.5-pro") -> None:
    run_dir = Path("results") / run_id
    rankings_csv = run_dir / "rankings.csv"

    if not rankings_csv.exists():
        typer.echo(f"No rankings.csv found at {rankings_csv}")
        return

    processed_ids: set[str] = set()
    with rankings_csv.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            processed_ids.add(row["paper_id"])

    all_pdfs = sorted(input_dir.glob("*.pdf"))
    to_retry = [p for p in all_pdfs if p.stem not in processed_ids]

    typer.echo(f"\nRetrying {len(to_retry)} unprocessed papers...")

    succeeded = 0
    failed = []

    for pdf_path in to_retry:
        typer.echo(f"Processing: {pdf_path.name}")
        try:
            record = call_with_backoff(analyze_paper, pdf_path, pdf_path.stem, model=model, retry_model=retry_model)
            save_json_log(record, run_dir)
            append_to_csv(record, run_dir)
            typer.echo(f"  Done. Score: {record.score}/4 | Bucket: {record.bucket.value}")
            succeeded += 1
        except Exception as e:
            typer.echo(f"  Failed: {e}")
            failed.append((pdf_path.name, str(e)))

    typer.echo(f"\nRetry done. {succeeded} succeeded, {len(failed)} still failed.")
    if failed:
        for name, err in failed:
            typer.echo(f"  {name}: {err}")


@app.command()
def run(
    input_dir: Path = typer.Option(..., help="Folder of PDFs to process"),
    run_id: str = typer.Option(default=None, help="Run identifier e.g. run_001"),
    model: str = typer.Option(default="gemini-2.5-flash", help="Main screening model"),
    retry_model: str = typer.Option(default="gemini-2.5-pro", help="Model for low-confidence retries"),
) -> None:
    
    if run_id is None:
        run_id = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

    run_dir = Path("results") / run_id

    typer.echo(f"Run ID:      {run_id}")
    typer.echo(f"Input:       {input_dir}")
    typer.echo(f"Output:      {run_dir}")
    typer.echo(f"Model:       {model}")
    typer.echo(f"Retry model: {retry_model}")

    # Find all PDFs in input folder
    pdf_files = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        typer.echo(f"No PDFs found in {input_dir}")
        raise typer.Exit()

    # Load already processed paper IDs for crash recovery
    rankings_csv = run_dir / "rankings.csv"
    processed_ids: set[str] = set()
    if rankings_csv.exists():
        with rankings_csv.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed_ids.add(row["paper_id"])

    typer.echo(f"Found:     {len(pdf_files)} PDFs")
    typer.echo(f"Skipping:  {len(processed_ids)} already processed")

    to_process = [p for p in pdf_files if p.stem not in processed_ids]
    typer.echo(f"Processing:{len(to_process)} PDFs")

    errors: list[tuple[str, str]] = []

    for pdf_path in tqdm(to_process, desc="Screening", unit="paper"):
        try:
            record = analyze_paper(pdf_path, paper_id=pdf_path.stem, model=model, retry_model=retry_model)
            save_json_log(record, run_dir)
            append_to_csv(record, run_dir)
        except Exception as e:
            errors.append((pdf_path.name, str(e)))
            tqdm.write(f"ERROR: {pdf_path.name} — {e}")
            continue

    typer.echo(f"\nDone. {len(to_process) - len(errors)} succeeded, {len(errors)} failed.")
    if errors:
        typer.echo("Failed papers:")
        for name, err in errors:
            typer.echo(f"  {name}: {err}")
        retry_failed(run_id=run_id, input_dir=input_dir, model=model, retry_model=retry_model)


if __name__ == "__main__":
    app()