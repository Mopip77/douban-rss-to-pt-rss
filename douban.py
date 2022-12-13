#!/usr/bin/env python3
import requests
import re
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def crawl_douban_rss(user_id: str) -> str:
    """crawl douban user activation rss content

    Args:
        user_id (str): user id

    Returns:
        str: rss raw xml content
    """
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    return requests.get(f"https://www.douban.com/feed/people/{user_id}/interests", headers=headers).text

def parse_douban_rss(rss_xml_content: str) -> list[str]:
    """parse douban rss content, return .

    Args:
        rss_xml_content (str): 

    Returns:
        list[str]: wanna watching title list.
    """
    
    _douban_title_pattern = re.compile('<title>(在看|想看|看过)(.*?)</title>')
    result = []
    for action, title in _douban_title_pattern.findall(rss_xml_content):
        if action == '想看':
            result.append(title)
            logging.info(f"想看 [{title}]")
    return result