-- This file is now handled by setup-replication.sh script
-- The shell script will handle replication setup after master is ready

-- Create replication user if not exists (for master connection)
CREATE USER IF NOT EXISTS 'repl'@'%' IDENTIFIED BY 'replpassword123';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
FLUSH PRIVILEGES;

-- Configure replication source
CHANGE REPLICATION SOURCE TO 
  SOURCE_HOST='mysql-master', 
  SOURCE_USER='repl', 
  SOURCE_PASSWORD='replpassword123', 
  SOURCE_AUTO_POSITION=1,
  GET_SOURCE_PUBLIC_KEY=1;

-- Set slave to read-only mode
SET PERSIST read_only = 1;
SET PERSIST super_read_only = 1;

-- Show current configuration for debugging
SHOW VARIABLES LIKE 'server_id';
SHOW VARIABLES LIKE 'log_bin';
SHOW VARIABLES LIKE 'gtid_mode';