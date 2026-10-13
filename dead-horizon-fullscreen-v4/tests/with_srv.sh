#!/bin/bash
# usage: with_srv.sh <dir> <port> <cmd...>
d=$1; port=$2; shift 2
cd "$d" && (python3 -m http.server $port >/dev/null 2>&1 & echo $! >/tmp/srv.pid)
sleep 1.2
"$@"; rc=$?
kill $(cat /tmp/srv.pid) 2>/dev/null
exit $rc
