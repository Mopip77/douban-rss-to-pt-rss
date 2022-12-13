#!/bin/bash

touch rss.log

# generate config files
mkdir -p "config"

if [ ! -e "config/CRON" ]; then
  cat > config/CRON <<EOF
*/5 8-23 * * * cd /app && /usr/local/bin/python3 /app/main.py >> /app/rss.log 2>&1
0 0-7 * * * cd /app && /usr/local/bin/python3 /app/main.py >> /app/rss.log 2>&1

EOF
fi

if [ ! -e "config/sites.json" ]; then
  cat > config/sites.json <<EOF
{
    "tjupt": "https://tjupt.org/torrentrss.php?rows={size}&isize=1&search={query}&passkey={passkey}&linktype=dl",
    "mteam": "https://pt.m-team.cc/torrentrss.php?rows={size}&isize=1&search={query}&passkey={passkey}&linktype=dl"
}
EOF
fi

# inject env
tmpfile=$(mktemp)
cat <(env) config/CRON > $tmpfile

crontab $tmpfile
cron

tail -f rss.log
