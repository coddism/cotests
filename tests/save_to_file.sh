cd ..

dt=$(date '+%Y%m%d_%H%M%S')

python3 -m tests >> "$dt.log"
