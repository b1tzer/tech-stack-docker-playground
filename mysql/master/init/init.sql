-- Create replication user for slave connection
CREATE USER IF NOT EXISTS 'repl'@'%' IDENTIFIED BY 'replpassword123';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
FLUSH PRIVILEGES;

-- Show master status for replication setup
SHOW MASTER STATUS;

-- Show replication configuration
SHOW VARIABLES LIKE 'server_id';
SHOW VARIABLES LIKE 'log_bin';
SHOW VARIABLES LIKE 'gtid_mode';
SHOW MASTER STATUS;