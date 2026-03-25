import time
import argparse
import random
import uuid
from faker import Faker
from db_utils import get_db_connection
from seed import seed_users

fake = Faker(['zh_CN', 'en_US'])

def seed_users_single(cursor, connection, count):
    print(f"Seeding {count} users using single inserts (Slow Method)...")
    sql = """
        INSERT IGNORE INTO users 
        (username, email, password_hash, first_name, last_name, phone, status, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    for i in range(count):
        unique_id = str(uuid.uuid4())[:8]
        username = f"{fake.user_name()}_{unique_id}"
        email = f"{unique_id}_{fake.email()}"
        cursor.execute(sql, (
            username,
            email,
            fake.sha256(),
            fake.first_name(),
            fake.last_name(),
            fake.phone_number()[:20],
            random.choice(['active', 'active', 'active', 'inactive', 'suspended']),
            random.choice(['user', 'user', 'user', 'manager', 'admin'])
        ))
        # 真正的单条插入：每次执行完立刻提交事务，模拟最原始/最差的写法
        connection.commit()
        
        if (i + 1) % 1000 == 0:
            print(f"  -> Inserted {i + 1} users...")
    print(f"  -> Inserted {count} users...")

def get_mysql_metrics(cursor):
    """Fetch key MySQL performance metrics to demonstrate what happens under the hood."""
    metrics = {}
    
    # Session metrics (Network and Query counts)
    cursor.execute("""
        SHOW SESSION STATUS WHERE Variable_name IN (
            'Questions', 
            'Com_commit', 
            'Bytes_received'
        )
    """)
    for row in cursor.fetchall():
        metrics[row['Variable_name']] = int(row['Value'])
        
    # Global metrics (Disk I/O and InnoDB internals)
    # Note: In a shared DB, global metrics might be noisy, but for local testing they are perfect.
    cursor.execute("""
        SHOW GLOBAL STATUS WHERE Variable_name IN (
            'Innodb_os_log_written'
        )
    """)
    for row in cursor.fetchall():
        metrics[row['Variable_name']] = int(row['Value'])
        
    return metrics

def run_performance_test(cursor, connection, count):
    print("\n" + "="*80)
    print(f"🚀 STARTING ADVANCED PERFORMANCE TEST: Single vs Batch Insert ({count} records)")
    print("="*80)
    
    # Test 1: Single Inserts
    metrics_before_single = get_mysql_metrics(cursor)
    start_time = time.time()
    seed_users_single(cursor, connection, count)
    single_duration = time.time() - start_time
    metrics_after_single = get_mysql_metrics(cursor)
    
    single_metrics = {k: metrics_after_single.get(k, 0) - metrics_before_single.get(k, 0) for k in metrics_before_single}
    print(f"⏱️  Single Insert Time: {single_duration:.2f} seconds")
    
    # Clean up users table before next test to ensure fair comparison
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("TRUNCATE TABLE users")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    connection.commit()
    
    # Test 2: Batch Inserts
    metrics_before_batch = get_mysql_metrics(cursor)
    start_time = time.time()
    seed_users(cursor, connection, count)
    batch_duration = time.time() - start_time
    metrics_after_batch = get_mysql_metrics(cursor)
    
    batch_metrics = {k: metrics_after_batch.get(k, 0) - metrics_before_batch.get(k, 0) for k in metrics_before_batch}
    print(f"⏱️  Batch Insert Time: {batch_duration:.2f} seconds")
    
    print("\n" + "="*80)
    print("📊 ADVANCED PERFORMANCE & METRICS TEST RESULTS")
    print("="*80)
    print(f"{'Metric (What it measures)':<35} | {'Single Insert':<15} | {'Batch Insert':<15} | {'Comparison'}")
    print("-" * 80)
    
    # Time
    speedup = single_duration / max(0.001, batch_duration)
    print(f"{'⏱️ Time Taken (Execution Speed)':<35} | {single_duration:<15.2f} | {batch_duration:<15.2f} | {speedup:.1f}x faster")
    
    # Queries
    q_single = single_metrics.get('Questions', 0)
    q_batch = batch_metrics.get('Questions', 0)
    q_diff = q_single / max(1, q_batch)
    print(f"{'🗣️ Queries Sent (Network/CPU)':<35} | {q_single:<15} | {q_batch:<15} | {q_diff:.1f}x fewer queries")
    
    # Commits
    c_single = single_metrics.get('Com_commit', 0)
    c_batch = batch_metrics.get('Com_commit', 0)
    c_diff = c_single / max(1, c_batch)
    print(f"{'💾 Transactions (Disk fsyncs)':<35} | {c_single:<15} | {c_batch:<15} | {c_diff:.1f}x fewer commits")
    
    # Network
    n_single = single_metrics.get('Bytes_received', 0) / 1024
    n_batch = batch_metrics.get('Bytes_received', 0) / 1024
    n_diff = n_single / max(0.01, n_batch)
    print(f"{'🌐 Network Traffic (KB received)':<35} | {n_single:<15.1f} | {n_batch:<15.1f} | {n_diff:.1f}x less bandwidth")
    
    # Disk I/O
    io_single = single_metrics.get('Innodb_os_log_written', 0) / (1024 * 1024)
    io_batch = batch_metrics.get('Innodb_os_log_written', 0) / (1024 * 1024)
    io_diff = io_single / max(0.01, io_batch)
    print(f"{'💽 Redo Log Written (MB Disk I/O)':<35} | {io_single:<15.2f} | {io_batch:<15.2f} | {io_diff:.1f}x less disk I/O")
    
    print("="*80 + "\n")
    
    print("🔍 PERFORMANCE INSIGHTS & PRODUCTION METRICS:")
    print("1. 🗣️ Queries Sent (Questions):")
    print("   - Single inserts send a separate SQL string for every row. This consumes Database CPU for parsing SQL.")
    print("   - Batch inserts send one large SQL string, drastically reducing CPU parsing overhead and network round-trips.")
    print("\n2. 💾 Transactions (Com_commit):")
    print("   - Every commit forces MySQL to flush data to disk (fsync) to guarantee data isn't lost on crash (ACID properties).")
    print("   - Disk I/O is the slowest part of a database. 10,000 commits = 10,000 disk flushes. This is the #1 performance killer.")
    print("\n3. 🌐 Network Traffic (Bytes_received):")
    print("   - Notice how single inserts send much more data over the network? That's because the SQL boilerplate ")
    print("     ('INSERT INTO users VALUES...') is repeated 10,000 times!")
    print("\n4. 💽 Redo Log Written (Innodb_os_log_written):")
    print("   - InnoDB writes all changes to a 'Redo Log' on disk. Single transactions have massive overhead per row.")
    print("   - Batching reduces the metadata and transaction boundary overhead, writing significantly fewer megabytes to your SSD/HDD.")
    print("   - In production, high Redo Log writes cause disk wear and IOPS bottlenecks.")
    print("\n💡 PRO TIP FOR TROUBLESHOOTING:")
    print("If your database is slow, check 'SHOW GLOBAL STATUS LIKE \"Com_commit\"'. If it's skyrocketing,")
    print("your application is likely doing single-row inserts/updates instead of batching!")
    print("="*80 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Run performance comparison test between single and batch inserts.')
    parser.add_argument('count', type=int, nargs='?', default=10000, help='Number of records to generate for the test')
    args = parser.parse_args()

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            run_performance_test(cursor, connection, args.count)
    except Exception as e:
        print(f"Error during performance test: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == '__main__':
    main()
