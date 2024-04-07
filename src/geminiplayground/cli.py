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
            "from https://aistudio.google.com/app/apikey")
        raise typer.Abort()


@cli.callback()
def ui(
        host: str = "127.0.0.1",
        port: int = 8081,
        workers: int = 5,
        api_key: Annotated[str, typer.Argument(envvar="AISTUDIO_API_KEY")] = None,
        reload: Annotated[bool, typer.Option("--reload")] = True,
):
    """
    Lauch the web app
    """
    import uvicorn
    check_api_key()

    uvicorn.run(
        "geminiplayground.web.app:app",
        host=host,
        port=port,
        workers=workers,
        reload=reload,
    )


@cli.command()
def api(
        host: str = "127.0.0.1",
        port: int = 8081,
        workers: int = 5,
        reload: Annotated[bool, typer.Option("--reload")] = True,

):
    """
    Lauch the API
    """
    import uvicorn
    check_api_key()

    uvicorn.run(
        "geminiplayground.web.app:api",
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
