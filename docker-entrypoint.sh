#!/bin/bash

touch rss.log

# inject env
tmpfile=$(mktemp)
cat <(env) config/CRON > $tmpfile

crontab $tmpfile
cron

tail -f rss.log
