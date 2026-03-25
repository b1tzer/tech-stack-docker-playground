#!/bin/bash
AUTO=${AUTO:-0}
printf "\n\033[0;34m========================================================\033[0m\n"
printf "\033[0;34m❄️  Starting Cache Avalanche (缓存雪崩) Demonstration\033[0m\n"
printf "\033[0;34m========================================================\033[0m\n\n"
printf "\033[1;33m[Step 1] The BAD Practice: Setting 200 keys with the EXACT same TTL (15s)...\033[0m\n"
docker exec redis-master sh -c 'for i in $(seq 1 200); do echo "SET bad_key:$i \"value\" EX 15"; done | redis-cli --pipe > /dev/null 2>&1'
printf "\033[0;32m✔ 200 keys created with exactly 15s expiration.\033[0m\n\n"
echo "👉 Press [ENTER] to watch the Live TTL Dashboard..."; if [ "$AUTO" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
printf "\n\033[0;36mLive TTL Dashboard (200 Keys - Bad Practice):\033[0m\n"
for i in $(seq 1 10); do echo ""; done
printf "\033[?25l"
for step in $(seq 1 32); do \
	printf "\033[10A"; \
	docker exec redis-master redis-cli --raw EVAL "local ttls={}; for i=1,200 do table.insert(ttls, redis.call('TTL', ARGV[1]..':'..i)) end; return ttls" 0 "bad_key" | \
	awk '{ \
		gsub(/\r/, "", $1); \
		if ($1 == -2) val = "\033[0;31m -\033[0m"; \
		else if ($1 <= 5) val = sprintf("\033[1;31m%2d\033[0m", $1); \
		else if ($1 <= 10) val = sprintf("\033[1;33m%2d\033[0m", $1); \
		else val = sprintf("\033[1;32m%2d\033[0m", $1); \
		if (NR % 20 == 0) printf "%s\n", val; \
		else printf "%s ", val; \
	}'; \
	sleep 0.5; \
done
printf "\033[?25h"
printf "\n💥 \033[0;31mAll keys expired simultaneously! If these were hot data, your database would be crushed right now.\033[0m\n\n"
echo "👉 Press [ENTER] to simulate the GOOD practice (Adding random jitter)..."; if [ "$AUTO" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
printf "\n\033[1;33m[Step 2] The GOOD Practice: Adding random jitter to TTLs (10s + random 0-10s)...\033[0m\n"
docker exec redis-master sh -c 'for i in $(seq 1 200); do jitter=$((RANDOM % 11)); echo "SET good_key:$i \"value\" EX $((10 + jitter))"; done | redis-cli --pipe > /dev/null 2>&1'
printf "\033[0;32m✔ 200 keys created with 10s~20s expiration.\033[0m\n\n"
echo "👉 Press [ENTER] to watch the Live TTL Dashboard..."; if [ "$AUTO" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
printf "\n\033[0;36mLive TTL Dashboard (200 Keys - Good Practice):\033[0m\n"
for i in $(seq 1 10); do echo ""; done
printf "\033[?25l"
for step in $(seq 1 42); do \
	printf "\033[10A"; \
	docker exec redis-master redis-cli --raw EVAL "local ttls={}; for i=1,200 do table.insert(ttls, redis.call('TTL', ARGV[1]..':'..i)) end; return ttls" 0 "good_key" | \
	awk '{ \
		gsub(/\r/, "", $1); \
		if ($1 == -2) val = "\033[0;31m -\033[0m"; \
		else if ($1 <= 5) val = sprintf("\033[1;31m%2d\033[0m", $1); \
		else if ($1 <= 10) val = sprintf("\033[1;33m%2d\033[0m", $1); \
		else val = sprintf("\033[1;32m%2d\033[0m", $1); \
		if (NR % 20 == 0) printf "%s\n", val; \
		else printf "%s ", val; \
	}'; \
	sleep 0.5; \
done
printf "\033[?25h"
printf "\n🎉 \033[0;32mKeys are expiring gradually! The database load is smoothed out.\033[0m\n\n"
