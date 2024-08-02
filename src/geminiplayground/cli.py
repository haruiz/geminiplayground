import os
import typing

import typer
from typing_extensions import Annotated
from geminiplayground.catching import cache

cli = typer.Typer(invoke_without_command=True)


def check_api_key():
    """
    Check if the api key is set
    """
    # attempt to load the api key from the .env file
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
    # receive the api key from the command line
    api_key = os.environ.get("GOOGLE_API_KEY", None)
    if not api_key:
        typer.echo(
            "Please set the AISTUDIO_API_KEY environment variable, or create a .env file with the api key obtained "
            "from https://aistudio.google.com/app/apikey"
        )
        raise typer.Abort()


def dispatch_fastapi_app(
        app: str, host: str, port: int, workers: typing.Optional[int], reload: bool = True
):
    """
    Launch the app
    """
    import uvicorn

    if workers is None:
        cpu_count = os.cpu_count() or 1
        workers = 1  # cpu_count * 2 + 1

    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=workers,
        reload=reload,
    )


@cli.command()
def ui(
        host: str = "localhost",
        port: int = 8080,
        workers: typing.Optional[int] = None,
        reload: Annotated[bool, typer.Option("--reload")] = True,
        api_key: str = typer.Option(None, envvar="GOOGLE_API_KEY")
):
    """
    Launch the web app
    """
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

    check_api_key()

    dispatch_fastapi_app("geminiplayground.web.app:app", host, port, workers, reload)


@cli.command()
def api(
        host: str = "0.0.0.0",
        port: int = 8080,
        workers: int = os.cpu_count() * 2 + 1,
        reload: Annotated[bool, typer.Option("--reload")] = True,
        api_key: str = typer.Option(None, envvar="GOOGLE_API_KEY")
):
    """
    Launch the API
    """
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

    check_api_key()

    dispatch_fastapi_app("geminiplayground.web.api:api", host, port, workers, reload)


@cli.command(
    name="clear-cache"
)
def clear_cache():
    """
    Clear the cache
    """
    cache.clear()


@cli.command(
    name="clear-cache"
)
def clear_cache():
    """
    Clear the cache
    """
    cache.clear()


def run():
    """
    Run the app
    """
    cli()


if __name__ == "__main__":
    run()
