-- Batch Insert Script
-- Usage: Call this stored procedure to insert specified number of records
-- Example: CALL InsertSampleData(1000);

DELIMITER //

CREATE PROCEDURE InsertSampleData(IN record_count INT)
BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE user_count INT;
    DECLARE product_count INT;
    DECLARE category_count INT;
    
    -- Get current counts
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*) INTO product_count FROM products;
    SELECT COUNT(*) INTO category_count FROM categories;
    
    -- Insert users
    SET i = user_count + 1;
    WHILE i <= user_count + record_count DO
        INSERT INTO users (username, email, password_hash, first_name, last_name, phone, role)
        VALUES (
            CONCAT('user', i),
            CONCAT('user', i, '@example.com'),
            CONCAT('hash_', UUID()),
            CONCAT('First', i),
            CONCAT('Last', i),
            CONCAT('+1-555-', LPAD(i, 4, '0')),
            CASE WHEN i % 10 = 0 THEN 'manager' ELSE 'user' END
        );
        SET i = i + 1;
    END WHILE;
    
    -- Insert products if categories exist
    IF category_count > 0 THEN
        SET i = product_count + 1;
        WHILE i <= product_count + record_count DO
            INSERT INTO products (name, description, sku, category_id, price, cost_price, stock_quantity, weight)
            VALUES (
                CONCAT('Product ', i),
                CONCAT('Description for product ', i, '. This is a sample product with detailed description.'),
                CONCAT('SKU-', LPAD(i, 6, '0')),
                (SELECT id FROM categories ORDER BY RAND() LIMIT 1),
                ROUND(RAND() * 1000 + 10, 2),
                ROUND(RAND() * 800 + 5, 2),
                FLOOR(RAND() * 1000),
                ROUND(RAND() * 10, 2)
            );
            SET i = i + 1;
        END WHILE;
    END IF;
    
    -- Insert orders if users and products exist
    IF user_count + record_count > 0 AND product_count + record_count > 0 THEN
        SET i = 0;
        WHILE i < record_count / 2 DO
            INSERT INTO orders (order_number, user_id, total_amount, status, payment_status, shipping_address)
            VALUES (
                CONCAT('ORD-', DATE_FORMAT(NOW(), '%Y%m%d'), '-', LPAD(i, 6, '0')),
                (SELECT id FROM users ORDER BY RAND() LIMIT 1),
                ROUND(RAND() * 500 + 50, 2),
                ELT(FLOOR(RAND() * 5) + 1, 'pending', 'confirmed', 'shipped', 'delivered', 'cancelled'),
                ELT(FLOOR(RAND() * 4) + 1, 'pending', 'paid', 'failed', 'refunded'),
                CONCAT('Shipping Address for order ', i)
            );
            
            -- Insert order items for each order
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
            SELECT 
                LAST_INSERT_ID(),
                (SELECT id FROM products ORDER BY RAND() LIMIT 1),
                FLOOR(RAND() * 5) + 1,
                ROUND(RAND() * 100 + 10, 2),
                quantity * unit_price
            FROM (SELECT 1) t;
            
            SET i = i + 1;
        END WHILE;
    END IF;
    
    -- Insert inventory transactions if products exist
    IF product_count + record_count > 0 THEN
        SET i = 0;
        WHILE i < record_count DO
            INSERT INTO inventory_transactions (product_id, transaction_type, quantity, reference_type, notes)
            VALUES (
                (SELECT id FROM products ORDER BY RAND() LIMIT 1),
                ELT(FLOOR(RAND() * 3) + 1, 'in', 'out', 'adjustment'),
                FLOOR(RAND() * 100) + 1,
                ELT(FLOOR(RAND() * 4) + 1, 'order', 'purchase', 'adjustment', 'return'),
                CONCAT('Transaction note for record ', i)
            );
            SET i = i + 1;
        END WHILE;
    END IF;
    
    SELECT 
        CONCAT('Inserted ', record_count, ' records successfully.') AS result,
        (SELECT COUNT(*) FROM users) AS total_users,
        (SELECT COUNT(*) FROM products) AS total_products,
        (SELECT COUNT(*) FROM orders) AS total_orders,
        (SELECT COUNT(*) FROM inventory_transactions) AS total_transactions;
END //

DELIMITER ;

-- Quick insert function for smaller batches
DELIMITER //

CREATE PROCEDURE QuickInsert(IN table_name VARCHAR(50), IN count INT)
BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE base_count INT;
    
    CASE table_name
        WHEN 'users' THEN
            SELECT COUNT(*) INTO base_count FROM users;
            SET i = base_count + 1;
            WHILE i <= base_count + count DO
                INSERT INTO users (username, email, password_hash, first_name, last_name)
                VALUES (
                    CONCAT('quickuser', i),
                    CONCAT('quickuser', i, '@example.com'),
                    CONCAT('quick_hash_', UUID()),
                    CONCAT('QuickFirst', i),
                    CONCAT('QuickLast', i)
                );
                SET i = i + 1;
            END WHILE;
            
        WHEN 'products' THEN
            SELECT COUNT(*) INTO base_count FROM products;
            SET i = base_count + 1;
            WHILE i <= base_count + count DO
                INSERT INTO products (name, sku, price, stock_quantity)
                VALUES (
                    CONCAT('Quick Product ', i),
                    CONCAT('QSKU-', LPAD(i, 6, '0')),
                    ROUND(RAND() * 100 + 10, 2),
                    FLOOR(RAND() * 100)
                );
                SET i = i + 1;
            END WHILE;
    END CASE;
    
    SELECT CONCAT('Inserted ', count, ' records into ', table_name) AS result;
END //

DELIMITER ;

-- Usage examples commented out
-- CALL InsertSampleData(1000);  -- Insert 1000 records across all tables
-- CALL QuickInsert('users', 100);  -- Quickly insert 100 users
-- CALL QuickInsert('products', 50);  -- Quickly insert 50 products