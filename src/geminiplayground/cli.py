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


@cli.command()
def ui(
        host: str = "127.0.0.1",
        port: int = 8081,
        workers: int = os.cpu_count() * 2 + 1,
        reload: Annotated[bool, typer.Option("--reload")] = True,
        timeout: int = 12600,
):
    """
    Launch the web app
    """
    import uvicorn
    check_api_key()

    run_cmd = (
        f"gunicorn "
        f"geminiplayground.web.app:app "
        f"-w {workers} "
        f"--bind {host}:{port} "
        f"--timeout {timeout} "
        f"-k uvicorn.workers.UvicornWorker ")

    if reload:
        run_cmd += "--reload"

    os.system(run_cmd)


@cli.command()
def api(
        host: str = "127.0.0.1",
        port: int = 8081,
        workers: int = os.cpu_count() * 2 + 1,
        reload: Annotated[bool, typer.Option("--reload")] = True,
        timeout: int = 12600,

):
    """
    Launch the API
    """
    check_api_key()

    run_cmd = (
        f"gunicorn "
        f"geminiplayground.web.api:api "
        f"-w {workers} "
        f"--bind {host}:{port} "
        f"--timeout {timeout} "
        f"-k uvicorn.workers.UvicornWorker ")

    if reload:
        run_cmd += "--reload"

    os.system(run_cmd)


def run():
    """
    Run the app
    """
    cli()


if __name__ == "__main__":
    cli()
