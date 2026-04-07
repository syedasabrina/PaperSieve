# ---------------------------------------------------------------------------
# Route Files — Copy PDFs to Bucket Folders Based on Run Results
# ---------------------------------------------------------------------------
# Responsibilities:
#   1. Accept a run ID from command line
#   2. Read results/<run_id>/rankings.csv
#   3. For each paper, find the PDF in the source folder
#   4. Copy it to the correct data/ bucket folder
# ---------------------------------------------------------------------------

from __future__ import annotations
import csv
import typer
import shutil
from pathlib import Path

app = typer.Typer()

DATA_BUCKETS = {
    "to_read": Path("data/to_read"),
    "maybe_recheck": Path("data/maybe_recheck"),
    "maybe_borderline": Path("data/maybe_borderline"),
    "filtered_out": Path("data/filtered_out"),
}


@app.command()
def route(
    run_id: str = typer.Option(..., help="Run ID to route files for e.g. run_001"),
    source_dir: Path = typer.Option(..., help="Folder where source PDFs currently live"),
) -> None:
    run_dir = Path("results") / run_id
    rankings_csv = run_dir / "rankings.csv"

    if not rankings_csv.exists():
        typer.echo(f"No rankings.csv found at {rankings_csv}")
        raise typer.Exit()

    typer.echo(f"Run ID:    {run_id}")
    typer.echo(f"Source:    {source_dir}")
    typer.echo(f"Rankings:  {rankings_csv}")

    copied = 0
    skipped = 0
    errors = []

    with rankings_csv.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            paper_id = row["paper_id"]
            bucket = row["bucket"]
            pdf_path = source_dir / f"{paper_id}.pdf"

            if not pdf_path.exists():
                errors.append(f"{paper_id}: PDF not found im {source_dir}")
                continue

            destination_dir = DATA_BUCKETS.get(bucket)
            if destination_dir is None:
                errors.append(f"{paper_id}: unknown bucket '{bucket}'")
                continue

            destination_dir.mkdir(parents=True, exist_ok=True)
            destination = destination_dir / pdf_path.name

            if destination.exists():
                skipped += 1
                continue

            shutil.copy2(pdf_path, destination)
            copied += 1

    typer.echo(f"\nDone. {copied} copied, {skipped} already existed, {len(errors)} errors.")

    if errors:
        typer.echo("Errors:")
        for err in errors:
            typer.echo(f" {err}")


if __name__ == "__main__":
    app()