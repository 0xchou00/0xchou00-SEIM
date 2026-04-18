#!/usr/bin/env bash
set -euo pipefail

mkdir -p /shared-logs/nginx /run/sshd
touch /shared-logs/auth.log /shared-logs/nginx/access.log

rsyslogd
/usr/sbin/sshd

exec nginx -g 'daemon off;'
