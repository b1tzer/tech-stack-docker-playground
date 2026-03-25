import os
import argparse
from faker import Faker
import random
import uuid
from db_utils import get_db_connection

# Initialize Faker with multiple locales for diverse data
fake = Faker(['zh_CN', 'en_US'])

def seed_users(cursor, connection, count, batch_size=5000):
    print(f"Seeding {count} users in batches of {batch_size} (Fast Method)...")
    sql = """
        INSERT IGNORE INTO users 
        (username, email, password_hash, first_name, last_name, phone, status, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = []
    for i in range(count):
        # Use uuid to ensure unique username and email even on repeated runs
        unique_id = str(uuid.uuid4())[:8]
        username = f"{fake.user_name()}_{unique_id}"
        email = f"{unique_id}_{fake.email()}"
        data.append((
            username,
            email,
            fake.sha256(),
            fake.first_name(),
            fake.last_name(),
            fake.phone_number()[:20],
            random.choice(['active', 'active', 'active', 'inactive', 'suspended']),
            random.choice(['user', 'user', 'user', 'manager', 'admin'])
        ))
        
        if len(data) >= batch_size:
            cursor.executemany(sql, data)
            connection.commit()
            print(f"  -> Inserted {i + 1} users...")
            data = []
            
    if data:
        cursor.executemany(sql, data)
        connection.commit()
        print(f"  -> Inserted {count} users...")

def seed_categories(cursor, connection, count):
    print(f"Seeding {count} categories...")
    sql = """
        INSERT INTO categories (name, description, parent_id, sort_order, is_active)
        VALUES (%s, %s, %s, %s, %s)
    """
    # First, insert some root categories
    root_categories = [
        ('Electronics', 'Electronic devices and accessories'),
        ('Clothing', 'Clothing and fashion items'),
        ('Books', 'Books and educational materials'),
        ('Home & Garden', 'Home improvement and garden supplies'),
        ('Sports', 'Sports equipment and apparel'),
        ('Toys', 'Toys and games for children'),
        ('Beauty', 'Beauty and personal care products'),
        ('Automotive', 'Automotive parts and accessories')
    ]
    
    # Insert root categories if they don't exist
    cursor.execute("SELECT COUNT(*) as cnt FROM categories WHERE parent_id IS NULL")
    if cursor.fetchone()['cnt'] == 0:
        for i, (name, desc) in enumerate(root_categories):
            cursor.execute(sql, (name, desc, None, i + 1, True))
        connection.commit()
    
    # Get root category IDs and names
    cursor.execute("SELECT id, name FROM categories WHERE parent_id IS NULL")
    roots = cursor.fetchall()
    
    if not roots:
        return

    # Meaningful subcategories mapped to root categories
    subcategories_map = {
        'Electronics': ['Smartphones', 'Laptops', 'Tablets', 'Audio', 'Cameras', 'Wearables', 'Networking', 'PC Components'],
        'Clothing': ['Men\'s Wear', 'Women\'s Wear', 'Kids', 'Shoes', 'Accessories', 'Activewear', 'Outerwear', 'Underwear'],
        'Books': ['Fiction', 'Non-Fiction', 'Science', 'History', 'Technology', 'Children\'s Books', 'Biographies', 'Cookbooks'],
        'Home & Garden': ['Furniture', 'Decor', 'Kitchen', 'Bedding', 'Bath', 'Gardening Tools', 'Outdoor Furniture', 'Lighting'],
        'Sports': ['Fitness', 'Team Sports', 'Outdoor Recreation', 'Cycling', 'Water Sports', 'Winter Sports', 'Golf', 'Racket Sports'],
        'Toys': ['Action Figures', 'Building Blocks', 'Dolls', 'Board Games', 'Educational', 'Remote Control', 'Puzzles', 'Arts & Crafts'],
        'Beauty': ['Skincare', 'Makeup', 'Haircare', 'Fragrance', 'Bath & Body', 'Men\'s Grooming', 'Tools & Accessories', 'Oral Care'],
        'Automotive': ['Car Care', 'Interior Accessories', 'Exterior Accessories', 'Tools & Equipment', 'Replacement Parts', 'Motorcycle', 'RV Parts', 'Tires & Wheels']
    }

    # Generate subcategories
    data = []
    inserted_count = 0
    
    # First, ensure we insert the meaningful subcategories
    for root in roots:
        root_id = root['id']
        root_name = root['name']
        
        if root_name in subcategories_map:
            for i, sub_name in enumerate(subcategories_map[root_name]):
                if inserted_count >= count:
                    break
                desc = f"{sub_name} products in the {root_name} category"
                data.append((sub_name, desc, root_id, i + 1, True))
                inserted_count += 1
                
        if inserted_count >= count:
            break
            
    # If we still need more categories, generate some random but plausible ones
    while inserted_count < count:
        root = random.choice(roots)
        root_id = root['id']
        root_name = root['name']
        
        # Generate a plausible subcategory name using Faker
        adjective = fake.word(ext_word_list=['Premium', 'Basic', 'Advanced', 'Professional', 'Eco-friendly', 'Smart', 'Vintage', 'Modern']).capitalize()
        noun = fake.word().capitalize()
        sub_name = f"{adjective} {noun} {root_name}"
        desc = fake.sentence()
        
        data.append((sub_name, desc, root_id, random.randint(1, 100), random.choice([True, True, False])))
        inserted_count += 1
        
        if len(data) >= 5000:
            cursor.executemany(sql, data)
            connection.commit()
            data = []
            
    if data:
        cursor.executemany(sql, data)
        connection.commit()
    print(f"  -> Inserted {count} subcategories...")

def seed_products(cursor, connection, count, batch_size=5000):
    print(f"Seeding {count} products in batches of {batch_size}...")
    # Get existing categories
    cursor.execute("SELECT id FROM categories")
    categories = [row['id'] for row in cursor.fetchall()]
    if not categories:
        print("No categories found. Skipping products.")
        return

    sql = """
        INSERT IGNORE INTO products 
        (name, description, sku, category_id, price, cost_price, stock_quantity, weight, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = []
    for i in range(count):
        unique_id = str(uuid.uuid4())[:8]
        sku = f"SKU-{fake.ean(length=8)}-{unique_id}"
        price = round(random.uniform(10.0, 1000.0), 2)
        cost_price = round(price * random.uniform(0.4, 0.8), 2)
        data.append((
            f"{fake.word().capitalize()} {fake.word().capitalize()}",
            fake.text(max_nb_chars=200),
            sku,
            random.choice(categories),
            price,
            cost_price,
            random.randint(0, 1000),
            round(random.uniform(0.1, 50.0), 2),
            random.choice(['active', 'active', 'inactive', 'discontinued'])
        ))
        
        if len(data) >= batch_size:
            cursor.executemany(sql, data)
            connection.commit()
            print(f"  -> Inserted {i + 1} products...")
            data = []
            
    if data:
        cursor.executemany(sql, data)
        connection.commit()
        print(f"  -> Inserted {count} products...")
 
def seed_inventory_transactions(cursor, connection, count, batch_size=5000):
    print(f"Seeding {count} inventory transactions in batches of {batch_size}...")
    cursor.execute("SELECT id FROM products")
    products = [row['id'] for row in cursor.fetchall()]
    cursor.execute("SELECT id FROM users WHERE role IN ('admin', 'manager')")
    users = [row['id'] for row in cursor.fetchall()]
    
    if not products or not users:
        print("Not enough products or users. Skipping inventory transactions.")
        return

    sql = """
        INSERT INTO inventory_transactions 
        (product_id, transaction_type, quantity, reference_type, reference_id, notes, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    data = []
    for i in range(count):
        product_id = random.choice(products)
        transaction_type = random.choice(['in', 'out', 'adjustment'])
        quantity = random.randint(1, 100)
        reference_type = random.choice(['order', 'purchase', 'adjustment', 'return'])
        reference_id = random.randint(1, 10000)
        notes = fake.sentence()
        created_by = random.choice(users)
        
        data.append((
            product_id,
            transaction_type,
            quantity,
            reference_type,
            reference_id,
            notes,
            created_by
        ))
        
        if len(data) >= batch_size:
            cursor.executemany(sql, data)
            connection.commit()
            print(f"  -> Inserted {i + 1} inventory transactions...")
            data = []
            
    if data:
        cursor.executemany(sql, data)
        connection.commit()
        print(f"  -> Inserted {count} inventory transactions...")

def seed_orders(cursor, connection, count, batch_size=2000):
    print(f"Seeding {count} orders in batches of {batch_size}...")
    cursor.execute("SELECT id FROM users")
    users = [row['id'] for row in cursor.fetchall()]
    cursor.execute("SELECT id, price FROM products WHERE status = 'active'")
    products = cursor.fetchall()
    
    if not users or not products:
        print("Not enough users or products. Skipping orders.")
        return

    order_sql = """
        INSERT IGNORE INTO orders 
        (order_number, user_id, total_amount, status, payment_status, shipping_address)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    item_sql = """
        INSERT INTO order_items 
        (order_id, product_id, quantity, unit_price, total_price)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    for i in range(count):
        unique_id = str(uuid.uuid4())[:8]
        order_number = f"ORD-{fake.date_this_year().strftime('%Y%m%d')}-{unique_id}"
        user_id = random.choice(users)
        
        # Pick 1 to 5 random products for this order
        num_items = random.randint(1, 5)
        order_items = random.sample(products, min(num_items, len(products)))
        
        total_amount = 0
        items_data = []
        for p in order_items:
            qty = random.randint(1, 5)
            unit_price = float(p['price'])
            total_price = qty * unit_price
            total_amount += total_price
            items_data.append((p['id'], qty, unit_price, total_price))
            
        # Insert order
        cursor.execute(order_sql, (
            order_number,
            user_id,
            total_amount,
            random.choice(['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']),
            random.choice(['pending', 'paid', 'failed', 'refunded']),
            fake.address()
        ))
        
        order_id = cursor.lastrowid
        if order_id:
            # Insert items
            final_items_data = [(order_id, *item) for item in items_data]
            cursor.executemany(item_sql, final_items_data)
            
        # Commit periodically to avoid massive transactions
        if (i + 1) % batch_size == 0:
            connection.commit()
            print(f"  -> Inserted {i + 1} orders...")
            
    connection.commit()
    print(f"  -> Inserted {count} orders...")

def seed_payments(cursor, connection, count, batch_size=5000):
    print(f"Seeding {count} payments in batches of {batch_size}...")
    cursor.execute("SELECT id, total_amount FROM orders WHERE status IN ('confirmed', 'shipped', 'delivered')")
    orders = cursor.fetchall()
    
    if not orders:
        print("Not enough confirmed orders. Skipping payments.")
        return

    sql = """
        INSERT INTO payments 
        (order_id, payment_method, amount, transaction_id, status, payment_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    data = []
    for i in range(count):
        order = random.choice(orders)
        order_id = order['id']
        amount = order['total_amount']
        payment_method = random.choice(['credit_card', 'debit_card', 'paypal', 'bank_transfer'])
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        status = random.choice(['pending', 'completed', 'failed', 'refunded'])
        payment_date = fake.date_time_this_year() if status == 'completed' else None
        
        data.append((
            order_id,
            payment_method,
            amount,
            transaction_id,
            status,
            payment_date
        ))
        
        if len(data) >= batch_size:
            cursor.executemany(sql, data)
            connection.commit()
            print(f"  -> Inserted {i + 1} payments...")
            data = []
            
    if data:
        cursor.executemany(sql, data)
        connection.commit()
        print(f"  -> Inserted {count} payments...")

import time

def main():
    parser = argparse.ArgumentParser(description='Seed database with meaningful data.')
    parser.add_argument('count', type=int, nargs='?', default=100, help='Number of records to generate per table')
    args = parser.parse_args()

    # Safety check for extreme values
    if args.count > 500000:
        print("\n" + "!"*60)
        print("🚨 CRITICAL WARNING: MASSIVE DATA INSERTION DETECTED 🚨")
        print("!"*60)
        print(f"You are attempting to insert {args.count} records per table.")
        print("This is an EXTREMELY large amount of data for a local test environment.")
        print("\n⚠️  POTENTIAL CONSEQUENCES:")
        print("1. Your computer may become completely unresponsive (freeze/hang).")
        print("2. Docker may consume all available RAM and crash.")
        print("3. The MySQL container may run out of memory (OOM killed).")
        print("4. Your hard drive may run out of space due to massive transaction logs.")
        print("\n💡 RECOMMENDATION:")
        print("For a typical 8GB/16GB RAM machine, keep the count under 200,000.")
        print("If you really want to test this, ensure you have at least 32GB RAM and SSD storage.")
        print("\nPress Ctrl+C within 10 seconds to abort, or wait to proceed at your own risk...")
        try:
            for i in range(10, 0, -1):
                print(f"Proceeding in {i} seconds...", end="\r", flush=True)
                time.sleep(1)
            print("\nProceeding with massive insertion...")
        except KeyboardInterrupt:
            print("\nAborted by user. Good choice! 👍")
            return

    connection = get_db_connection(max_retries=10, delay=5)
    try:
        with connection.cursor() as cursor:
            # Check if data already exists to prevent double seeding on restart
            cursor.execute("SELECT COUNT(*) as cnt FROM users")
            if cursor.fetchone()['cnt'] > 0:
                print("Data already exists. Skipping seeding.")
                return

            seed_users(cursor, connection, args.count)
            seed_categories(cursor, connection, max(1, args.count // 10))
            seed_products(cursor, connection, args.count)
            seed_inventory_transactions(cursor, connection, args.count)
            # Generate fewer orders than users/products to keep it realistic
            seed_orders(cursor, connection, max(1, args.count // 2))
            seed_payments(cursor, connection, max(1, args.count // 2))
            print("Data seeding completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == '__main__':
    main()
