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
	@printf "\033[1;34m🛠️  MySQL Cluster Management\033[0m\n\n"
	@printf "Usage: \033[36mmake [target]\033[0m\n\n"
	@printf "Targets:\n"
	@printf "  \033[32mstart\033[0m       🚀 Initialize and start the cluster\n"
	@printf "  \033[31mstop\033[0m        🛑 Stop the cluster\n"
	@printf "  \033[31mclean\033[0m       🧹 Stop and remove all data\n"
	@printf "  \033[33mreset\033[0m       🔄 Clean and restart\n"
	@printf "  \033[36mseed\033[0m        🌱 Generate sample data (e.g., make seed 500)\n"
	@printf "  \033[36mtest-perf\033[0m   ⏱️  Run insert performance test\n"
	@printf "  \033[36mtest-prefix\033[0m 🔍 Run prefix performance experiment\n"
	@printf "  \033[36mstudy-locks\033[0m 🔒 Run MySQL locks study\n"
	@printf "  \033[36mtest\033[0m        🧪 Run unit tests\n"
	@printf "  \033[35mstatus\033[0m      📊 Check cluster status\n"
	@printf "  \033[35mlogs\033[0m        📄 View cluster logs\n"

init:
	@printf "\033[1;34m📁 Preparing directories...\033[0m\n"
	@mkdir -p master/data slave/data master/conf slave/conf master/init slave/init
	@cp init-database.sql master/init/ 2>/dev/null || true

define wait_for_healthy
	@bash -c ' \
	sp=( "⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏" ); \
	i=0; \
	while ! docker-compose ps $(1) 2>/dev/null | grep -q "healthy"; do \
		printf "\r\033[33m%s\033[0m Waiting for \033[36m$(2)\033[0m to be ready...\033[K" "$${sp[i]}"; \
		i=$$(( (i+1) % 10 )); \
		sleep 0.1; \
	done; \
	printf "\r\033[32m✔\033[0m \033[36m$(2)\033[0m is ready! \033[K\n" \
	'
endef

define wait_for_seeder
	@printf "\033[1;34m🌱 Waiting for data seeder to complete (this may take a moment)...\033[0m\n"
	@docker wait $$(docker-compose ps -a -q seeder) > /dev/null 2>&1 || true
	@printf "\033[1;36m📊 Seeder Result:\033[0m\n"
	@bash -c ' \
		LAST_LINE=$$(docker-compose logs --tail=1 --no-log-prefix seeder 2>/dev/null); \
		if [[ "$$LAST_LINE" == *"Data already exists"* ]]; then \
			printf "  \033[33m%s\033[0m\n" "$$LAST_LINE"; \
		else \
			docker-compose logs --no-log-prefix seeder 2>/dev/null | grep -E "Data already exists|Data seeding completed|Error|Seeding" | tail -n 5 | sed "s/^/  /"; \
		fi \
	'
endef

start: init
	@printf "\033[1;34m🚀 Starting MySQL Cluster...\033[0m\n"
	@docker-compose up -d > /dev/null 2>&1
	$(call wait_for_healthy,mysql-master,Master Node)
	$(call wait_for_healthy,mysql-slave,Slave Node)
	$(call wait_for_seeder)
	@printf "\033[1;32m✨ Cluster is up and running!\033[0m\n"

stop:
	@printf "\033[1;33m🛑 Stopping cluster...\033[0m\n"
	@docker-compose down
	@printf "\033[1;32m✔ Cluster stopped.\033[0m\n"

clean: stop
	@printf "\033[1;33m🧹 Cleaning workspace...\033[0m\n"
	@docker-compose down -v
	@sudo rm -rf master/data/* slave/data/*
	@printf "\033[1;32m✔ Workspace cleaned.\033[0m\n"

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
		printf "\033[1;31m❌ Error: mysql-master is not running. Run 'make start' first.\033[0m\n"; \
		exit 1; \
	fi
	@printf "\033[1;34m⏳ Running script...\033[0m\n"
	@docker-compose run --rm seeder bash -c "pip install -r requirements.txt > /dev/null 2>&1 && python $(1)"
	@printf "\033[1;32m✔ Done!\033[0m\n"
endef

seed:
	@printf "\033[1;36m🌱 Seeding $(ACTUAL_COUNT) records...\033[0m\n"
	$(call run_python_script,seeders/main.py $(ACTUAL_COUNT))

test-perf:
	@printf "\033[1;36m⏱️  Running performance test ($(ACTUAL_COUNT) records)...\033[0m\n"
	$(call run_python_script,benchmarks/benchmark_inserts.py $(ACTUAL_COUNT))

test-prefix:
	@printf "\033[1;36m🔍 Running prefix performance experiment...\033[0m\n"
	$(call run_python_script,benchmarks/benchmark_like_prefix.py)

study-locks:
	@printf "\033[1;36m🔒 Running MySQL locks study...\033[0m\n"
	$(call run_python_script,demos/mysql_locks.py)

test:
	@printf "\033[1;36m🧪 Running unit tests...\033[0m\n"
	@docker-compose run --rm seeder bash -c "pip install -r requirements.txt > /dev/null 2>&1 && pytest tests/ -v"

status:
	@printf "\n\033[1;34m📊 MySQL Cluster Status\033[0m\n"
	@printf "\033[1;30m========================\033[0m\n"
	@printf "\033[1;36m🐳 Containers:\033[0m\n"
	@docker-compose ps
	@printf "\n\033[1;36m👑 Master Status:\033[0m\n"
	@docker exec mysql-master mysql -uroot -p$(MYSQL_ROOT_PASSWORD) -e "SHOW MASTER STATUS;" 2>/dev/null || echo "  ❌ Master not ready"
	@printf "\n\033[1;36m🛡️  Slave Status:\033[0m\n"
	@docker exec mysql-slave mysql -uroot -p$(MYSQL_ROOT_PASSWORD) -e "SHOW REPLICA STATUS\G" | grep -E "Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Master|Last_Error" 2>/dev/null || echo "  ❌ Slave not ready"
	@printf "\n"

logs:
	@docker-compose logs -f

# Catch-all target to allow arguments to be passed to make commands
%:
	@:
