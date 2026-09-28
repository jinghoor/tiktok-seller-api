run() { echo "########## $* ##########"; python3 tk01_finance.py "$@" 2>&1 | grep -vE "Deprecation|trace-deprecation|node:" | head -14; echo; }
run --shop tk89 order-list --status 2 --size 3
run --shop tk89 balance-detail --type 1 --limit 3
run --shop tk89 invoice
run --shop tk89 file-list
run --shop tk89 stat-info
run --shop tk01 settings
run --shop tk01 order-list --status 2 --size 3
run --shop tk01 oec-file-list
run --shop tk01 settlement-account
