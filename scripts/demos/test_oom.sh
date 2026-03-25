#!/bin/bash
AUTO=${AUTO:-0}
printf "\n\033[0;34m========================================================\033[0m\n"
printf "\033[0;34m🚨 Starting Redis OOM (Out of Memory) Demonstration\033[0m\n"
printf "\033[0;34m========================================================\033[0m\n\n"
printf "\033[1;33m[Step 1] Checking current memory configuration...\033[0m\n"
printf "Max Memory Limit: \033[0;32m"
docker exec redis-master redis-cli config get maxmemory | tail -n 1 | awk '{print $1/1024/1024 " MB"}'
printf "\033[0m\n"
printf "Eviction Policy: \033[0;32m"
docker exec redis-master redis-cli config get maxmemory-policy | tail -n 1
printf "\033[0m\n\n"
echo "👉 Press [ENTER] to start filling up memory (This will take a while)..."; if [ "$AUTO" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
printf "\n\033[1;33m[Step 2] Writing massive amounts of data to trigger OOM...\033[0m\n"
printf "We are writing 1MB strings continuously. Watch the memory usage grow!\n"
docker exec redis-master sh -c ' \
	echo "Starting data injection..."; \
	for i in $(seq 1 300); do \
		redis-cli SET "oom_key_$i" "$(head -c 1048576 /dev/urandom | tr -dc A-Za-z0-9 | head -c 1048576)" > /dev/null 2>&1; \
		if [ $((i % 50)) -eq 0 ]; then \
			echo "Written $i MB..."; \
			redis-cli info memory | grep used_memory_human; \
		fi; \
	done \
'
printf "\n\033[1;33m[Step 3] Memory is full! Let's check what happened...\033[0m\n"
printf "Current Memory Usage: \033[0;31m"
docker exec redis-master redis-cli info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r'
printf "\033[0m\n"
printf "Number of Evicted Keys (due to allkeys-lru): \033[0;31m"
docker exec redis-master redis-cli info stats | grep evicted_keys | cut -d: -f2 | tr -d '\r'
printf "\033[0m\n\n"
echo "👉 Press [ENTER] to try writing a new key now that memory is full..."; if [ "$AUTO" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
printf "\n\033[1;33m[Step 4] Attempting to write a new key...\033[0m\n"
printf "Executing: SET new_test_key \"This is a test\"\n"
docker exec redis-master redis-cli SET new_test_key "This is a test"
printf "\n\033[0;32m🎉 Demonstration Complete!\033[0m\n"
printf "Because we configured \033[0;36mallkeys-lru\033[0m, Redis didn't crash! It automatically deleted old keys to make room for new ones.\n"
printf "If the policy was \033[0;31mnoeviction\033[0m, the SET command above would have returned an OOM error.\n\n"
