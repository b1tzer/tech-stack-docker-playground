.PHONY: start stop clean logs status cli-master cli-slave test-failover

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
docker-compose ps
@echo "\n--- Master Replication Status ---"
@docker exec redis-master redis-cli info replication | grep -E 'role|connected_slaves|master_repl_offset' || echo "Master is down"
@echo "\n--- Slave 1 Replication Status ---"
@docker exec redis-slave redis-cli info replication | grep -E 'role|master_host|master_link_status|slave_repl_offset' || echo "Slave 1 is down"
@echo "\n--- Slave 2 Replication Status ---"
@docker exec redis-slave2 redis-cli info replication | grep -E 'role|master_host|master_link_status|slave_repl_offset' || echo "Slave 2 is down"
@echo "\n--- Sentinel Status ---"
@docker exec redis-sentinel-1 redis-cli -p 26379 info sentinel | grep status

# Connect to Master CLI
cli-master:
docker exec -it redis-master redis-cli

# Connect to Slave CLI
cli-slave:
docker exec -it redis-slave redis-cli

# Test Failover Scenario
test-failover:
@echo "1. Current Master according to Sentinel:"
@docker exec redis-sentinel-1 redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster
@echo "\n2. Stopping Redis Master to simulate failure..."
docker stop redis-master
@echo "\n3. Waiting for Sentinel to detect failure and promote a slave (approx 10 seconds)..."
sleep 10
@echo "\n4. New Master Status (Checking Sentinel):"
@docker exec redis-sentinel-1 redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster
@echo "\n5. Checking Role of redis-slave:"
@docker exec redis-slave redis-cli role | head -n 1 || true
@echo "\n6. Checking Role of redis-slave2:"
@docker exec redis-slave2 redis-cli role | head -n 1 || true
@echo "\nFailover complete. You can restart the old master with: docker start redis-master"
