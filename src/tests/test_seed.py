import pytest
from unittest.mock import MagicMock, patch
import os
import sys

# Add parent directory to path to import seed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from seeders.main import (
    seed_users,
    seed_categories,
    seed_products,
    seed_inventory_transactions,
    seed_orders,
    seed_payments,
    main
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

def test_seed_categories_large_count(mock_db):
    connection, cursor = mock_db
    count = 6000 # > 5000 to trigger batch insert
    
    # Mock the check for existing root categories
    cursor.fetchone.return_value = {'cnt': 0}
    # Mock the fetch of root categories
    cursor.fetchall.return_value = [
        {'id': 1, 'name': 'Electronics'}
    ]
    
    seed_categories(cursor, connection, count)
    
    # Should insert subcategories in batches
    assert cursor.executemany.call_count == 2 # 5000 + 1000
    # 1 commit for root categories + 2 commits for subcategories
    assert connection.commit.call_count == 3

def test_seed_categories_no_roots(mock_db):
    connection, cursor = mock_db
    count = 5
    
    # Mock the check for existing root categories
    cursor.fetchone.return_value = {'cnt': 0}
    # Mock the fetch of root categories to return empty
    cursor.fetchall.return_value = []
    
    seed_categories(cursor, connection, count)
    
    # Should insert root categories
    assert cursor.execute.call_count > 0
    # Should not insert subcategories
    assert cursor.executemany.call_count == 0

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

def test_seed_products_no_categories(mock_db):
    connection, cursor = mock_db
    count = 10
    batch_size = 5
    
    # Mock no existing categories
    cursor.fetchall.return_value = []
    
    seed_products(cursor, connection, count, batch_size)
    
    assert cursor.executemany.call_count == 0

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

def test_seed_inventory_transactions_no_data(mock_db):
    connection, cursor = mock_db
    count = 10
    batch_size = 5
    
    # Mock no existing products
    cursor.fetchall.side_effect = [
        [], # products
        [{'id': 1}, {'id': 2}]  # users
    ]
    
    seed_inventory_transactions(cursor, connection, count, batch_size)
    
    assert cursor.executemany.call_count == 0

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

def test_seed_orders_no_data(mock_db):
    connection, cursor = mock_db
    count = 10
    batch_size = 5
    
    # Mock no existing users
    cursor.fetchall.side_effect = [
        [], # users
        [{'id': 1, 'price': 10.0}, {'id': 2, 'price': 20.0}] # products
    ]
    
    seed_orders(cursor, connection, count, batch_size)
    
    assert cursor.execute.call_count == 2 # Select users and select products
    assert cursor.executemany.call_count == 0

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

def test_seed_payments_no_data(mock_db):
    connection, cursor = mock_db
    count = 10
    batch_size = 5
    
    # Mock no existing orders
    cursor.fetchall.return_value = []
    
    seed_payments(cursor, connection, count, batch_size)
    
    assert cursor.executemany.call_count == 0

@patch('seeders.main.get_db_connection')
@patch('seeders.main.argparse.ArgumentParser.parse_args')
def test_main_success(mock_parse_args, mock_get_db_connection):
    # Arrange
    mock_args = MagicMock()
    mock_args.count = 100
    mock_parse_args.return_value = mock_args

    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_connection

    # Mock that no data exists
    mock_cursor.fetchone.return_value = {'cnt': 0}
    
    # Mock fetchall for dependencies
    mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'Test', 'price': 10.0, 'total_amount': 100.0}]
    mock_cursor.lastrowid = 1

    # Act
    main()

    # Assert
    mock_get_db_connection.assert_called_once()
    assert mock_cursor.execute.call_count > 0
    mock_connection.close.assert_called_once()

@patch('seeders.main.get_db_connection')
@patch('seeders.main.argparse.ArgumentParser.parse_args')
def test_main_data_exists(mock_parse_args, mock_get_db_connection):
    # Arrange
    mock_args = MagicMock()
    mock_args.count = 100
    mock_parse_args.return_value = mock_args

    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_connection

    # Mock that data already exists
    mock_cursor.fetchone.return_value = {'cnt': 1}

    # Act
    main()

    # Assert
    mock_get_db_connection.assert_called_once()
    mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) as cnt FROM users")
    # Should not call any seed functions
    assert mock_cursor.executemany.call_count == 0
    mock_connection.close.assert_called_once()

@patch('seeders.main.get_db_connection')
@patch('seeders.main.argparse.ArgumentParser.parse_args')
def test_main_exception(mock_parse_args, mock_get_db_connection):
    # Arrange
    mock_args = MagicMock()
    mock_args.count = 100
    mock_parse_args.return_value = mock_args

    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_connection

    # Force an exception
    mock_cursor.execute.side_effect = Exception("Test error")

    # Act
    main()

    # Assert
    mock_connection.rollback.assert_called_once()
    mock_connection.close.assert_called_once()

@patch('seeders.main.time.sleep')
@patch('seeders.main.get_db_connection')
@patch('seeders.main.argparse.ArgumentParser.parse_args')
def test_main_massive_insertion(mock_parse_args, mock_get_db_connection, mock_sleep):
    # Arrange
    mock_args = MagicMock()
    mock_args.count = 600000 # > 500000 to trigger warning
    mock_parse_args.return_value = mock_args

    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_connection

    # Mock that no data exists
    mock_cursor.fetchone.return_value = {'cnt': 0}
    
    # Mock fetchall for dependencies
    mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'Test', 'price': 10.0, 'total_amount': 100.0}]
    mock_cursor.lastrowid = 1

    # Act
    main()

    # Assert
    assert mock_sleep.call_count == 10
    mock_get_db_connection.assert_called_once()

@patch('seeders.main.time.sleep')
@patch('seeders.main.get_db_connection')
@patch('seeders.main.argparse.ArgumentParser.parse_args')
def test_main_massive_insertion_abort(mock_parse_args, mock_get_db_connection, mock_sleep):
    # Arrange
    mock_args = MagicMock()
    mock_args.count = 600000 # > 500000 to trigger warning
    mock_parse_args.return_value = mock_args

    # Simulate user pressing Ctrl+C
    mock_sleep.side_effect = KeyboardInterrupt()

    # Act
    main()

    # Assert
    mock_get_db_connection.assert_not_called()

def test_main_execution():
    with patch('seeders.main.main') as mock_main:
        # Import the module to trigger the __name__ == '__main__' block
        # We need to simulate this block being executed
        import seeders.main
        # Since we can't easily test the __main__ block directly without running it as a script,
        # we just ensure the main function exists and is callable
        assert callable(seeders.main.main)