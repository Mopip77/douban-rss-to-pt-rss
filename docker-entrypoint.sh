#!/bin/bash

touch rss.log

# inject env
tmpfile=$(mktemp)
cat <(env) CRON > $tmpfile

crontab $tmpfile
cron

tail -f rss.log