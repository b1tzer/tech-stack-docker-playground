#!/bin/bash
AUTO=${AUTO:-0}
printf "\n\033[0;34m========================================================\033[0m\n"
printf "\033[0;34m🚀 Starting Redis Persistence (RDB/AOF) Demonstration\033[0m\n"
printf "\033[0;34m========================================================\033[0m\n\n"
printf "\033[1;33m[Step 1] Writing test data to Redis Master...\033[0m\n"
docker exec redis-master redis-cli SET persistence_test_key "Hello, Redis Persistence!"
printf "\033[0;32m✔ Data written successfully.\033[0m\n\n"
printf "\033[1;33m[Step 2] Verifying data exists in memory...\033[0m\n"
printf "Value in Redis: \033[0;32m"
docker exec redis-master redis-cli GET persistence_test_key | tr -d '\r'
printf "\033[0m\n\n"
printf "\033[1;33m[Step 3] Checking persistence files generated on the host...\033[0m\n"
printf "Listing contents of ./data/master/ directory:\n"
ls -lh data/master/ | grep -E "dump.rdb|appendonly" || echo "Files are being synced..."
printf "\n"
echo "👉 Press [ENTER] to simulate a complete cluster crash (docker-compose down)..."; if [ "$AUTO" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
printf "\n\033[0;31m💥 Stopping and removing all Redis containers...\033[0m\n"
docker-compose down
printf "\n\033[1;33m[Step 4] Cluster is down. Let's verify no containers are running...\033[0m\n"
docker ps | grep redis || printf "\033[0;32m✔ No Redis containers running.\033[0m\n"
printf "\n"
echo "👉 Press [ENTER] to restart the cluster and test data recovery..."; if [ "$AUTO" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
printf "\n\033[0;34m🔄 Starting the cluster again...\033[0m\n"
docker-compose up -d
printf "\n\033[1;33m[Step 5] Waiting for cluster to initialize (5 seconds)...\033[0m\n"
printf "\033[?25l"
for i in $(seq 5 -1 1); do \
	printf "\r\033[K\033[0;33m⏳ Waiting... %2d seconds remaining\033[0m" $i; \
	sleep 1; \
done
printf "\r\033[K\033[?25h"
printf "\n\033[1;33m[Step 6] Reading test data from Redis Master after restart...\033[0m\n"
printf "Value in Redis: \033[0;32m"
docker exec redis-master redis-cli GET persistence_test_key | tr -d '\r'
printf "\033[0m\n\n"
printf "\033[0;32m🎉 Demonstration Complete!\033[0m\n"
printf "If you saw 'Hello, Redis Persistence!' above, it means the data survived the crash thanks to AOF/RDB!\n\n"
