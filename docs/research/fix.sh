#!/bin/sh
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"
awk '$2!="200"{print $1}' verify.txt | while read -r id; do
  url=$(grep "^$id|" candidates.txt | cut -d'|' -f4)
  root=$(echo "$url" | sed -E 's#^(https?://[^/]+).*#\1#')
  html=$(curl -sL -A "$UA" -m 25 "$root/" 2>/dev/null)
  code=$(curl -sL -A "$UA" -o /dev/null -m 25 -w "%{http_code}" "$root/" 2>/dev/null)
  link=$(echo "$html" | grep -oiE 'href="[^"]*wedding[^"]*"' | head -1 | sed -E 's/href="//; s/"$//')
  echo "$id root=$code wedlink=$link"
done
