import pytest
from unittest.mock import MagicMock, patch
import os
import sys

# Add parent directory to path to import seed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from seed import (
    seed_users,
    seed_categories,
    seed_products,
    seed_inventory_transactions,
    seed_orders,
    seed_payments
)

@pytest.fixture
def mock_db():
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    return connection, cursor

def test_seed_users(mock_db):
    connection, cursor = mock_db
    count = 10
    batch_size = 5
    
    seed_users(cursor, connection, count, batch_size)
    
    # Should call executemany twice (10 / 5 = 2 batches)
    assert cursor.executemany.call_count == 2
    assert connection.commit.call_count == 2
    
    # Verify the SQL and data structure of the first call
    args, kwargs = cursor.executemany.call_args_list[0]
    sql, data = args
    assert "INSERT IGNORE INTO users" in sql
    assert len(data) == 5
    assert len(data[0]) == 8 # 8 columns

def test_seed_categories(mock_db):
    connection, cursor = mock_db
    count = 5
    
    # Mock the check for existing root categories
    cursor.fetchone.return_value = {'cnt': 0}
    # Mock the fetch of root categories
    cursor.fetchall.return_value = [
        {'id': 1, 'name': 'Electronics'},
        {'id': 2, 'name': 'Clothing'}
    ]
    
    seed_categories(cursor, connection, count)
    
    # Should insert root categories (8 of them)
    assert cursor.execute.call_count > 0
    # Should insert subcategories
    assert cursor.executemany.call_count == 1
    
    args, kwargs = cursor.executemany.call_args
    sql, data = args
    assert "INSERT INTO categories" in sql
    assert len(data) == count

def test_seed_products(mock_db):
    connection, cursor = mock_db
    count = 10
    batch_size = 5
    
    # Mock existing categories
    cursor.fetchall.return_value = [{'id': 1}, {'id': 2}]
    
    seed_products(cursor, connection, count, batch_size)
    
    assert cursor.executemany.call_count == 2
    assert connection.commit.call_count == 2
    
    args, kwargs = cursor.executemany.call_args_list[0]
    sql, data = args
    assert "INSERT IGNORE INTO products" in sql
    assert len(data) == 5
    assert len(data[0]) == 9 # 9 columns

def test_seed_inventory_transactions(mock_db):
    connection, cursor = mock_db
    count = 10
    batch_size = 5
    
    # Mock existing products and users
    cursor.fetchall.side_effect = [
        [{'id': 1}, {'id': 2}], # products
        [{'id': 1}, {'id': 2}]  # users
    ]
    
    seed_inventory_transactions(cursor, connection, count, batch_size)
    
    assert cursor.executemany.call_count == 2
    assert connection.commit.call_count == 2
    
    args, kwargs = cursor.executemany.call_args_list[0]
    sql, data = args
    assert "INSERT INTO inventory_transactions" in sql
    assert len(data) == 5
    assert len(data[0]) == 7 # 7 columns

def test_seed_orders(mock_db):
    connection, cursor = mock_db
    count = 10
    batch_size = 5
    
    # Mock existing users and products
    cursor.fetchall.side_effect = [
        [{'id': 1}, {'id': 2}], # users
        [{'id': 1, 'price': 10.0}, {'id': 2, 'price': 20.0}] # products
    ]
    # Mock lastrowid for order insertion
    cursor.lastrowid = 1
    
    seed_orders(cursor, connection, count, batch_size)
    
    # Should execute order insert 10 times + 2 initial selects
    assert cursor.execute.call_count == 12
    # Should execute order items insert 10 times
    assert cursor.executemany.call_count == 10
    # Should commit twice (10 / 5 = 2 batches) + 1 final commit
    assert connection.commit.call_count == 3

def test_seed_payments(mock_db):
    connection, cursor = mock_db
    count = 10
    batch_size = 5
    
    # Mock existing orders
    cursor.fetchall.return_value = [
        {'id': 1, 'total_amount': 100.0},
        {'id': 2, 'total_amount': 200.0}
    ]
    
    seed_payments(cursor, connection, count, batch_size)
    
    assert cursor.executemany.call_count == 2
    assert connection.commit.call_count == 2
    
    args, kwargs = cursor.executemany.call_args_list[0]
    sql, data = args
    assert "INSERT INTO payments" in sql
    assert len(data) == 5
    assert len(data[0]) == 6 # 6 columns