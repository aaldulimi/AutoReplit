# AutoReplit 
Automate deployment to Replit in a couple of lines of Python. This is a fun project to make for the people at Replit to see. Don't abuse it.

## Installation
Firstly clone the repo using `git clone https://github.com/aaldulimi/AutoReplit.git` and `cd` into the root directory. Then install the dependencies in the `pyproject.toml` file or `requirements.txt`. Finally install the firefox browser for playwright using `playwright install firefox`.

## Usage
AutoReplit works 8/10 times. If it keeps stalling (depends on your internet speed), increase the `*_MS` constants at the top of `autoreplit/repl.py` file. 

Check the `example.py` (it works!), but this is pretty much it:
```
from autoreplit import Repl, browser_login

browser_login()

repl = Repl(mount='agent/', packages=['requests'])
output = repl.run('python main.py')
repl.delete()
```

### CLI 
To login via web browser:
```
python autoreplit/cli.py login
```

To upload current directory to Replit
```
python autoreplit/cli.py init --ignore-file .env --ignore-folder .autoreplit
```
- Folders that are already ignored: `venv .venv __pycache__`
- Files that are already ignored: `.DS_Store`


#### This is basiccaly my job application for Replit.