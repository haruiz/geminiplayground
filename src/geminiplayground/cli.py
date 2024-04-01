import typer
from typing_extensions import Annotated

cli = typer.Typer(invoke_without_command=True)


@cli.callback()
def ui(
    host: str = "127.0.0.1",
    port: int = 8081,
    workers: int = 5,
    reload: Annotated[bool, typer.Option("--reload")] = True,
):
    """
    Lauch legopy web app
    """
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
    host: str = "127.0.0.1",
    port: int = 8081,
    workers: int = 5,
    reload: Annotated[bool, typer.Option("--reload")] = True,
):
    """
    Lauch legopy web app
    """
    import uvicorn

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
