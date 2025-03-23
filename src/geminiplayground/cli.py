import os
from typing import Optional

import typer
from typing_extensions import Annotated
from dotenv import load_dotenv, find_dotenv
from geminiplayground.catching import cache

app = typer.Typer(invoke_without_command=True)


def set_api_key_env(api_key: Optional[str] = None):
    """Ensure the API key is set in environment variables."""
    load_dotenv(find_dotenv())

    # If provided explicitly, set it
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key

    if not os.environ.get("GEMINI_API_KEY"):
        typer.echo(
            "❌ Missing GEMINI_API_KEY.\n"
            "Set it as an environment variable or in a .env file.\n"
            "Get your API key at: https://aistudio.google.com/app/apikey"
        )
        raise typer.Abort()


def dispatch_fastapi_app(
        app: str,
        host: str,
        port: int,
        workers: Optional[int] = None,
        reload: bool = True
):
    """Launch a FastAPI app using Uvicorn."""
    import uvicorn
    if workers is None:
        workers = (os.cpu_count() or 1) * 2 + 1
    uvicorn.run(app, host=host, port=port, workers=workers, reload=reload)


@app.command()
def ui(
        host: Annotated[str, typer.Option("--host")] = "0.0.0.0",
        port: Annotated[int, typer.Option("--port")] = 8080,
        workers: Annotated[Optional[int], typer.Option("--workers")] = None,
        reload: Annotated[bool, typer.Option("--reload")] = False,
        api_key: Annotated[Optional[str], typer.Option(envvar="GEMINI_API_KEY")] = None,
):
    """Launch the web UI."""
    set_api_key_env(api_key)
    dispatch_fastapi_app("geminiplayground.web.app:app", host, port, workers, reload)


@app.command()
def api(
        host: Annotated[str, typer.Option("--host")] = "0.0.0.0",
        port: Annotated[int, typer.Option("--port")] = 8080,
        workers: Annotated[int, typer.Option("--workers")] = (os.cpu_count() or 1) * 2 + 1,
        reload: Annotated[bool, typer.Option("--reload")] = False,
        api_key: Annotated[Optional[str], typer.Option(envvar="GEMINI_API_KEY")] = None,
):
    """Launch the API."""
    set_api_key_env(api_key)
    dispatch_fastapi_app("geminiplayground.web.api:api", host, port, workers, reload)


@app.command(name="clear-cache")
def clear_cache():
    """Clear the application cache."""
    cache.clear()
    typer.echo("✅ Cache cleared.")


if __name__ == "__main__":
    app()
