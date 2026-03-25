# Redis Playground / Redis 游乐场

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## 🇬🇧 English

Welcome to the Redis Playground! This environment is designed to help you learn, experiment, and understand the core features, common use cases, and potential pitfalls of Redis.

### 🌟 Features Demonstrated

1. **Master-Slave Replication**: A basic high-availability setup with one master and two read-only replicas.
2. **High Availability (Sentinel)**: Three Sentinel nodes configured to monitor the master and automatically perform failover if the master goes down.
3. **Persistence Mechanisms**: Both RDB (snapshotting) and AOF (Append Only File) are configured to demonstrate data durability.
4. **Memory Management**: Configured with `maxmemory` and an eviction policy (`allkeys-lru`) to simulate memory-constrained environments.
5. **Visual Management**: Includes `redis-commander` for a web-based GUI to inspect keys and monitor the instances.

### 🚀 Quick Start

1. **Start the Environment**:
   ```bash
   make start
   ```
   This will start the Redis Master, Redis Slave, and Redis Commander.

2. **Access Redis Commander**:
   Open your browser and go to `http://localhost:8081`. You can view both the master and slave databases here.

3. **Check Replication Status**:
   ```bash
   make status
   ```

4. **Test Automatic Failover (Sentinel)**:
   ```bash
   make test-failover
   ```
   This command will stop the master node, wait for Sentinel to detect the failure, and automatically promote one of the slaves to be the new master.

5. **Test Persistence (RDB/AOF)**:
   ```bash
   make test-persistence
   ```
   This command writes test data to the master, completely stops the cluster, restarts it, and verifies that the data survived the restart.

6. **Test Big Key Problem**:
   ```bash
   make test-bigkey
   ```
   This command demonstrates the performance difference between using `DEL` (blocking) and `UNLINK` (non-blocking) when deleting a massive Hash key.

7. **Test Out of Memory (OOM)**:
   ```bash
   make test-oom
   ```
   This command fills up the Redis memory to hit the `maxmemory` limit and demonstrates how the `allkeys-lru` eviction policy keeps the server running by deleting old keys.

8. **Connect via CLI**:
   ```bash
   make cli-master  # Connect to Master
   make cli-slave   # Connect to Slave
   ```

### 💡 Common Use Cases & Experiments

#### 1. Caching (String & Hash)
Redis is most commonly used as a cache.
- **Experiment**: Store user session data using Hashes.
  ```redis
  HSET session:1001 user_id "user123" status "active" last_login "2023-10-27"
  HGETALL session:1001
  EXPIRE session:1001 3600  # Set expiration
  ```

#### 2. Leaderboards / Ranking (Sorted Set)
Sorted Sets (`ZSET`) are perfect for leaderboards.
- **Experiment**: Add players and their scores, then get the top 3.
  ```redis
  ZADD leaderboard 1500 "PlayerA" 2000 "PlayerB" 1200 "PlayerC"
  ZREVRANGE leaderboard 0 2 WITHSCORES
  ```

#### 3. Message Queue / Pub-Sub (List & Pub/Sub)
- **Experiment (List)**: Use lists as a simple queue.
  ```redis
  LPUSH task_queue "task1" "task2"
  RPOP task_queue
  ```
- **Experiment (Pub/Sub)**: Open two CLI windows. In one, subscribe to a channel; in the other, publish a message.
  ```redis
  # Window 1 (Subscriber)
  SUBSCRIBE news_channel
  # Window 2 (Publisher)
  PUBLISH news_channel "Breaking News!"
  ```

#### 4. Distributed Locks (String with NX)
- **Experiment**: Simulate acquiring a lock.
  ```redis
  SET resource_lock "unique_id" NX EX 10
  # If it returns OK, lock acquired. If nil, lock is held by someone else.
  ```

### ⚠️ Common Pitfalls & Solutions

#### 1. The "Big Key" Problem
- **Pitfall**: Storing massive amounts of data in a single key (e.g., a Hash with millions of fields). This blocks Redis's single thread when accessing or deleting the key, causing latency spikes.
- **Solution**: Split the big key into smaller keys (e.g., sharding based on user ID hash). Use `UNLINK` instead of `DEL` for asynchronous deletion.

