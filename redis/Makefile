.PHONY: start stop clean logs status cli-master cli-slave

# Start the Redis cluster
start:
@echo "Starting Redis Master-Slave cluster..."
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
sudo rm -rf data/master/* data/slave/*
@echo "Clean complete."

# View logs
logs:
docker-compose logs -f

# Check status
status:
docker-compose ps
@echo "\n--- Master Replication Status ---"
@docker exec redis-master redis-cli info replication | grep -E 'role|connected_slaves|master_repl_offset'
@echo "\n--- Slave Replication Status ---"
@docker exec redis-slave redis-cli info replication | grep -E 'role|master_host|master_link_status|slave_repl_offset'

# Connect to Master CLI
cli-master:
docker exec -it redis-master redis-cli

# Connect to Slave CLI
cli-slave:
docker exec -it redis-slave redis-cli
