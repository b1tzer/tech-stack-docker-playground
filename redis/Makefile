.PHONY: start stop clean logs status cli-master cli-slave test-failover test-persistence test-bigkey test-oom test-avalanche test-penetration

# Auto-execute parameter for tests (set to 1 to skip manual prompts)
AUTO ?= 0

# Start the Redis cluster
start:
	@echo "Starting Redis Master-Slave-Sentinel cluster..."
	docker-compose up -d
	@echo "Cluster started. Redis Commander available at http://localhost:8081"

# Stop the Redis cluster
stop:
	@echo "Stopping Redis cluster..."
	docker-compose down

# Stop and remove all data
clean:
	@echo "Stopping cluster and removing data volumes..."
	docker-compose down -v
	sudo rm -rf data/master/* data/slave/* data/slave2/*
	@echo "Clean complete."

# View logs
logs:
	docker-compose logs -f

# Check status
status:
	@docker-compose ps
	@printf "\n\033[1;33m--- Master Replication Status ---\033[0m\n"
	@docker exec redis-master redis-cli info replication | grep -E 'role|connected_slaves|master_repl_offset' || echo "Master is down"
	@printf "\n\033[1;33m--- Slave 1 Replication Status ---\033[0m\n"
	@docker exec redis-slave redis-cli info replication | grep -E 'role|master_host|master_link_status|slave_repl_offset' || echo "Slave 1 is down"
	@printf "\n\033[1;33m--- Slave 2 Replication Status ---\033[0m\n"
	@docker exec redis-slave2 redis-cli info replication | grep -E 'role|master_host|master_link_status|slave_repl_offset' || echo "Slave 2 is down"
	@printf "\n\033[1;33m--- Sentinel Status ---\033[0m\n"
	@docker exec redis-sentinel-1 redis-cli -p 26379 info sentinel | grep status
	@printf "\n"

# Connect to Master CLI
cli-master:
	docker exec -it redis-master redis-cli

# Connect to Slave CLI
cli-slave:
	docker exec -it redis-slave redis-cli

# Test Failover Scenario
test-failover:
	@printf "\n\033[0;34m========================================================\033[0m\n"
	@printf "\033[0;34m🛡️  Starting Redis Sentinel Failover Demonstration\033[0m\n"
	@printf "\033[0;34m========================================================\033[0m\n\n"
	@printf "\033[1;33m[Step 1] Current Cluster Topology:\033[0m\n"
	@M_ROLE=$$(docker exec redis-master redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
	 S1_ROLE=$$(docker exec redis-slave redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
	 S2_ROLE=$$(docker exec redis-slave2 redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
	 printf "\n           [ 👑 \033[1;32mredis-master\033[0m ($$M_ROLE) ]\n" ; \
	 printf "             /                      \\\n" ; \
	 printf "[ 🛡️ \033[1;36mredis-slave\033[0m ($$S1_ROLE) ]  [ 🛡️ \033[1;36mredis-slave2\033[0m ($$S2_ROLE) ]\n\n"
	@echo "👉 Press [ENTER] to simulate Master failure (docker pause redis-master)..."; if [ "$(AUTO)" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
	@printf "\n\033[0;31m💥 Pausing redis-master (simulating network partition/hang)...\033[0m\n"
	@docker pause redis-master > /dev/null 2>&1 || true
	@printf "\n           [ ❌ \033[1;31mredis-master\033[0m (down) ]\n"
	@printf "             /                      \\\n"
	@printf "[ 🛡️ \033[1;36mredis-slave\033[0m (slave) ]  [ 🛡️ \033[1;36mredis-slave2\033[0m (slave) ]\n\n"
	@printf "\033[1;33m[Step 2] Sentinels detecting failure and voting...\033[0m\n"
	@printf "\033[?25l"
	@for i in $$(seq 1 25); do \
		printf "\r\033[K\033[0;33m👀 Sentinels observing and negotiating... %2d seconds\033[0m" $$i; \
		sleep 1; \
	done
	@printf "\r\033[K\033[?25h"
	@printf "\n\033[1;33m[Step 3] Sentinel Decision Log (Highlights):\033[0m\n"
	@docker logs redis-sentinel-1 --since 30s | grep -E "sdown|odown|vote-for-leader|switch-master" | sed 's/^/  /' || echo "  (No logs found, maybe still deciding?)"
	@printf "\n\033[1;33m[Step 4] Live Cluster Topology (Updating for 15s):\033[0m\n"
	@printf "\n\n\n\n"
	@printf "\033[?25l"
	@for i in $$(seq 1 15); do \
		printf "\033[4A"; \
		S1_ROLE=$$(docker exec redis-slave redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
		S2_ROLE=$$(docker exec redis-slave2 redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
		if [ "$$S1_ROLE" = "master" ]; then \
			printf "           [ ❌ \033[1;31mredis-master\033[0m (down) ]\033[K\n" ; \
			printf "             /                      \\\033[K\n" ; \
			printf "[ 👑 \033[1;32mredis-slave\033[0m (master) ] [ 🛡️ \033[1;36mredis-slave2\033[0m ($$S2_ROLE) ]\033[K\n\n" ; \
		elif [ "$$S2_ROLE" = "master" ]; then \
			printf "           [ ❌ \033[1;31mredis-master\033[0m (down) ]\033[K\n" ; \
			printf "             /                      \\\033[K\n" ; \
			printf "[ 🛡️ \033[1;36mredis-slave\033[0m ($$S1_ROLE) ]  [ 👑 \033[1;32mredis-slave2\033[0m (master) ]\033[K\n\n" ; \
		else \
			printf "           [ ❌ \033[1;31mredis-master\033[0m (down) ]\033[K\n" ; \
			printf "             /                      \\\033[K\n" ; \
			printf "[ 🛡️ \033[1;36mredis-slave\033[0m ($$S1_ROLE) ]  [ 🛡️ \033[1;36mredis-slave2\033[0m ($$S2_ROLE) ]\033[K\n" ; \
			printf "  ⚠️  Failover in progress... ($$i/15s)\033[K\n" ; \
		fi; \
		sleep 1; \
	done
	@printf "\033[?25h"
	@echo "👉 Press [ENTER] to unpause the old master and see it join as a slave..."; if [ "$(AUTO)" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
	@printf "\n\033[0;34m🔄 Unpausing redis-master...\033[0m\n"
	@docker unpause redis-master > /dev/null 2>&1 || true
	@printf "\033[?25l"
	@for i in $$(seq 1 5); do \
		printf "\r\033[K\033[0;33m⏳ Waiting for old master to sync... %2d seconds\033[0m" $$i; \
		sleep 1; \
	done
	@printf "\r\033[K\033[?25h"
	@printf "\n\033[1;33m[Step 5] Final Cluster Topology:\033[0m\n"
	@M_ROLE=$$(docker exec redis-master redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
	 S1_ROLE=$$(docker exec redis-slave redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
	 S2_ROLE=$$(docker exec redis-slave2 redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
	 if [ "$$S1_ROLE" = "master" ]; then \
	 	printf "\n           [ 🛡️ \033[1;36mredis-master\033[0m ($$M_ROLE) ]\n" ; \
	 	printf "             /                      \\\n" ; \
	 	printf "[ 👑 \033[1;32mredis-slave\033[0m (master) ] [ 🛡️ \033[1;36mredis-slave2\033[0m ($$S2_ROLE) ]\n\n" ; \
	 elif [ "$$S2_ROLE" = "master" ]; then \
	 	printf "\n           [ 🛡️ \033[1;36mredis-master\033[0m ($$M_ROLE) ]\n" ; \
	 	printf "             /                      \\\n" ; \
	 	printf "[ 🛡️ \033[1;36mredis-slave\033[0m ($$S1_ROLE) ]  [ 👑 \033[1;32mredis-slave2\033[0m (master) ]\n\n" ; \
	 else \
	 	printf "\n           [ 👑 \033[1;32mredis-master\033[0m ($$M_ROLE) ]\n" ; \
	 	printf "             /                      \\\n" ; \
	 	printf "[ 🛡️ \033[1;36mredis-slave\033[0m ($$S1_ROLE) ]  [ 🛡️ \033[1;36mredis-slave2\033[0m ($$S2_ROLE) ]\n\n" ; \
	 fi
	@printf "\033[0;32m🎉 Failover Demonstration Complete!\033[0m\n\n"

# Test Persistence Scenario
test-persistence:
	@printf "\n\033[0;34m========================================================\033[0m\n"
	@printf "\033[0;34m🚀 Starting Redis Persistence (RDB/AOF) Demonstration\033[0m\n"
	@printf "\033[0;34m========================================================\033[0m\n\n"
	@printf "\033[1;33m[Step 1] Writing test data to Redis Master...\033[0m\n"
	@docker exec redis-master redis-cli SET persistence_test_key "Hello, Redis Persistence!"
	@printf "\033[0;32m✔ Data written successfully.\033[0m\n\n"
	@printf "\033[1;33m[Step 2] Verifying data exists in memory...\033[0m\n"
	@printf "Value in Redis: \033[0;32m"
	@docker exec redis-master redis-cli GET persistence_test_key | tr -d '\r'
	@printf "\033[0m\n\n"
	@printf "\033[1;33m[Step 3] Checking persistence files generated on the host...\033[0m\n"
	@printf "Listing contents of ./data/master/ directory:\n"
	@ls -lh data/master/ | grep -E "dump.rdb|appendonly" || echo "Files are being synced..."
	@printf "\n"
	@echo "👉 Press [ENTER] to simulate a complete cluster crash (docker-compose down)..."; if [ "$(AUTO)" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
	@printf "\n\033[0;31m💥 Stopping and removing all Redis containers...\033[0m\n"
	@docker-compose down
	@printf "\n\033[1;33m[Step 4] Cluster is down. Let's verify no containers are running...\033[0m\n"
	@docker ps | grep redis || printf "\033[0;32m✔ No Redis containers running.\033[0m\n"
	@printf "\n"
	@echo "👉 Press [ENTER] to restart the cluster and test data recovery..."; if [ "$(AUTO)" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
	@printf "\n\033[0;34m🔄 Starting the cluster again...\033[0m\n"
	@docker-compose up -d
	@printf "\n\033[1;33m[Step 5] Waiting for cluster to initialize (5 seconds)...\033[0m\n"
	@printf "\033[?25l"
	@for i in $$(seq 5 -1 1); do \
		printf "\r\033[K\033[0;33m⏳ Waiting... %2d seconds remaining\033[0m" $$i; \
		sleep 1; \
	done
	@printf "\r\033[K\033[?25h"
	@printf "\n\033[1;33m[Step 6] Reading test data from Redis Master after restart...\033[0m\n"
	@printf "Value in Redis: \033[0;32m"
	@docker exec redis-master redis-cli GET persistence_test_key | tr -d '\r'
	@printf "\033[0m\n\n"
	@printf "\033[0;32m🎉 Demonstration Complete!\033[0m\n"
	@printf "If you saw 'Hello, Redis Persistence!' above, it means the data survived the crash thanks to AOF/RDB!\n\n"

# Test Big Key Scenario
test-bigkey:
	@printf "\n\033[0;34m========================================================\033[0m\n"
	@printf "\033[0;34m🐘 Starting Redis Big Key Demonstration\033[0m\n"
	@printf "\033[0;34m========================================================\033[0m\n\n"
	@printf "\033[1;33m[Step 1] Creating a Big Key (Hash with 100,000 fields)...\033[0m\n"
	@printf "This might take a few seconds...\n"
	@docker exec redis-master sh -c 'for i in $$(seq 1 100000); do echo "HSET my_big_hash field$$i value$$i"; done | redis-cli --pipe > /dev/null 2>&1'
	@printf "\033[0;32m✔ Big Key 'my_big_hash' created successfully.\033[0m\n\n"
	@printf "\033[1;33m[Step 2] Checking the size of the Big Key...\033[0m\n"
	@printf "Number of fields in 'my_big_hash': \033[0;32m"
	@docker exec redis-master redis-cli HLEN my_big_hash | tr -d '\r'
	@printf "\033[0m\n"
	@printf "Memory usage of 'my_big_hash': \033[0;32m"
	@docker exec redis-master redis-cli MEMORY USAGE my_big_hash | awk '{print $$1/1024/1024 " MB"}'
	@printf "\033[0m\n\n"
	@echo "👉 Press [ENTER] to simulate the BAD practice (using DEL on a Big Key)..."; if [ "$(AUTO)" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
	@printf "\n\033[0;31m💥 Executing DEL my_big_hash (This blocks Redis!)...\033[0m\n"
	@printf "Time taken to execute DEL: \033[0;31m"
	@docker exec redis-master sh -c 'time redis-cli DEL my_big_hash > /dev/null' 2>&1 | grep real | awk '{print $$2}'
	@printf "\033[0m\n"
	@printf "Notice how long it took? During this time, Redis couldn't process ANY other commands!\n\n"
	@echo "👉 Press [ENTER] to recreate the Big Key and simulate the GOOD practice (using UNLINK)..."; if [ "$(AUTO)" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
	@printf "\n\033[1;33m[Step 3] Recreating the Big Key...\033[0m\n"
	@docker exec redis-master sh -c 'for i in $$(seq 1 100000); do echo "HSET my_big_hash field$$i value$$i"; done | redis-cli --pipe > /dev/null 2>&1'
	@printf "\033[0;32m✔ Big Key recreated.\033[0m\n\n"
	@printf "\033[0;32m✨ Executing UNLINK my_big_hash (Asynchronous deletion, non-blocking!)...\033[0m\n"
	@printf "Time taken to execute UNLINK: \033[0;32m"
	@docker exec redis-master sh -c 'time redis-cli UNLINK my_big_hash > /dev/null' 2>&1 | grep real | awk '{print $$2}'
	@printf "\033[0m\n\n"
	@printf "\033[0;32m🎉 Demonstration Complete!\033[0m\n"
	@printf "See the difference? UNLINK returns almost instantly because it deletes the memory in a background thread.\n"
	@printf "Always use \033[0;36mUNLINK\033[0m instead of \033[0;31mDEL\033[0m for large keys!\n\n"

# Test OOM (Out of Memory) Scenario
test-oom:
	@printf "\n\033[0;34m========================================================\033[0m\n"
	@printf "\033[0;34m🚨 Starting Redis OOM (Out of Memory) Demonstration\033[0m\n"
	@printf "\033[0;34m========================================================\033[0m\n\n"
	@printf "\033[1;33m[Step 1] Checking current memory configuration...\033[0m\n"
	@printf "Max Memory Limit: \033[0;32m"
	@docker exec redis-master redis-cli config get maxmemory | tail -n 1 | awk '{print $$1/1024/1024 " MB"}'
	@printf "\033[0m\n"
	@printf "Eviction Policy: \033[0;32m"
	@docker exec redis-master redis-cli config get maxmemory-policy | tail -n 1
	@printf "\033[0m\n\n"
	@echo "👉 Press [ENTER] to start filling up memory (This will take a while)..."; if [ "$(AUTO)" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
	@printf "\n\033[1;33m[Step 2] Writing massive amounts of data to trigger OOM...\033[0m\n"
	@printf "We are writing 1MB strings continuously. Watch the memory usage grow!\n"
	@docker exec redis-master sh -c ' \
		echo "Starting data injection..."; \
		for i in $$(seq 1 300); do \
			redis-cli SET "oom_key_$$i" "$$(head -c 1048576 /dev/urandom | tr -dc A-Za-z0-9 | head -c 1048576)" > /dev/null 2>&1; \
			if [ $$((i % 50)) -eq 0 ]; then \
				echo "Written $$i MB..."; \
				redis-cli info memory | grep used_memory_human; \
			fi; \
		done \
	'
	@printf "\n\033[1;33m[Step 3] Memory is full! Let's check what happened...\033[0m\n"
	@printf "Current Memory Usage: \033[0;31m"
	@docker exec redis-master redis-cli info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r'
	@printf "\033[0m\n"
	@printf "Number of Evicted Keys (due to allkeys-lru): \033[0;31m"
	@docker exec redis-master redis-cli info stats | grep evicted_keys | cut -d: -f2 | tr -d '\r'
	@printf "\033[0m\n\n"
	@echo "👉 Press [ENTER] to try writing a new key now that memory is full..."; if [ "$(AUTO)" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
	@printf "\n\033[1;33m[Step 4] Attempting to write a new key...\033[0m\n"
	@printf "Executing: SET new_test_key \"This is a test\"\n"
	@docker exec redis-master redis-cli SET new_test_key "This is a test"
	@printf "\n\033[0;32m🎉 Demonstration Complete!\033[0m\n"
	@printf "Because we configured \033[0;36mallkeys-lru\033[0m, Redis didn't crash! It automatically deleted old keys to make room for new ones.\n"
	@printf "If the policy was \033[0;31mnoeviction\033[0m, the SET command above would have returned an OOM error.\n\n"

# Test Cache Avalanche Scenario
test-avalanche:
	@printf "\n\033[0;34m========================================================\033[0m\n"
	@printf "\033[0;34m❄️  Starting Cache Avalanche (缓存雪崩) Demonstration\033[0m\n"
	@printf "\033[0;34m========================================================\033[0m\n\n"
	@printf "\033[1;33m[Step 1] The BAD Practice: Setting 200 keys with the EXACT same TTL (15s)...\033[0m\n"
	@docker exec redis-master sh -c 'for i in $$(seq 1 200); do echo "SET bad_key:$$i \"value\" EX 15"; done | redis-cli --pipe > /dev/null 2>&1'
	@printf "\033[0;32m✔ 200 keys created with exactly 15s expiration.\033[0m\n\n"
	@echo "👉 Press [ENTER] to watch the Live TTL Dashboard..."; if [ "$(AUTO)" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
	@printf "\n\033[0;36mLive TTL Dashboard (200 Keys - Bad Practice):\033[0m\n"
	@for i in $$(seq 1 10); do echo ""; done
	@printf "\033[?25l"
	@for step in $$(seq 1 32); do \
		printf "\033[10A"; \
		docker exec redis-master redis-cli --raw EVAL "local ttls={}; for i=1,200 do table.insert(ttls, redis.call('TTL', ARGV[1]..':'..i)) end; return ttls" 0 "bad_key" | \
		awk '{ \
			gsub(/\r/, "", $$1); \
			if ($$1 == -2) val = "\033[0;31m -\033[0m"; \
			else if ($$1 <= 5) val = sprintf("\033[1;31m%2d\033[0m", $$1); \
			else if ($$1 <= 10) val = sprintf("\033[1;33m%2d\033[0m", $$1); \
			else val = sprintf("\033[1;32m%2d\033[0m", $$1); \
			if (NR % 20 == 0) printf "%s\n", val; \
			else printf "%s ", val; \
		}'; \
		sleep 0.5; \
	done
	@printf "\033[?25h"
	@printf "\n💥 \033[0;31mAll keys expired simultaneously! If these were hot data, your database would be crushed right now.\033[0m\n\n"
	@echo "👉 Press [ENTER] to simulate the GOOD practice (Adding random jitter)..."; if [ "$(AUTO)" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
	@printf "\n\033[1;33m[Step 2] The GOOD Practice: Adding random jitter to TTLs (10s + random 0-10s)...\033[0m\n"
	@docker exec redis-master sh -c 'for i in $$(seq 1 200); do jitter=$$((RANDOM % 11)); echo "SET good_key:$$i \"value\" EX $$((10 + jitter))"; done | redis-cli --pipe > /dev/null 2>&1'
	@printf "\033[0;32m✔ 200 keys created with 10s~20s expiration.\033[0m\n\n"
	@echo "👉 Press [ENTER] to watch the Live TTL Dashboard..."; if [ "$(AUTO)" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
	@printf "\n\033[0;36mLive TTL Dashboard (200 Keys - Good Practice):\033[0m\n"
	@for i in $$(seq 1 10); do echo ""; done
	@printf "\033[?25l"
	@for step in $$(seq 1 42); do \
		printf "\033[10A"; \
		docker exec redis-master redis-cli --raw EVAL "local ttls={}; for i=1,200 do table.insert(ttls, redis.call('TTL', ARGV[1]..':'..i)) end; return ttls" 0 "good_key" | \
		awk '{ \
			gsub(/\r/, "", $$1); \
			if ($$1 == -2) val = "\033[0;31m -\033[0m"; \
			else if ($$1 <= 5) val = sprintf("\033[1;31m%2d\033[0m", $$1); \
			else if ($$1 <= 10) val = sprintf("\033[1;33m%2d\033[0m", $$1); \
			else val = sprintf("\033[1;32m%2d\033[0m", $$1); \
			if (NR % 20 == 0) printf "%s\n", val; \
			else printf "%s ", val; \
		}'; \
		sleep 0.5; \
	done
	@printf "\033[?25h"
	@printf "\n🎉 \033[0;32mKeys are expiring gradually! The database load is smoothed out.\033[0m\n\n"

# Test Cache Penetration Scenario
test-penetration:
	@printf "\n\033[0;34m========================================================\033[0m\n"
	@printf "\033[0;34m👻 Starting Cache Penetration (缓存穿透) Demonstration\033[0m\n"
	@printf "\033[0;34m========================================================\033[0m\n\n"
	@printf "\033[1;33m[Concept] A malicious user requests a key that doesn't exist in Cache OR Database (e.g., user:-1).\033[0m\n\n"
	@echo "👉 Press [ENTER] to simulate the BAD practice..."; if [ "$(AUTO)" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
	@printf "\n\033[1;33m[Step 1] The BAD Practice: Doing nothing when DB returns empty...\033[0m\n"
	@printf "Request 1 for user:-1 -> Cache Miss! -> \033[0;31mQuerying Database (Heavy Load)...\033[0m -> DB returns empty.\n"
	@printf "Request 2 for user:-1 -> Cache Miss! -> \033[0;31mQuerying Database (Heavy Load)...\033[0m -> DB returns empty.\n"
	@printf "Request 3 for user:-1 -> Cache Miss! -> \033[0;31mQuerying Database (Heavy Load)...\033[0m -> DB returns empty.\n"
	@printf "💥 The cache is completely bypassed! The database takes all the hits.\n\n"
	@echo "👉 Press [ENTER] to simulate the GOOD practice (Caching empty results)..."; if [ "$(AUTO)" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
	@printf "\n\033[1;33m[Step 2] The GOOD Practice: Caching the empty result with a short TTL...\033[0m\n"
	@printf "Request 1 for user:-1 -> Cache Miss! -> Querying Database... -> DB returns empty.\n"
	@printf "Writing empty result to cache: \033[0;36mSET user:-1 \"<NULL>\" EX 60\033[0m\n"
	@docker exec redis-master redis-cli SET user:-1 "<NULL>" EX 60 > /dev/null
	@printf "\033[0;32m✔ Empty result cached.\033[0m\n\n"
	@printf "Request 2 for user:-1 -> \033[0;32mCache Hit! (Value: <NULL>)\033[0m -> Database is safe.\n"
	@printf "Request 3 for user:-1 -> \033[0;32mCache Hit! (Value: <NULL>)\033[0m -> Database is safe.\n"
	@printf "Checking cached value: \033[0;32m"
	@docker exec redis-master redis-cli GET user:-1 | tr -d '\r'
	@printf "\033[0m\n\n"
	@printf "🎉 The database is protected from repeated malicious queries!\n"
	@printf "(Note: For advanced protection, use a Bloom Filter before checking the cache).\n\n"
