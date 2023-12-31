import string
import random
import requests
import os
import json
import time
import re
import zipfile
import platform
import typing
import playwright.sync_api
from rich.console import Console
from rich.tree import Tree
from rich.live import Live

# TO DO: Better way to check Repl has finished booting up

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
BROWSER_HEADERS = {
    'authority': 'replit.com',
    'accept': '*/*',
    'accept-language': 'en-GB,en;q=0.5',
    'content-type': 'application/json',
    'origin': 'https://replit.com',
    'referer': 'https://replit.com/~',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': USER_AGENT,
    'x-forwarded-host': 'replit.com',
    'x-requested-with': 'XMLHttpRequest',
}

MOVE_TIME_PER_FILE_MS = 100
NEW_PAGE_WAIT_MS = 10000 
STANDARD_WAIT_MS = 1500

REPLIT_PYTHON_ORIGIN_ID = '8d4142a6-b4ad-4e1c-940b-15b99773aa04'
REPLIT_PYTHON_RELEASE_ID = 'fb9329ad-3e62-40c4-8951-e488fdb00ded'

class Repl():
    def __init__(self, mount: str, packages: typing.Optional[typing.List[str]] = None, private: bool = False,
                 mount_ignore: typing.Optional[typing.Dict[str, typing.List[str]]] = None):
        self.mount = mount
        self.mount_ignore = mount_ignore
        self.packages = packages
        self.private = private

        self.stdout = ''
       
        self._connect_sid = self._get_connect_sid()
        if self._connect_sid is None:
            return None
        
        self._user_agent = USER_AGENT
        self._headers = BROWSER_HEADERS
        self._api_cookies = {
            'connect.sid': self._connect_sid,
            'replit:authed': '1',
        }
        self._browser_cookies = self._generate_browser_cookies()

        # for terminal output
        self._console = Console()
        self._live = Live(console=self._console, refresh_per_second=4)
        self._live.start()
        
        # put the below in an init() method?
        self.repl_name = self._generate_temp_name()

        self.repl_url, self._repl_id = self._create_repl()
        if self.repl_url is None:
            return None
        
        self._browser_context = self._create_browser_context()
        if self.packages:
            self._packages_stdout = self._install_packages()

        self._mount_files()

        self._live.stop()
        self._console.print('Repl created successfully.')

    def _get_connect_sid(self):
        config_file_path = './.autoreplit/config.json'

        if os.path.exists(config_file_path):
            with open(config_file_path, "r") as json_file:
                data = json.load(json_file)
                if data["expire"] > time.time():
                    # potential edge case; key not found error 
                    return data["connect.sid"]
                
                self._console.print('Login expired. Login again by typing [bold]autoreplit login[/bold] in the terminal.')
                return None
        else:
            self._console.print('Login first by typing [bold]autoreplit login[/bold] in the terminal.')
            return None
    
    def _generate_browser_cookies(self) -> list:
        browser_cookies = []
        for k, v in self._api_cookies.items():
            browser_cookies.append({
                'name': k,
                'value': v,
                'path': '/',
                'domain': 'replit.com'
            })

        return browser_cookies

    def _generate_temp_name(self) -> str:
        characters = string.ascii_letters + string.digits
        repl_name = 'AR_' + ''.join(random.choice(characters) for _ in range(9))

        self._tree = Tree(f"[bold gold1]Repl: [white]{repl_name}")
        self._live.update(self._tree)

        return repl_name

    def _create_repl(self) -> typing.Optional[typing.Tuple[str, str]]:
        json_data = [
            {
                'operationName': 'CreateReplFormCreateRepl',
                'variables': {
                    'input': {
                        'title': self.repl_name,
                        'folderId': None,
                        'isPrivate': self.private,
                        'originId': REPLIT_PYTHON_ORIGIN_ID,
                        'replReleaseId': REPLIT_PYTHON_RELEASE_ID,
                    },
                    'isTitleAutoGenerated': False,
                },
                'query': 'mutation CreateReplFormCreateRepl($input: CreateReplInput!, $isTitleAutoGenerated: Boolean!) {\n  createRepl(input: $input, isTitleAutoGenerated: $isTitleAutoGenerated) {\n    ... on Repl {\n      ...CreateReplFormRepl\n      __typename\n    }\n    ... on UserError {\n      message\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CreateReplFormRepl on Repl {\n  id\n  ...TemplateSelector2Repl\n  __typename\n}\n\nfragment TemplateSelector2Repl on Repl {\n  id\n  url\n  title\n  iconUrl\n  templateLabel\n  nixedLanguage\n  isPrivate\n  isRenamed\n  language\n  likeCount\n  description(plainText: true)\n  deployment {\n    id\n    activeRelease {\n      id\n      __typename\n    }\n    __typename\n  }\n  owner {\n    ... on User {\n      id\n      username\n      __typename\n    }\n    ... on Team {\n      id\n      username\n      __typename\n    }\n    __typename\n  }\n  ...TemplateReplCardRepl\n  __typename\n}\n\nfragment TemplateReplCardRepl on Repl {\n  id\n  iconUrl\n  templateCategory\n  title\n  description(plainText: true)\n  releasesForkCount\n  templateLabel\n  likeCount\n  url\n  owner {\n    ... on User {\n      id\n      ...TemplateReplCardFooterUser\n      __typename\n    }\n    ... on Team {\n      id\n      ...TemplateReplCardFooterTeam\n      __typename\n    }\n    __typename\n  }\n  deployment {\n    id\n    activeRelease {\n      id\n      __typename\n    }\n    __typename\n  }\n  publishedAs\n  __typename\n}\n\nfragment TemplateReplCardFooterUser on User {\n  id\n  username\n  image\n  url\n  __typename\n}\n\nfragment TemplateReplCardFooterTeam on Team {\n  id\n  username\n  image\n  url\n  __typename\n}\n',
            },
        ]

        response = requests.post('https://replit.com/graphql', cookies=self._api_cookies, headers=self._headers, json=json_data).json()

        if response[0]['data']['createRepl']['__typename'] == "Repl":
            repl_id = response[0]['data']['createRepl']['id']
            repl_url = 'https://replit.com' + response[0]['data']['createRepl']['url']

            self._tree.add(repl_url)
            self._live.update(self._tree)

            return repl_url, repl_id
        
        self._console.print('Error creating repl. Please try again.', style="red")
        return None
    
    def _create_browser_context(self) -> playwright.sync_api.BrowserContext:
        p = playwright.sync_api.sync_playwright().start()
        browser = p.firefox.launch(headless=True)
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={ 'width': 1920, 'height': 1080},
            is_mobile=False,
        )
        context.add_cookies(self._browser_cookies)
        
        return context

    def _copy_repl_file_content(self, filename: str, page: playwright.sync_api.Page) -> str:
        page.goto(f'{self.repl_url}#{filename}')
        page.wait_for_timeout(NEW_PAGE_WAIT_MS)

        cm_line_elements = page.query_selector_all('div.cm-line')
        text_content = '\n'.join(cm_line.text_content() for cm_line in cm_line_elements)
        
        return text_content

    def _install_packages(self) -> str:
        self._tree.add("Installing packages")
        self._live.update(self._tree)

        install_command = f"""import os; os.system("poetry add {' '.join(self.packages)} > {self.repl_name}_log.txt 2>&1 ; touch {self.repl_name}_packages.txt ; sleep 10 ; rm -rf {self.repl_name}_packages.txt ; echo -n '' > main.py")"""

        page = self._browser_context.new_page()
        page.goto(self.repl_url)
        page.wait_for_timeout(NEW_PAGE_WAIT_MS)

        page.keyboard.type(install_command)
        page.keyboard.press("Enter")

        if platform.system() == "Darwin":
            page.keyboard.press("Meta+Enter")  
        else:
            page.keyboard.press("Control+Enter") 

        while not page.get_by_title(f'{self.repl_name}_packages.txt').is_visible():
            pass
        
        stdout = self._copy_repl_file_content(f'{self.repl_name}_log.txt', page)

        page.goto(f'{self.repl_url}#main.py')
        page.wait_for_timeout(NEW_PAGE_WAIT_MS)
        page.keyboard.type(f'import os; os.system("rm -rf {self.repl_name}_log.txt")')
        
        if platform.system() == "Darwin":
            page.keyboard.press("Meta+Enter")  
        else:
            page.keyboard.press("Control+Enter") 
    
        return stdout
    
    def _mount_files(self) -> None:
        self._tree.add(f"Mounting {self.mount}")
        self._live.update(self._tree)

        with zipfile.ZipFile(f'.autoreplit/{self.repl_name}.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.mount):
                if self.mount_ignore and 'folders' in self.mount_ignore:
                    if self.mount_ignore and any(ignore_dir in root for ignore_dir in self.mount_ignore['folders']):
                        continue

                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.mount)

                    if self.mount_ignore and 'files' in self.mount_ignore:
                        if any(ignore_file == rel_path for ignore_file in self.mount_ignore['files']):
                            continue

                    zipf.write(file_path, rel_path)

        page = self._browser_context.new_page()
        page.goto(self.repl_url)
        page.wait_for_timeout(NEW_PAGE_WAIT_MS)

        button = page.locator('[role="tab"] >> text=Shell')
        button.click()
        page.get_by_label("Shell").locator("div").filter(has_text=re.compile(r"^W$")).nth(2).click()
        page.keyboard.type('rm -rf main.py')
        page.keyboard.press("Enter")
        
        page.wait_for_timeout(STANDARD_WAIT_MS)
        
        input_element = page.locator('input[id^="file-upload-input-0."][type="file"]')
        input_element.set_input_files(f'.autoreplit/{self.repl_name}.zip') 
        page.wait_for_timeout(STANDARD_WAIT_MS)

        while page.query_selector("circle") is not None:
            pass
        
        page.wait_for_timeout(STANDARD_WAIT_MS)

        page.get_by_label("Shell").locator("div").filter(has_text=re.compile(r"^W$")).nth(2).click()
        page.keyboard.type(f"""python -c "import zipfile; zipfile.ZipFile('{self.repl_name}.zip', 'r').extractall()" ; rm -rf {self.repl_name}.zip""")
        page.keyboard.press("Enter")
        page.wait_for_timeout(STANDARD_WAIT_MS)

        os.remove(f'.autoreplit/{self.repl_name}.zip')

    def _close_main_tab(self, page: playwright.sync_api.Page) -> None:
        div_elements = page.query_selector_all("div")

        for div_element in div_elements:
            if "main.py" in div_element.text_content():
                close_button = div_element.wait_for_selector("button[aria-label='Close']")

                if close_button:
                    close_button.click()
                    break

    def run(self, command: str, timeout: int = 10) -> str:
        page = self._browser_context.new_page()
        page.goto(self.repl_url)
        page.wait_for_timeout(NEW_PAGE_WAIT_MS)

        full_command = f'{command} > {self.repl_name}_run_log.txt 2>&1 ; touch {self.repl_name}_run.txt ; sleep 5 ; rm -rf {self.repl_name}_run.txt'

        button = page.locator('[role="tab"] >> text=Shell')
        button.click()
        page.get_by_label("Shell").locator("div").filter(has_text=re.compile(r"^W$")).nth(2).click()
        page.keyboard.type(full_command)
        page.keyboard.press("Enter")
        self._console.print(f'[bold green]Running: [white]{command}')
        
        while not page.get_by_title(f'{self.repl_name}_run.txt').is_visible():
            pass
        
        self._close_main_tab(page)
        stdout = self._copy_repl_file_content(f'{self.repl_name}_run_log.txt', page)

        button = page.locator('[role="tab"] >> text=Shell')
        button.click()
        page.get_by_label("Shell").locator("div").filter(has_text=re.compile(r"^W$")).nth(2).click()

        page.keyboard.type(f'rm -rf {self.repl_name}_run_log.txt')
        page.keyboard.press("Enter")
        page.wait_for_timeout(STANDARD_WAIT_MS)

        self._console.print('Finished running command.')
    
        self.stdout += stdout
        return stdout
    
    def delete(self) -> bool:
        json_data = [
            {
                'operationName': 'ReplsDashboardDeleteRepl',
                'variables': {
                    'id': self._repl_id,
                },
                'query': 'mutation ReplsDashboardDeleteRepl($id: String!) {\n  deleteRepl(id: $id) {\n    id\n    __typename\n  }\n}\n',
            },
        ]

        response = requests.post('https://replit.com/graphql', cookies=self._api_cookies, headers=self._headers, json=json_data).json()

        if 'errors' in response[0]:
            self._console.print(f'[bold red]Error deleting repl.')
            return False

        self._console.print(f'[bold red]Repl deleted.')
        return True
