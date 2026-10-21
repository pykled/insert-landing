#!/bin/sh
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"
while IFS='|' read -r id type place url; do
  code=$(curl -sL -A "$UA" -o /dev/null -m 25 -w "%{http_code} %{url_effective}" "$url" 2>/dev/null)
  echo "$id $code"
done < candidates.txt
