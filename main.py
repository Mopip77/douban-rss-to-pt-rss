#!/usr/bin/env python3
import os
import douban
import logging
import qbittorrent
import sites
import re

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

DEFAULT_TITLE = "_"
LAST_RECORD_TITLE_FILE = "last_record_title"
PT_SITES = set([x.strip() for x in os.getenv('SITES').split(",")])

def handle_title(title: str):
    """convert title to rss subscription url, and send to qbittorrent

    Args:
        title (str): movie title
    """
    site_map = sites.load_sites()
    # pre-handle, remove the puntuation for better match
    pre_handled_title = re.sub("[^0-9A-Za-z\u4e00-\u9fa5]", " ", title)
    for site in PT_SITES:
        if site not in site_map:
            logging.warning(f"<{site}> 还不支持，跳过")
        else:
            url = site_map[site].format(query=pre_handled_title, size=10, passkey=os.getenv(f"{site}_passkey"))
            # send to qb
            qbittorrent.add_folder(site)
            qbittorrent.add_rss(url, f"{site}\\{title}")

def main():
    douban_rss_content = douban.crawl_douban_rss(os.environ.get('DOUBAN_USER_ID'))
    wanna_watch_titles = douban.parse_douban_rss(douban_rss_content)
    # load last record title
    if not os.path.exists(LAST_RECORD_TITLE_FILE):
        # first run, do not handle the previous titles
        last_record_title = DEFAULT_TITLE
    else:
        last_record_title = open(LAST_RECORD_TITLE_FILE, 'r').readline()
        logging.info(f"上次处理到 [{last_record_title}]")
    
    handled = False
    for title in wanna_watch_titles:
        if not handled and last_record_title != title:
            logging.info(f"正在发送 [{title}] 在 <{os.environ.get('PT')}> 的rss链接到qb")
            handle_title(title)
        else:
            logging.info(f"跳过 [{title}] ，之前已被处理")
            handled = True
    # save the newest title to file
    with open(LAST_RECORD_TITLE_FILE, 'w') as ff:
        newest_title = wanna_watch_titles[0] if len(wanna_watch_titles) > 0 else last_record_title
        ff.write(newest_title)
            
if __name__ == '__main__':
    main()