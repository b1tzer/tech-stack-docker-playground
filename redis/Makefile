.PHONY: start stop clean logs status cli-master cli-slave test-failover test-persistence test-bigkey

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
	@printf "\033[1;33m[Step 1] Current Master according to Sentinel:\033[0m\n"
	@docker exec redis-sentinel-1 redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster
	@printf "\n"
	@echo "👉 Press [ENTER] to simulate Master failure (docker stop redis-master)..."; read dummy
	@printf "\n\033[0;31m💥 Stopping Redis Master...\033[0m\n"
	@docker stop redis-master
	@printf "\n\033[1;33m[Step 2] Waiting for Sentinel to detect failure and promote a slave (approx 10 seconds)...\033[0m\n"
	@sleep 10
	@printf "\n\033[1;33m[Step 3] New Master Status (Checking Sentinel):\033[0m\n"
	@docker exec redis-sentinel-1 redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster
	@printf "\n\033[1;33m[Step 4] Checking Role of redis-slave:\033[0m\n"
	@docker exec redis-slave redis-cli role | head -n 1 || true
	@printf "\n\033[1;33m[Step 5] Checking Role of redis-slave2:\033[0m\n"
	@docker exec redis-slave2 redis-cli role | head -n 1 || true
	@printf "\n\033[0;32m🎉 Failover complete!\033[0m\n"
	@printf "You can restart the old master with: \033[0;36mdocker start redis-master\033[0m\n\n"

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
	@echo "👉 Press [ENTER] to simulate a complete cluster crash (docker-compose down)..."; read dummy
	@printf "\n\033[0;31m💥 Stopping and removing all Redis containers...\033[0m\n"
	@docker-compose down
	@printf "\n\033[1;33m[Step 4] Cluster is down. Let's verify no containers are running...\033[0m\n"
	@docker ps | grep redis || printf "\033[0;32m✔ No Redis containers running.\033[0m\n"
	@printf "\n"
	@echo "👉 Press [ENTER] to restart the cluster and test data recovery..."; read dummy
	@printf "\n\033[0;34m🔄 Starting the cluster again...\033[0m\n"
	@docker-compose up -d
	@printf "\n\033[1;33m[Step 5] Waiting for cluster to initialize (5 seconds)...\033[0m\n"
	@sleep 5
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
	@echo "👉 Press [ENTER] to simulate the BAD practice (using DEL on a Big Key)..."; read dummy
	@printf "\n\033[0;31m💥 Executing DEL my_big_hash (This blocks Redis!)...\033[0m\n"
	@printf "Time taken to execute DEL: \033[0;31m"
	@docker exec redis-master sh -c 'time redis-cli DEL my_big_hash > /dev/null' 2>&1 | grep real | awk '{print $$2}'
	@printf "\033[0m\n"
	@printf "Notice how long it took? During this time, Redis couldn't process ANY other commands!\n\n"
	@echo "👉 Press [ENTER] to recreate the Big Key and simulate the GOOD practice (using UNLINK)..."; read dummy
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
