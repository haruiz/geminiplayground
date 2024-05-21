import os

import typer
from typing_extensions import Annotated

cli = typer.Typer(invoke_without_command=True)


def check_api_key():
    """
    Check if the api key is set
    """
    # attempt to load the api key from the .env file
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
    # receive the api key from the command line
    api_key = os.environ.get("AISTUDIO_API_KEY", None)
    if not api_key:
        typer.echo(
            "Please set the AISTUDIO_API_KEY environment variable, or create a .env file with the api key obtained "
            "from https://aistudio.google.com/app/apikey"
        )
        raise typer.Abort()


@cli.command()
def ui(
    host: str = "localhost",
    port: int = 8081,
    workers: int = int(os.cpu_count() * 2 + 1),  # type: ignore
    reload: Annotated[bool, typer.Option("--reload")] = True,
    timeout: int = 12600,
):
    """
    Launch the web app
    """
    check_api_key()

    import uvicorn

    uvicorn.run(
        "geminiplayground.web.app:app",
        host=host,
        port=port,
        workers=workers,
        reload=reload,
    )


@cli.command()
def api(
    host: str = "localhost",
    port: int = 8081,
    workers: int = int(os.cpu_count() * 2 + 1),  # type: ignore
    reload: Annotated[bool, typer.Option("--reload")] = True,
):
    """
    Launch the API
    """
    check_api_key()

    import uvicorn

    uvicorn.run(
        "geminiplayground.web.api:api",
        host=host,
        port=port,
        workers=workers,
        reload=reload,
    )


def run():
    """
    Run the app
    """
    cli()


if __name__ == "__main__":
    cli()
