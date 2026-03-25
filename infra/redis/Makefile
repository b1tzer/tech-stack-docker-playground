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
	@bash ../../scripts/demos/test_failover.sh

# Test Persistence Scenario
test-persistence:
	@bash ../../scripts/demos/test_persistence.sh

# Test Big Key Scenario
test-bigkey:
	@bash ../../scripts/demos/test_bigkey.sh

# Test OOM (Out of Memory) Scenario
test-oom:
	@bash ../../scripts/demos/test_oom.sh

# Test Cache Avalanche Scenario
test-avalanche:
	@bash ../../scripts/demos/test_avalanche.sh

# Test Cache Penetration Scenario
test-penetration:
	@bash ../../scripts/demos/test_penetration.sh
