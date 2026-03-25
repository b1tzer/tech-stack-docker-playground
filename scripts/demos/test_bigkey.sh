#!/bin/bash
AUTO=${AUTO:-0}
printf "\n\033[0;34m========================================================\033[0m\n"
printf "\033[0;34m🐘 Starting Redis Big Key Demonstration\033[0m\n"
printf "\033[0;34m========================================================\033[0m\n\n"
printf "\033[1;33m[Step 1] Creating a Big Key (Hash with 100,000 fields)...\033[0m\n"
printf "This might take a few seconds...\n"
docker exec redis-master sh -c 'for i in $(seq 1 100000); do echo "HSET my_big_hash field$i value$i"; done | redis-cli --pipe > /dev/null 2>&1'
printf "\033[0;32m✔ Big Key 'my_big_hash' created successfully.\033[0m\n\n"
printf "\033[1;33m[Step 2] Checking the size of the Big Key...\033[0m\n"
printf "Number of fields in 'my_big_hash': \033[0;32m"
docker exec redis-master redis-cli HLEN my_big_hash | tr -d '\r'
printf "\033[0m\n"
printf "Memory usage of 'my_big_hash': \033[0;32m"
docker exec redis-master redis-cli MEMORY USAGE my_big_hash | awk '{print $1/1024/1024 " MB"}'
printf "\033[0m\n\n"
echo "👉 Press [ENTER] to simulate the BAD practice (using DEL on a Big Key)..."; if [ "$AUTO" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
printf "\n\033[0;31m💥 Executing DEL my_big_hash (This blocks Redis!)...\033[0m\n"
printf "Time taken to execute DEL: \033[0;31m"
docker exec redis-master sh -c 'time redis-cli DEL my_big_hash > /dev/null' 2>&1 | grep real | awk '{print $2}'
printf "\033[0m\n"
printf "Notice how long it took? During this time, Redis couldn't process ANY other commands!\n\n"
echo "👉 Press [ENTER] to recreate the Big Key and simulate the GOOD practice (using UNLINK)..."; if [ "$AUTO" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
printf "\n\033[1;33m[Step 3] Recreating the Big Key...\033[0m\n"
docker exec redis-master sh -c 'for i in $(seq 1 100000); do echo "HSET my_big_hash field$i value$i"; done | redis-cli --pipe > /dev/null 2>&1'
printf "\033[0;32m✔ Big Key recreated.\033[0m\n\n"
printf "\033[0;32m✨ Executing UNLINK my_big_hash (Asynchronous deletion, non-blocking!)...\033[0m\n"
printf "Time taken to execute UNLINK: \033[0;32m"
docker exec redis-master sh -c 'time redis-cli UNLINK my_big_hash > /dev/null' 2>&1 | grep real | awk '{print $2}'
printf "\033[0m\n\n"
printf "\033[0;32m🎉 Demonstration Complete!\033[0m\n"
printf "See the difference? UNLINK returns almost instantly because it deletes the memory in a background thread.\n"
printf "Always use \033[0;36mUNLINK\033[0m instead of \033[0;31mDEL\033[0m for large keys!\n\n"
