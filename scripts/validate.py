# ---------------------------------------------------------------------------
# Validate — Compare Pipeline Run Results Against Gold Labels
# ---------------------------------------------------------------------------
# Responsibilities:
#   1. Load gold labels from data/validation_gold_labels.csv
#   2. Load pipeline results from results/<run_id>/rankings.csv
#   3. Compare per-criterion labels and bucket assignments
#   4. Report agreement rates per criterion and overall
# ---------------------------------------------------------------------------

from __future__ import annotations
import csv
import typer
from pathlib import Path


app = typer.Typer()


def load_csv(path: Path) -> dict[str, dict]:
    rows = {}
    with path.open("r", encoding= "utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows[row["paper_id"]] = row
    return rows


@app.command()
def validate(
    run_id: str = typer.Option(..., help="Run ID to vlidate e.g. validation_run_001"),
    gold_path: Path = typer.Option(default=Path("data/validation_gold_labels.csv"))
) -> None :
    run_dir = Path("results") / run_id
    rankings_csv = run_dir / "rankings.csv"

    if not rankings_csv.exists():
        typer.echo(f"No rankings.csv found at {rankings_csv}")
        raise typer.Exit()
    
    if not gold_path.exists():
        typer.echo(f"No gold labels found at {gold_path}")
        raise typer.Exit()
    
    gold = load_csv(gold_path)
    prediction = load_csv(rankings_csv)
    common = set(gold.keys()) & set(prediction.keys())

    typer.echo(f"\nPaper number in gold set: {len(gold)}")
    typer.echo(f"\nPaper number in prediction set: {len(prediction)}")
    typer.echo(f"\nPapers common in both set: {len(common)}")

    #label agreement per criteria
    criteria = ["q1", "q2", "q3", "q4"]
    typer.echo(f"-------------Per criterion label agrrement ----------------")
    for q in criteria:
        correct = sum(1 for pid in common if gold[pid][f"{q}_label"].lower()==prediction[pid][f"{q}_label"].lower())
        typer.echo(f"{q}: {correct}/{len(common)} ({100*correct//len(common)}%)")

    #agreement per bucket
    bucket_correct = sum(1 for pid in common if gold[pid]["bucket"].lower()==prediction[pid]["bucket"].lower())
    typer.echo(f"-------------Bucket agrrement ----------------")
    typer.echo(f"Exact match: {bucket_correct}/{len(common)} ({100*bucket_correct//len(common)}%)")

    # Safe direction check — no to_read paper went to filtered_out
    unsafe = [
        pid for pid in common
        if gold[pid]["bucket"] == "to_read" and prediction[pid]["bucket"] == "filtered_out"
    ]
    typer.echo(f"\n--- Safety check ---")
    typer.echo(f"to_read papers incorrectly filtered out: {len(unsafe)}")
    if unsafe:
        for pid in unsafe:
            typer.echo(f"  {pid}")


    #Precision, Recall, FP rate: to_read= positive class
    tp = sum(1 for pid in common if gold[pid]['bucket'].lower() == "to_read" and prediction[pid]['bucket'].lower()=='to_read')
    tn = sum(1 for pid in common if gold[pid]['bucket'].lower() != "to_read" and prediction[pid]['bucket'].lower()!='to_read')
    fp = sum(1 for pid in common if gold[pid]['bucket'].lower() != "to_read" and prediction[pid]['bucket'].lower()=='to_read')
    fn = sum(1 for pid in common if gold[pid]['bucket'].lower() == "to_read" and prediction[pid]['bucket'].lower()!='to_read')

    precision = tp/(tp+fp) if (tp+fp)>0 else 0.0
    recall = tp/(tp+fn) if (tp+fn)>0 else 0.0
    fpr = fp/(tn+fp) if (tn+fp)>0 else 0.0

    typer.echo(f"\n--- Precision / Recall / FPR (to_read as positive class) ---")
    typer.echo(f"True positives:  {tp}")
    typer.echo(f"False negatives: {fn}")
    typer.echo(f"False positives: {fp}")
    typer.echo(f"True negatives:  {tn}")
    typer.echo(f"Precision:       {precision:.2f}")
    typer.echo(f"Recall:          {recall:.2f}")
    typer.echo(f"False pos rate:  {fpr:.2f}")


    false_negatives = [
        pid for pid in common
        if gold[pid]["bucket"] == "to_read" and prediction[pid]["bucket"] != "to_read"
    ]
    false_positives = [
        pid for pid in common
        if gold[pid]["bucket"] != "to_read" and prediction[pid]["bucket"] == "to_read"
    ]
    if false_negatives:
        typer.echo(f"\nFalse negatives (missed to_read):")
        for pid in false_negatives:
            typer.echo(f"  {pid} → predicted: {prediction[pid]['bucket']}")
            
    if false_positives:
        typer.echo(f"\nFalse positives (wrongly sent to to_read):")
        for pid in false_positives:
            typer.echo(f"  {pid} → gold: {gold[pid]['bucket']}")


if __name__ == "__main__":
    app()

