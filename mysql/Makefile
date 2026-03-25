# Load environment variables if exists
-include .env
export

# Default values
MYSQL_ROOT_PASSWORD ?= rootpassword123
MYSQL_DATABASE ?= business_db
COUNT ?= 100

.PHONY: help init start stop clean reset seed status logs

# Default target, show help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  start   - Initialize and start the MySQL master-slave cluster"
	@echo "  stop    - Stop the cluster"
	@echo "  clean   - Stop the cluster and remove all data volumes"
	@echo "  reset   - Clean and then start the cluster"
	@echo "  seed    - Generate meaningful sample data (e.g., make seed COUNT=500)"
	@echo "  test-perf - Run performance test for inserts"
	@echo "  test-prefix - Run prefix performance experiment"
	@echo "  study-locks - Run MySQL locks study scenarios"
	@echo "  test    - Run unit tests for Python scripts"
	@echo "  status  - Check cluster and replication status"
	@echo "  logs    - View cluster logs"

init:
	@printf "\033[1;34mCreating necessary directories...\033[0m\n"
	@mkdir -p master/data slave/data
	@mkdir -p master/conf slave/conf
	@mkdir -p master/init slave/init
	@printf "\033[1;34mCopying initialization scripts...\033[0m\n"
	@cp init-database.sql master/init/ 2>/dev/null || true

define wait_for_healthy
	@bash -c ' \
sp=( "⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏" ); \
i=0; \
while ! docker-compose ps $(1) 2>/dev/null | grep -q "healthy"; do \
printf "\r\033[33m%s Waiting for $(2) to be healthy...\033[0m" "$${sp[i]}"; \
i=$$(( (i+1) % 10 )); \
sleep 0.1; \
done; \
printf "\r\033[32m✔ $(2) is healthy!                                \033[0m\n" \
'
endef

start: init
	@printf "\033[1;34mStarting Docker Compose services...\033[0m\n"
	@docker-compose up -d
	$(call wait_for_healthy,mysql-master,MySQL master)
	$(call wait_for_healthy,mysql-slave,MySQL slave)
	@printf "\033[1;32mCluster started successfully!\033[0m\n"

stop:
	@printf "\033[1;34mStopping cluster...\033[0m\n"
	@docker-compose down

clean: stop
	@printf "\033[1;34mCleaning workspace (removing containers and data)...\033[0m\n"
	@docker-compose down -v
	@sudo rm -rf master/data/* slave/data/*
	@printf "\033[1;32mWorkspace cleaned.\033[0m\n"

reset: clean start

# Allow passing arguments to seed like `make seed 1000`
ifeq (seed,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "seed"
  SEED_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(SEED_ARGS):;@:)
endif

# Allow passing arguments to test-perf like `make test-perf 1000`
ifeq (test-perf,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "test-perf"
  SEED_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(SEED_ARGS):;@:)
endif

# If SEED_ARGS is set, use it as COUNT, otherwise use default COUNT
ifneq ($(SEED_ARGS),)
  ACTUAL_COUNT = $(SEED_ARGS)
else
  ACTUAL_COUNT = $(COUNT)
endif

define run_python_script
	@if ! docker-compose ps mysql-master | grep -qiE "up|running"; then \
echo "Error: mysql-master is not running. Please run 'make start' first."; \
exit 1; \
fi
	@docker run --rm --network docker-compose_mysql-network \
-v $(PWD)/seeder:/app -w /app \
-e MYSQL_HOST=mysql-master \
-e MYSQL_USER=$(MYSQL_USER) \
-e MYSQL_PASSWORD=$(MYSQL_PASSWORD) \
-e MYSQL_DATABASE=$(MYSQL_DATABASE) \
python:3.9-slim bash -c "pip install -r requirements.txt > /dev/null 2>&1 && python $(1)"
endef

seed:
	@echo "Seeding $(ACTUAL_COUNT) records of meaningful data..."
	$(call run_python_script,seed.py $(ACTUAL_COUNT))

test-perf:
	@echo "Running performance test with $(ACTUAL_COUNT) records..."
	$(call run_python_script,benchmark_inserts.py $(ACTUAL_COUNT))

test-prefix:
	@echo "Running prefix performance experiment..."
	$(call run_python_script,benchmark_like_prefix.py)

study-locks:
	@echo "Running MySQL locks study scenarios..."
	$(call run_python_script,study_locks.py)

test:
	@echo "Running unit tests..."
	@docker run --rm \
-v $(PWD)/seeder:/app -w /app \
python:3.9-slim bash -c "pip install -r requirements.txt > /dev/null 2>&1 && pytest tests/ -v"

status:
	@echo "=== Docker Containers Status ==="
	@docker-compose ps
	@echo "\n=== Master Status ==="
	@docker exec mysql-master mysql -uroot -p$(MYSQL_ROOT_PASSWORD) -e "SHOW MASTER STATUS;" 2>/dev/null || echo "Master not ready"
	@echo "\n=== Slave Status ==="
	@docker exec mysql-slave mysql -uroot -p$(MYSQL_ROOT_PASSWORD) -e "SHOW REPLICA STATUS\G" | grep -E "Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Master|Last_Error" 2>/dev/null || echo "Slave not ready"

logs:
	@docker-compose logs -f

# Catch-all target to allow arguments to be passed to make commands
%:
	@:
