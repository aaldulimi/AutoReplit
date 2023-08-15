import click
import os
import json
import time 
from rich.console import Console
from auth import browser_login
from repl import Repl

@click.group()
def cli():
    pass


@click.command()
@click.option('-f', '--force', help="Ignore existing login and force login", default=False, is_flag=True)
def login(force):
    console = Console()

    if ".autoreplit.json" in os.listdir() and not force:
        with open(".autoreplit.json", "r") as json_file:
            data = json.load(json_file)
            if data["expire"] > time.time():
                console.print(f'[bold deep_sky_blue1]Already logged in as [white]{data["username"]}')
                return    
  
    browser_login()

@click.command()
def init():
    # TO DO: ignore .autoreplit.json, poetry.toml, poetry.lock, venv + any others that interfere with Replit's 
    repl = Repl(mount='./', packages=[])


cli.add_command(login)
cli.add_command(init)

if __name__ == '__main__':
    cli()