#### 2. Cache Avalanche (缓存雪崩)
- **Pitfall**: A large number of cached keys expire at the exact same time, causing a massive surge of requests to hit the backend database simultaneously, potentially crashing it.
- **Solution**: Add a random jitter (e.g., 1-5 minutes) to the expiration time of keys so they don't all expire at once.

#### 3. Cache Penetration (缓存穿透)
- **Pitfall**: Repeatedly querying for a key that does not exist in both the cache and the database. The cache never hits, so every request hits the database.
- **Solution**:
  1. Cache empty results (with a short TTL).
  2. Use a **Bloom Filter** to quickly check if a key *might* exist before hitting the database.

#### 4. Cache Breakdown (缓存击穿)
- **Pitfall**: A highly accessed "hot" key expires. Before the cache can be rebuilt, thousands of concurrent requests hit the database for that specific key.
- **Solution**: Use a distributed lock (like `SETNX`) when rebuilding the cache. Only the thread that acquires the lock queries the database and updates the cache; other threads wait or return stale data.

#### 5. Memory Exhaustion (OOM)
- **Pitfall**: Redis runs out of memory and crashes or starts swapping to disk (killing performance).
- **Solution**: We have configured `maxmemory 256mb` and `maxmemory-policy allkeys-lru` in `redis.conf`. When memory is full, Redis will automatically evict the least recently used keys. Always monitor memory usage (`INFO memory`).

### 🧹 Cleanup

```bash
make stop   # Stop containers
make clean  # Stop containers and delete all persistent data
```

---

<a name="中文"></a>
## 🇨🇳 中文

欢迎来到 Redis 游乐场！本环境旨在帮助您学习、实验并深入理解 Redis 的核心特性、常见使用场景以及潜在的“坑”（陷阱）。

### 🌟 演示特性

1. **主从复制 (Master-Slave)**：配置了一主两从的基础高可用架构，从节点只读。
2. **高可用自动故障转移 (Sentinel)**：配置了 3 个 Sentinel（哨兵）节点，实时监控主节点状态。当主节点宕机时，自动将一个从节点提升为新主节点。
3. **持久化机制**：同时开启了 RDB（快照）和 AOF（追加文件），演示数据如何持久化到磁盘。
4. **内存管理**：在配置文件中设置了 `maxmemory` 限制和 `allkeys-lru` 淘汰策略，模拟内存受限环境。
5. **可视化管理**：集成了 `redis-commander`，提供 Web GUI 方便查看键值和监控实例。

### 🚀 快速开始

1. **启动环境**：
   ```bash
   make start
   ```
   这将启动 Redis 主节点、从节点以及 Redis Commander。

2. **访问可视化界面**：
   打开浏览器访问 `http://localhost:8081`。您可以在这里同时查看主库和从库的数据。

3. **检查复制状态**：
   ```bash
   make status
   ```

4. **测试自动故障转移 (Sentinel)**：
   ```bash
   make test-failover
   ```
   该命令会模拟主节点宕机（停止 master 容器），等待哨兵检测到故障后，自动将其中一个从节点提升为新的主节点。

5. **测试持久化 (RDB/AOF)**：
   ```bash
   make test-persistence
   ```
   该命令会向主节点写入测试数据，然后完全停止整个集群并重新启动，最后验证数据是否在重启后依然存在。

6. **测试大 Key 问题 (Big Key)**：
   ```bash
   make test-bigkey
   ```
   该命令会创建一个包含 10 万个字段的超大 Hash 键，并直观地演示使用 `DEL`（阻塞式删除）和 `UNLINK`（异步非阻塞删除）在耗时上的巨大差异。

7. **测试内存耗尽 (OOM)**：
   ```bash
   make test-oom
   ```
   该命令会疯狂写入数据直到触发 `maxmemory` 内存上限，并演示 `allkeys-lru` 淘汰策略是如何通过自动删除旧数据来保证 Redis 继续正常提供服务的。

