import pymysql
import threading
import time
import os
from rich.live import Live
from rich.table import Table
from rich.text import Text

DB_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
DB_USER = os.environ.get("MYSQL_USER", "root")
DB_PASSWORD = os.environ.get("MYSQL_PASSWORD", "rootpassword123")
DB_NAME = os.environ.get("MYSQL_DATABASE", "business_db")

def get_conn():
    conn = pymysql.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME,
        autocommit=False, cursorclass=pymysql.cursors.DictCursor
    )
    with conn.cursor() as cursor:
        # 设置较短的锁等待超时时间，方便演示阻塞报错而不是长时间挂起
        cursor.execute("SET SESSION innodb_lock_wait_timeout = 3;")
    return conn

def setup_db():
    conn = get_conn()
    conn.autocommit(True)
    with conn.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS lock_demo")
        cursor.execute("""
            CREATE TABLE lock_demo (
                id INT PRIMARY KEY,
                val INT NOT NULL,
                unindexed_val INT NOT NULL,
                version INT DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        for i in [10, 20, 30, 40]:
            cursor.execute("INSERT INTO lock_demo (id, val, unindexed_val) VALUES (%s, %s, %s)", (i, i, i))
    conn.close()
    print("✅ 数据库表 lock_demo 初始化完成，初始数据: id=[10, 20, 30, 40]")

class TxMonitor:
    def __init__(self, title, tx_names):
        self.title = title
        self.tx_names = tx_names
        self.state = {name: {"status": "Ready", "action": "-", "color": "white"} for name in tx_names}
        self.lock = threading.Lock()
        self.live = Live(self.generate_table(), refresh_per_second=10)

    def generate_table(self):
        table = Table(title=self.title, show_header=True, header_style="bold magenta")
        table.add_column("Transaction", style="cyan", width=15)
        table.add_column("Status", width=15)
        table.add_column("Current Action / SQL", style="green")
        
        for name in self.tx_names:
            info = self.state[name]
            status_text = Text(info["status"], style=info["color"])
            table.add_row(name, status_text, info["action"])
        return table

    def update(self, tx_name, status, action, color="white"):
        with self.lock:
            if tx_name in self.state:
                self.state[tx_name] = {"status": status, "action": action, "color": color}
            self.live.update(self.generate_table())

    def start(self):
        self.live.start()

    def stop(self):
        self.live.stop()

def run_tx(monitor, tx_name, sql_list, sleep_after_begin=0, sleep_between=0):
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            monitor.update(tx_name, "Executing", "BEGIN;", "yellow")
            cursor.execute("BEGIN;")
            if sleep_after_begin:
                monitor.update(tx_name, "Sleeping", f"Sleep {sleep_after_begin}s", "cyan")
                time.sleep(sleep_after_begin)
            
            for sql in sql_list:
                monitor.update(tx_name, "Executing", sql, "yellow")
                cursor.execute(sql)
                if sleep_between:
                    monitor.update(tx_name, "Sleeping", f"Sleep {sleep_between}s", "cyan")
                    time.sleep(sleep_between)
            
            monitor.update(tx_name, "Committing", "COMMIT;", "yellow")
            conn.commit()
            monitor.update(tx_name, "Success", "事务提交成功", "green")
    except pymysql.err.OperationalError as e:
        err_msg = str(e)
        if "Lock wait timeout" in err_msg:
            monitor.update(tx_name, "Timeout", "锁等待超时 (被阻塞)", "red")
        elif "Deadlock found" in err_msg:
            monitor.update(tx_name, "Deadlock", "发生死锁，被回滚", "red")
        else:
            monitor.update(tx_name, "Error", err_msg, "red")
        conn.rollback()
    finally:
        conn.close()

def scenario_1_row_lock():
    print("\n--- 场景 1: 行锁 (Row Lock) ---")
    print("说明: 事务A锁定 id=10 的行，事务B尝试更新 id=10 会被阻塞超时，但事务C更新 id=20 会立即成功。")
    
    monitor = TxMonitor("场景 1: 行锁 (Row Lock)", ["事务A", "事务B", "事务C"])
    monitor.start()
    
    def tx_a():
        run_tx(monitor, "事务A", ["SELECT * FROM lock_demo WHERE id = 10 FOR UPDATE;"], sleep_between=4)
        
    def tx_b():
        time.sleep(0.5) # 确保A先执行
        run_tx(monitor, "事务B", ["UPDATE lock_demo SET val = 11 WHERE id = 10;"])
        
    def tx_c():
        time.sleep(0.5)
        run_tx(monitor, "事务C", ["UPDATE lock_demo SET val = 21 WHERE id = 20;"])

    t1 = threading.Thread(target=tx_a)
    t2 = threading.Thread(target=tx_b)
    t3 = threading.Thread(target=tx_c)
    
    t1.start(); t2.start(); t3.start()
    t1.join(); t2.join(); t3.join()
    monitor.stop()

def scenario_2_gap_lock():
    print("\n--- 场景 2: 间隙锁 (Gap Lock) ---")
    print("说明: 事务A锁定 id BETWEEN 15 AND 25，这会锁定 (10, 20], (20, 30] 的间隙。事务B尝试插入 id=18 会被阻塞。")
    
    monitor = TxMonitor("场景 2: 间隙锁 (Gap Lock)", ["事务A", "事务B"])
    monitor.start()
    
    def tx_a():
        run_tx(monitor, "事务A", ["SELECT * FROM lock_demo WHERE id BETWEEN 15 AND 25 FOR UPDATE;"], sleep_between=4)
        
    def tx_b():
        time.sleep(0.5)
        run_tx(monitor, "事务B", ["INSERT INTO lock_demo (id, val, unindexed_val) VALUES (18, 18, 18);"])

    t1 = threading.Thread(target=tx_a)
    t2 = threading.Thread(target=tx_b)
    t1.start(); t2.start()
    t1.join(); t2.join()
    monitor.stop()

def scenario_3_table_lock():
    print("\n--- 场景 3: 索引失效导致表锁 (Index Failure -> Table Lock) ---")
    print("说明: 事务A根据无索引字段 unindexed_val 更新数据，导致全表扫描，行锁升级为表锁。事务B更新其他行也会被阻塞。")
    
    monitor = TxMonitor("场景 3: 索引失效导致表锁", ["事务A", "事务B"])
    monitor.start()
    
    def tx_a():
        run_tx(monitor, "事务A", ["UPDATE lock_demo SET val = 99 WHERE unindexed_val = 10;"], sleep_between=4)
        
    def tx_b():
        time.sleep(0.5)
        run_tx(monitor, "事务B", ["UPDATE lock_demo SET val = 88 WHERE id = 20;"])

    t1 = threading.Thread(target=tx_a)
    t2 = threading.Thread(target=tx_b)
    t1.start(); t2.start()
    t1.join(); t2.join()
    monitor.stop()

def scenario_4_deadlock():
    print("\n--- 场景 4: 死锁 (Deadlock) ---")
    print("说明: 事务A锁定 id=10，事务B锁定 id=20。然后A尝试锁定20，B尝试锁定10，形成死锁。MySQL会自动检测并回滚其中一个。")
    
    monitor = TxMonitor("场景 4: 死锁 (Deadlock)", ["事务A", "事务B"])
    monitor.start()
    
    def tx_a():
        run_tx(monitor, "事务A", [
            "UPDATE lock_demo SET val = 1 WHERE id = 10;",
            "UPDATE lock_demo SET val = 1 WHERE id = 20;"
        ], sleep_between=1)
        
    def tx_b():
        run_tx(monitor, "事务B", [
            "UPDATE lock_demo SET val = 2 WHERE id = 20;",
            "UPDATE lock_demo SET val = 2 WHERE id = 10;"
        ], sleep_between=1)

    t1 = threading.Thread(target=tx_a)
    t2 = threading.Thread(target=tx_b)
    t1.start(); t2.start()
    t1.join(); t2.join()
    monitor.stop()

def scenario_5_optimistic_lock():
    print("\n--- 场景 5: 乐观锁 (Optimistic Lock - 生产推荐) ---")
    print("说明: 不使用数据库锁，而是通过 version 字段控制并发。事务A和B同时读取 version=0，B先更新成功(version=1)，A更新时发现 version!=0，更新失败(影响行数为0)。")
    
    monitor = TxMonitor("场景 5: 乐观锁", ["事务A", "事务B"])
    monitor.start()
    
    def tx_a():
        conn = get_conn()
        conn.autocommit(True)
        try:
            with conn.cursor() as cursor:
                monitor.update("事务A", "Executing", "SELECT version FROM lock_demo WHERE id = 30;", "yellow")
                cursor.execute("SELECT version FROM lock_demo WHERE id = 30;")
                version = cursor.fetchone()['version']
                monitor.update("事务A", "Sleeping", f"读取到 version={version}, 模拟耗时", "cyan")
                time.sleep(1) # 模拟业务处理耗时，让B先执行完
                
                sql = f"UPDATE lock_demo SET val = 31, version = version + 1 WHERE id = 30 AND version = {version};"
                monitor.update("事务A", "Executing", sql, "yellow")
                affected = cursor.execute(sql)
                if affected == 0:
                    monitor.update("事务A", "Failed", "更新失败(乐观锁生效)", "red")
                else:
                    monitor.update("事务A", "Success", "更新成功", "green")
        finally:
            conn.close()
        
    def tx_b():
        time.sleep(0.2)
        conn = get_conn()
        conn.autocommit(True)
        try:
            with conn.cursor() as cursor:
                monitor.update("事务B", "Executing", "SELECT version FROM lock_demo WHERE id = 30;", "yellow")
                cursor.execute("SELECT version FROM lock_demo WHERE id = 30;")
                version = cursor.fetchone()['version']
                monitor.update("事务B", "Ready", f"读取到 version={version}", "cyan")
                
                sql = f"UPDATE lock_demo SET val = 32, version = version + 1 WHERE id = 30 AND version = {version};"
                monitor.update("事务B", "Executing", sql, "yellow")
                affected = cursor.execute(sql)
                if affected == 0:
                    monitor.update("事务B", "Failed", "更新失败", "red")
                else:
                    monitor.update("事务B", "Success", "更新成功", "green")
        finally:
            conn.close()

    t1 = threading.Thread(target=tx_a)
    t2 = threading.Thread(target=tx_b)
    t1.start(); t2.start()
    t1.join(); t2.join()
    monitor.stop()

if __name__ == "__main__":
    setup_db()
    scenario_1_row_lock()
    time.sleep(1)
    scenario_2_gap_lock()
    time.sleep(1)
    scenario_3_table_lock()
    time.sleep(1)
    scenario_4_deadlock()
    time.sleep(1)
    scenario_5_optimistic_lock()
    print("\n🎉 所有锁场景演示完毕！")