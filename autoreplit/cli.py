import click
import os
import json
import time 
from auth import browser_login
from rich.console import Console

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
    

cli.add_command(login)

if __name__ == '__main__':
    cli()
