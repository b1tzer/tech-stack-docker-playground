#!/bin/bash
AUTO=${AUTO:-0}
printf "\n\033[0;34m========================================================\033[0m\n"
printf "\033[0;34m👻 Starting Cache Penetration (缓存穿透) Demonstration\033[0m\n"
printf "\033[0;34m========================================================\033[0m\n\n"
printf "\033[1;33m[Concept] A malicious user requests a key that doesn't exist in Cache OR Database (e.g., user:-1).\033[0m\n\n"
echo "👉 Press [ENTER] to simulate the BAD practice..."; if [ "$AUTO" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
printf "\n\033[1;33m[Step 1] The BAD Practice: Doing nothing when DB returns empty...\033[0m\n"
printf "Request 1 for user:-1 -> Cache Miss! -> \033[0;31mQuerying Database (Heavy Load)...\033[0m -> DB returns empty.\n"
printf "Request 2 for user:-1 -> Cache Miss! -> \033[0;31mQuerying Database (Heavy Load)...\033[0m -> DB returns empty.\n"
printf "Request 3 for user:-1 -> Cache Miss! -> \033[0;31mQuerying Database (Heavy Load)...\033[0m -> DB returns empty.\n"
printf "💥 The cache is completely bypassed! The database takes all the hits.\n\n"
echo "👉 Press [ENTER] to simulate the GOOD practice (Caching empty results)..."; if [ "$AUTO" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
printf "\n\033[1;33m[Step 2] The GOOD Practice: Caching the empty result with a short TTL...\033[0m\n"
printf "Request 1 for user:-1 -> Cache Miss! -> Querying Database... -> DB returns empty.\n"
printf "Writing empty result to cache: \033[0;36mSET user:-1 \"<NULL>\" EX 60\033[0m\n"
docker exec redis-master redis-cli SET user:-1 "<NULL>" EX 60 > /dev/null
printf "\033[0;32m✔ Empty result cached.\033[0m\n\n"
printf "Request 2 for user:-1 -> \033[0;32mCache Hit! (Value: <NULL>)\033[0m -> Database is safe.\n"
printf "Request 3 for user:-1 -> \033[0;32mCache Hit! (Value: <NULL>)\033[0m -> Database is safe.\n"
printf "Checking cached value: \033[0;32m"
docker exec redis-master redis-cli GET user:-1 | tr -d '\r'
printf "\033[0m\n\n"
printf "🎉 The database is protected from repeated malicious queries!\n"
printf "(Note: For advanced protection, use a Bloom Filter before checking the cache).\n\n"
