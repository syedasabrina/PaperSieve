from pipeline import app
from verify_pipeline import verify_app

app.add_typer(verify_app, name="verify")

if __name__ == "__main__":
    app()