# MySQL Master-Slave Replication with Docker Compose

A complete Docker Compose setup for MySQL master-slave replication with rich business database schema and batch data insertion capabilities.

## Features

- **Master-Slave Replication**: Full MySQL 8.0 replication setup
- **Rich Business Schema**: Comprehensive tables for users, products, orders, inventory, and payments
- **Batch Data Insertion**: Stored procedures for inserting large volumes of test data
- **External Access**: Both master and slave accessible from host machine
- **Persistent Data**: Data volumes for data persistence
- **GTID Replication**: Modern GTID-based replication configuration

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 2GB of available memory
- `make` utility installed

### 1. Start the Services
```bash
# Initialize and start the cluster
make start
```

### 2. Check Status
```bash
# Check cluster and replication status
make status
```

## Connection Details

| Service | Host | Port | Database | Username | Password |
|---------|------|------|----------|----------|----------|
| Master | localhost | 3306 | business_db | app_user | userpassword123 |
| Slave | localhost | 3307 | business_db | app_user | userpassword123 |
| Root Access | localhost | 3306/3307 | - | root | rootpassword123 |

## Database Schema

### Core Tables
- **users**: User accounts with roles and authentication
- **products**: Product catalog with inventory management
- **categories**: Product categorization with hierarchical support
- **orders**: Order management with status tracking
- **order_items**: Order line items with pricing
- **inventory_transactions**: Inventory movement tracking
- **payments**: Payment processing records

### Views
- **product_inventory_view**: Real-time inventory calculations

### Stored Procedures
- **InsertSampleData(N)**: Insert N records across all tables
- **QuickInsert(table, count)**: Quick insertion into specific tables

## Data Seeding (Python Faker)

The project includes a Python-based data seeder that generates realistic, meaningful business data (names, addresses, products, etc.) using the `Faker` library.

### Generate Sample Data
```bash
# Seed 100 records per table (default)
make seed

# Seed a specific number of records (e.g., 500)
make seed COUNT=500
```
*Note: The seeder runs in a temporary Docker container, so you don't need Python installed on your host machine.*

## Replication Monitoring

### Check Master Status
```sql
SHOW MASTER STATUS;
SHOW BINARY LOGS;
SHOW SLAVE HOSTS;
```

### Check Slave Status
```sql
SHOW SLAVE STATUS\G
SHOW SLAVE HOSTS;
```

### Using Docker Commands
```bash
# Master status
docker exec mysql-master mysql -uroot -prootpassword123 -e "SHOW MASTER STATUS;"

# Slave status
docker exec mysql-slave mysql -uroot -prootpassword123 -e "SHOW SLAVE STATUS\G"
```

## Configuration Files

### Master Configuration (`master/conf/my.cnf`)
- Server ID: 1
- Binary logging enabled
- GTID replication
- Performance optimizations

### Slave Configuration (`slave/conf/my.cnf`)
- Server ID: 2
- Read-only mode
- Relay logging
- GTID replication

### Environment Variables (`.env`)
- Database credentials
- Network settings
- Replication parameters

## Management Commands

The project uses a `Makefile` to simplify all management operations.

```bash
# Start the cluster
make start

# Stop the cluster
make stop

# Stop the cluster and remove all data volumes
make clean

# Clean and then start the cluster (useful for development)
make reset

# View cluster logs
make logs

# Check cluster and replication status
make status
```

### Data Backup
```bash
# Backup master database
docker exec mysql-master mysqldump -uroot -prootpassword123 business_db > backup.sql

# Backup slave database
docker exec mysql-slave mysqldump -uroot -prootpassword123 business_db > backup_slave.sql
```

### Data Restoration
```bash
# Restore to master
docker exec -i mysql-master mysql -uroot -prootpassword123 business_db < backup.sql
```

## Troubleshooting

### Replication Issues
1. Check if slave is running: `make status` or `SHOW SLAVE STATUS\G`
2. If stopped, restart: `START SLAVE;`
3. Reset replication if needed: `RESET SLAVE;` then reconfigure

### Connection Issues
1. Verify ports 3306 and 3307 are available
2. Check Docker container status: `make status`
3. View logs: `make logs`

### Performance Issues
1. Monitor resource usage: `docker stats`
2. Adjust buffer sizes in configuration files
3. Consider increasing Docker memory allocation

## File Structure
```
├── docker-compose.yml          # Main Docker Compose configuration
├── .env                        # Environment variables
├── Makefile                    # Project management commands
├── init-database.sql           # Database schema initialization
├── batch-insert.sql            # Batch data insertion procedures
├── seeder/                     # Python Faker data generator
│   ├── seed.py                 # Seeder script
│   └── requirements.txt        # Python dependencies
├── README.md                   # This file
├── master/                     # Master database configuration
│   ├── conf/my.cnf             # Master MySQL configuration
│   └── init/init.sql           # Master initialization script
└── slave/                      # Slave database configuration
    ├── conf/my.cnf             # Slave MySQL configuration
    └── init/init.sql           # Slave initialization script
```

## Security Notes

- Change default passwords in `.env` file for production use
- Consider using Docker secrets for sensitive information
- Configure firewall rules for external access
- Regularly update MySQL images for security patches

## Performance Considerations

- Adjust `innodb_buffer_pool_size` based on available memory
- Monitor replication lag with `SHOW SLAVE STATUS`
- Consider using MySQL 8.0's performance schema for monitoring
- Use connection pooling for application connections

## License

This configuration is provided as-is for development and testing purposes.