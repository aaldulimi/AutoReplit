import json
import re
from datetime import datetime
import requests
import playwright.sync_api 
from rich.console import Console
import os

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

def get_username() -> str:
    with open(".autoreplit/config.json", "r") as json_file:
        replit_tools_data = json.load(json_file)
        connect_sid_value = replit_tools_data["connect.sid"]

    cookies = {
        'connect.sid': connect_sid_value,
        'replit:authed': '1',
    }

    json_data = {
        'operationName': 'ManageAccountStorageUtilizationCurrentUser',
        'variables': {},
        'query': 'query ManageAccountStorageUtilizationCurrentUser {\n  currentUser {\n    __typename\n    id\n    username\n    userSubscriptionType\n    userPowerUpsByType {\n      ... on UserError {\n        __typename\n        message\n      }\n      ... on UnauthorizedError {\n        __typename\n        message\n      }\n      ... on UserPowerUpsTypes {\n        __typename\n        storage {\n          __typename\n          currentSku\n        }\n      }\n      __typename\n    }\n    storageInfo {\n      __typename\n      storageQuota {\n        ... on StorageQuota {\n          __typename\n          quota\n        }\n        __typename\n      }\n      storageGracePeriodQuota {\n        ... on StorageGracePeriodQuota {\n          __typename\n          quota\n        }\n        __typename\n      }\n      storageQuotaStatus2 {\n        ... on StorageQuotaStatus {\n          __typename\n          status\n        }\n        ... on ServiceUnavailable {\n          __typename\n          message\n        }\n        __typename\n      }\n      accountStorageUtilization {\n        ...AccountStorageUtilization\n        ... on UnauthorizedError {\n          __typename\n          message\n        }\n        __typename\n      }\n    }\n  }\n}\n\nfragment AccountStorageUtilization on AccountStorageUtilization {\n  __typename\n  total\n  perRepl {\n    __typename\n    usage\n    percentage\n    repl {\n      __typename\n      id\n      slug\n      url\n      title\n      nextPagePathname\n      iconUrl\n    }\n  }\n}\n',
    }

    response = requests.post('https://replit.com/graphql', cookies=cookies, headers=BROWSER_HEADERS, json=json_data).json() 
    username = response['data']['currentUser']['username']

    replit_tools_data['username'] = username
    with open(".autoreplit/config.json", "w") as json_file:
        json.dump(replit_tools_data, json_file)

    return username

def on_response(response: requests.Response) -> None:
    if response.url == 'https://replit.com/login':
        set_cookie_header = response.headers.get('set-cookie', '')
        match = re.search(r'connect\.sid=([^;]+)', set_cookie_header)
    
        if match:
            connect_sid_value = match.group(1)

            expiry_match = re.search(r'Expires=([^;]+)', set_cookie_header)
            expiry_date_str = expiry_match.group(1)
            date_format = "%a, %d %b %Y %H:%M:%S %Z"
            expire_timestamp = datetime.strptime(expiry_date_str, date_format).timestamp()

            with open(".autoreplit/config.json", "w") as json_file:
                json.dump({"connect.sid": connect_sid_value,
                        "expire": expire_timestamp}, json_file)

def mk_config() -> None:
    config_dir = '.autoreplit'
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

def browser_login() -> str:
    mk_config()

    console = Console()
    with playwright.sync_api.sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.on("response", on_response)
        page.goto("https://replit.com/login")
        page.wait_for_url("https://replit.com/~")

        context.close()
    
        username = get_username()

    console.print(f'[bold deep_sky_blue1]Logged in as [white]{username}')
    return username
