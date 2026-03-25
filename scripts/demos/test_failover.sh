#!/bin/bash
AUTO=${AUTO:-0}
printf "\n\033[0;34m========================================================\033[0m\n"
printf "\033[0;34m🛡️  Starting Redis Sentinel Failover Demonstration\033[0m\n"
printf "\033[0;34m========================================================\033[0m\n\n"
printf "\033[1;33m[Step 1] Current Cluster Topology:\033[0m\n"
M_ROLE=$(docker exec redis-master redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
 S1_ROLE=$(docker exec redis-slave redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
 S2_ROLE=$(docker exec redis-slave2 redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
 printf "\n           [ 👑 \033[1;32mredis-master\033[0m ($M_ROLE) ]\n" ; \
 printf '             /                      \\\n' ; \
 printf "[ 🛡️ \033[1;36mredis-slave\033[0m ($S1_ROLE) ]  [ 🛡️ \033[1;36mredis-slave2\033[0m ($S2_ROLE) ]\n\n"
echo "👉 Press [ENTER] to simulate Master failure (docker pause redis-master)..."; if [ "$AUTO" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
printf "\n\033[0;31m💥 Pausing redis-master (simulating network partition/hang)...\033[0m\n"
docker pause redis-master > /dev/null 2>&1 || true
printf "\n           [ ❌ \033[1;31mredis-master\033[0m (down) ]\n"
printf '             /                      \\\n'
printf "[ 🛡️ \033[1;36mredis-slave\033[0m (slave) ]  [ 🛡️ \033[1;36mredis-slave2\033[0m (slave) ]\n\n"
printf "\033[1;33m[Step 2] Sentinels detecting failure and voting...\033[0m\n"
printf "\033[?25l"
for i in $(seq 1 25); do \
	printf "\r\033[K\033[0;33m👀 Sentinels observing and negotiating... %2d seconds\033[0m" $i; \
	sleep 1; \
done
printf "\r\033[K\033[?25h"
printf "\n\033[1;33m[Step 3] Sentinel Decision Log (Highlights):\033[0m\n"
docker logs redis-sentinel-1 --since 30s | grep -E "sdown|odown|vote-for-leader|switch-master" | sed 's/^/  /' || echo "  (No logs found, maybe still deciding?)"
printf "\n\033[1;33m[Step 4] Live Cluster Topology (Updating for 15s):\033[0m\n"
printf "\n\n\n\n"
printf "\033[?25l"
for i in $(seq 1 15); do \
	printf "\033[4A"; \
	S1_ROLE=$(docker exec redis-slave redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
	S2_ROLE=$(docker exec redis-slave2 redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
	if [ "$S1_ROLE" = "master" ]; then \
		printf "           [ ❌ \033[1;31mredis-master\033[0m (down) ]\033[K\n" ; \
		printf '             /                      \\\033[K\n' ; \
		printf "[ 👑 \033[1;32mredis-slave\033[0m (master) ]  [ 🛡️ \033[1;36mredis-slave2\033[0m ($S2_ROLE) ]\033[K\n\n" ; \
	elif [ "$S2_ROLE" = "master" ]; then \
		printf "           [ ❌ \033[1;31mredis-master\033[0m (down) ]\033[K\n" ; \
		printf '             /                      \\\033[K\n' ; \
		printf "[ 🛡️ \033[1;36mredis-slave\033[0m ($S1_ROLE) ]  [ 👑 \033[1;32mredis-slave2\033[0m (master) ]\033[K\n\n" ; \
	else \
		printf "           [ ❌ \033[1;31mredis-master\033[0m (down) ]\033[K\n" ; \
		printf '             /                      \\\033[K\n' ; \
		printf "[ 🛡️ \033[1;36mredis-slave\033[0m ($S1_ROLE) ]  [ 🛡️ \033[1;36mredis-slave2\033[0m ($S2_ROLE) ]\033[K\n" ; \
		printf "  ⚠️  Failover in progress... ($i/15s)\033[K\n" ; \
	fi; \
	sleep 1; \
done
printf "\033[?25h"
echo "👉 Press [ENTER] to unpause the old master and see it join as a slave..."; if [ "$AUTO" = "1" ]; then echo "   ⏳ Auto-continuing in 2s..."; sleep 2; else read dummy; fi
printf "\n\033[0;34m🔄 Unpausing redis-master...\033[0m\n"
docker unpause redis-master > /dev/null 2>&1 || true
printf "\033[?25l"
for i in $(seq 1 5); do \
	printf "\r\033[K\033[0;33m⏳ Waiting for old master to sync... %2d seconds\033[0m" $i; \
	sleep 1; \
done
printf "\r\033[K\033[?25h"
printf "\n\033[1;33m[Step 5] Final Cluster Topology:\033[0m\n"
M_ROLE=$(docker exec redis-master redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
 S1_ROLE=$(docker exec redis-slave redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
 S2_ROLE=$(docker exec redis-slave2 redis-cli role 2>/dev/null | head -n 1 | tr -d '\r' || echo "down") ; \
 if [ "$S1_ROLE" = "master" ]; then \
 	printf "\n           [ 🛡️ \033[1;36mredis-master\033[0m ($M_ROLE) ]\n" ; \
 	printf '             /                      \\\n' ; \
 	printf "[ 👑 \033[1;32mredis-slave\033[0m (master) ] [ 🛡️ \033[1;36mredis-slave2\033[0m ($S2_ROLE) ]\n\n" ; \
 elif [ "$S2_ROLE" = "master" ]; then \
 	printf "\n           [ 🛡️ \033[1;36mredis-master\033[0m ($M_ROLE) ]\n" ; \
 	printf '             /                      \\\n' ; \
 	printf "[ 🛡️ \033[1;36mredis-slave\033[0m ($S1_ROLE) ]  [ 👑 \033[1;32mredis-slave2\033[0m (master) ]\n\n" ; \
 else \
 	printf "\n           [ 👑 \033[1;32mredis-master\033[0m ($M_ROLE) ]\n" ; \
 	printf '             /                      \\\n' ; \
 	printf "[ 🛡️ \033[1;36mredis-slave\033[0m ($S1_ROLE) ]  [ 🛡️ \033[1;36mredis-slave2\033[0m ($S2_ROLE) ]\n\n" ; \
 fi
printf "\033[0;32m🎉 Failover Demonstration Complete!\033[0m\n\n"
