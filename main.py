#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
from requests.utils import requote_uri

import sys
import requests
import json
import re

CONFIG = {}

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        douban_rss_content = fetch_douban_rss()
        modifed_xml = inject_pt_rss_sites(douban_rss_content)
        self.send_response(200)
        self.send_header('Content-Type', 'text/xml; charset=utf-8')
        self.end_headers()
        self.wfile.write(bytes(modifed_xml, encoding='utf-8'))

def load_config():
    global CONFIG 
    CONFIG = json.load(open('config.json', 'r'))
    # config validate
    if 'douban-rss' not in CONFIG:
        raise SyntaxError("`douban-rss` is required in config file.")
    if 'pt-templates' not in CONFIG or type(CONFIG['pt-templates']) != list or len(CONFIG['pt-templates']) == 0:
        raise SyntaxError("`pt-templates` is required in config file, and at least one element.")

def fetch_douban_rss():
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    return requests.get(CONFIG['douban-rss'], headers=headers).text

def inject_pt_rss_sites(douban_rss_content):
    _douban_title_pattern = re.compile('^<title>(在看|想看|看过)(.*)</title>$')
    result = ""
    for part in re.split("(<title>.*?</title>)", douban_rss_content):
        result += part

        matcher = _douban_title_pattern.search(part)
        if matcher is None:
            continue

        title = matcher.group(2)
        # 将影片标题特殊字符转换成空格，再用pt的[和]方式进行搜索，防止因特殊字符造成搜索不出结果
        title = re.sub("[^0-9A-Za-z\u4e00-\u9fa5]", " ", title)
        for pt_template in CONFIG['pt-templates']:
            line = f"\n<{pt_template['name']}>{requote_uri(pt_template['template'].format(title))}</{pt_template['name']}>"
            line = line.replace("&amp;", "&").replace("&", "&amp;")
            result += line

    return result

if __name__ == '__main__':
    load_config()
    httpd = HTTPServer(('0.0.0.0', int(sys.argv[1])), SimpleHTTPRequestHandler)
    httpd.serve_forever()