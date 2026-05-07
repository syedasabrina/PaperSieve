# ---------------------------------------------------------------------------
# Verify Pipeline — Verifiability Run Orchestrator
# ---------------------------------------------------------------------------
# Mirrors pipeline.py but runs the three verifiability prompts per paper.
#
# Responsibilities:
#   1. Accept input folder, run ID, and model from command line
#   2. Find all PDFs in input folder
#   3. Skip papers already processed in this run (crash recovery)
#   4. For each PDF: verify, log, append to xlsx
#   5. Handle per-paper errors without stopping the full run
#   6. Show progress bar
# ---------------------------------------------------------------------------

from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from tqdm import tqdm
import typer
from src.verify import verify_paper, DEFAULT_VERIFY_MODEL
from src.verify_writer import append_to_xlsx, load_processed_ids

verify_app = typer.Typer()


def record_to_log(record) -> dict:
    return json.loads(record.model_dump_json())


@verify_app.command()
def run(
    input_dir: Path = typer.Option(..., help="Folder of PDFs to verify"),
    run_id: str = typer.Option(default=None, help="Run identifier e.g. verify_001"),
    model: str = typer.Option(default=DEFAULT_VERIFY_MODEL, help="Gemini model to use e.g. gemini-2.5-flash or gemini-2.5-pro"),
) -> None:

    if run_id is None:
        run_id = datetime.now(timezone.utc).strftime("verify_%Y-%m-%dT%H-%M-%S")

    run_dir = Path("results") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = run_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    xlsx_path = run_dir / "verifiability.xlsx"

    typer.echo(f"Run ID:    {run_id}")
    typer.echo(f"Input:     {input_dir}")
    typer.echo(f"Output:    {run_dir}")
    typer.echo(f"Model:     {model}")

    pdf_files = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        typer.echo(f"No PDFs found in {input_dir}")
        raise typer.Exit()

    processed_ids = load_processed_ids(xlsx_path)

    typer.echo(f"Found:     {len(pdf_files)} PDFs")
    typer.echo(f"Skipping:  {len(processed_ids)} already processed")

    to_process = [p for p in pdf_files if p.stem not in processed_ids]
    typer.echo(f"Processing:{len(to_process)} PDFs")

    errors: list[tuple[str, str]] = []

    for pdf_path in tqdm(to_process, desc="Verifying", unit="paper"):
        try:
            record = verify_paper(pdf_path, paper_id=pdf_path.stem, model=model)

            log_path = logs_dir / f"{pdf_path.stem}.json"
            log_path.write_text(
                json.dumps(record_to_log(record), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            append_to_xlsx(record, xlsx_path)

        except Exception as e:
            errors.append((pdf_path.name, str(e)))
            tqdm.write(f"ERROR: {pdf_path.name} — {e}")
            continue

    typer.echo(f"\nDone. {len(to_process) - len(errors)} succeeded, {len(errors)} failed.")
    if errors:
        typer.echo("Failed papers:")
        for name, err in errors:
            typer.echo(f"  {name}: {err}")