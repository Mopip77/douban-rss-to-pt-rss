import requests
import os
import logging

logging.basicConfig(format='[qb] %(asctime)s - %(message)s', level=logging.INFO)

COOKIE = None

def authenticate():
    """qb authentication, set `COOKIE`
    """
    global COOKIE
    if COOKIE is None:
        data = {
            "username": os.getenv('QB_USER'),
            "password": os.getenv('QB_PWD')
        }
        COOKIE = requests.get(f"{os.getenv('QB_URL')}/api/v2/auth/login", data=data).cookies

def add_folder(folder: str):
    authenticate()
    data = {
        "path": folder
    }
    resp = requests.post(f"{os.getenv('QB_URL')}/api/v2/rss/addFolder", data=data, cookies=COOKIE)
    if resp.status_code != 200 and 'already exists' not in resp.text:
        logging.error(f"添加rss到qb失败, 返回值: {resp.text}")
    else:
        logging.info(f"成功添加rss文件夹 [{folder}]")

def add_rss(rss_url: str, path: str):
    """add rss subscription

    Args:
        rss_url (str): rss url
        path (str): rss subscription path
    """
    authenticate()
    data = {
        "url": rss_url,
        "path": path
    }
    resp = requests.post(f"{os.getenv('QB_URL')}/api/v2/rss/addFeed", data=data, cookies=COOKIE)
    if resp.status_code != 200:
        logging.error(f"添加rss到qb失败, 返回值: {resp.text}")