8. **通过命令行连接**：
   ```bash
   make cli-master  # 连接到主节点
   make cli-slave   # 连接到从节点
   ```

### 💡 常见使用场景与实验

#### 1. 缓存 (String & Hash)
Redis 最常见的用途就是作为缓存。
- **实验**：使用 Hash 存储用户会话数据。
  ```redis
  HSET session:1001 user_id "user123" status "active" last_login "2023-10-27"
  HGETALL session:1001
  EXPIRE session:1001 3600  # 设置过期时间
  ```

#### 2. 排行榜 (Sorted Set)
有序集合 (`ZSET`) 非常适合做排行榜。
- **实验**：添加玩家分数，并获取前 3 名。
  ```redis
  ZADD leaderboard 1500 "PlayerA" 2000 "PlayerB" 1200 "PlayerC"
  ZREVRANGE leaderboard 0 2 WITHSCORES
  ```

#### 3. 消息队列 / 发布订阅 (List & Pub/Sub)
- **实验 (List)**：使用 List 作为简单的任务队列。
  ```redis
  LPUSH task_queue "task1" "task2"
  RPOP task_queue
  ```
- **实验 (Pub/Sub)**：打开两个 CLI 窗口。一个订阅频道，另一个发布消息。
  ```redis
  # 窗口 1 (订阅者)
  SUBSCRIBE news_channel
  # 窗口 2 (发布者)
  PUBLISH news_channel "突发新闻！"
  ```

#### 4. 分布式锁 (String with NX)
- **实验**：模拟获取一个锁。
  ```redis
  SET resource_lock "unique_id" NX EX 10
  # 如果返回 OK，说明获取锁成功。如果返回 nil，说明锁被别人占用了。
  ```

### ⚠️ 常见的坑与解决方案

#### 1. 大 Key 问题 (Big Key)
- **坑**：在一个 Key 中存储了海量数据（例如包含数百万个字段的 Hash）。由于 Redis 是单线程处理命令，读取或删除这个大 Key 会阻塞其他所有请求，导致严重的延迟毛刺。
- **解决**：将大 Key 拆分成多个小 Key（例如按用户 ID 哈希分片）。删除时使用 `UNLINK` 命令代替 `DEL` 进行异步删除。

#### 2. 缓存雪崩 (Cache Avalanche)
- **坑**：大量缓存数据在同一时间集中过期，导致原本应该访问缓存的请求全部打到了后端数据库上，瞬间压垮数据库。
- **解决**：在设置过期时间时，加上一个随机的抖动值（例如 1-5 分钟的随机数），让过期时间分散开。

#### 3. 缓存穿透 (Cache Penetration)
- **坑**：恶意请求频繁查询一个在缓存和数据库中都**不存在**的 Key。由于缓存不命中，每次请求都会去查数据库，导致数据库压力过大。
- **解决**：
  1. 缓存空值（设置较短的过期时间）。
  2. 使用 **布隆过滤器 (Bloom Filter)**，在请求到达缓存前，先快速判断该 Key 是否可能存在。

#### 4. 缓存击穿 (Cache Breakdown)
- **坑**：一个被极高并发访问的“热点” Key 突然过期。在缓存重新构建完成之前，成千上万的并发请求直接打到了数据库上，只为了查询这一个 Key。
- **解决**：使用分布式锁（如 `SETNX`）。当缓存失效时，只允许一个线程去查询数据库并重建缓存，其他线程等待锁释放或返回旧数据。

#### 5. 内存耗尽 (OOM)
- **坑**：Redis 内存写满，导致服务崩溃或操作系统开始使用 Swap（极大地降低性能）。
- **解决**：我们在 `redis.conf` 中配置了 `maxmemory 256mb` 和 `maxmemory-policy allkeys-lru`。当内存满时，Redis 会自动淘汰最近最少使用的 Key。生产环境中必须监控内存使用率 (`INFO memory`)。

### 🧹 清理环境

```bash
make stop   # 停止容器
make clean  # 停止容器并删除所有持久化数据卷
```
