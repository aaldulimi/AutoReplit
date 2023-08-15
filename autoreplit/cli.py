import click
import os
import json
import time 
from rich.console import Console
from auth import browser_login
from repl import Repl

IGNORE_FOLDERS = ['.venv', 'venv', '__pycache__']
IGNORE_FILES = ['.DS_Store']

@click.group()
def cli():
    pass

@click.command()
@click.option('-f', '--force', help="Ignore existing login and force login", default=False, is_flag=True)
def login(force):
    console = Console()

    config_file_path = '.autoreplit/config.json'
    if os.path.exists(config_file_path) and not force:
        with open(config_file_path, "r") as json_file:
            data = json.load(json_file)
            if data["expire"] > time.time():
                console.print(f'[bold deep_sky_blue1]Already logged in as [white]{data["username"]}')
                return
  
    browser_login()

@click.command()
@click.option('--ignore-folder', '-ifo', multiple=True, help='List of folders to ignore')
@click.option('--ignore-file', '-ifi', multiple=True, help='List of files to ignore')
def init(ignore_folder, ignore_file):
    ignore_folders = IGNORE_FOLDERS + list(ignore_folder)
    ignore_files = list(ignore_file)

    Repl(mount='./', mount_ignore={
        'folders': ignore_folders,
        'files': ignore_files
    })
 
cli.add_command(login)
cli.add_command(init)

if __name__ == '__main__':
    cli()
