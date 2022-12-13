#!/bin/bash

touch rss.log

crontab CRON
cron

tail -f rss.log