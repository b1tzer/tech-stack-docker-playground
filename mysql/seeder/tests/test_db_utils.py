import pytest
from unittest.mock import patch, MagicMock
import pymysql
import os
import sys

# Add parent directory to path to import db_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_db_connection

@patch('db_utils.pymysql.connect')
def test_get_db_connection_success(mock_connect):
    # Arrange
    mock_connection = MagicMock()
    mock_connect.return_value = mock_connection

    # Act
    conn = get_db_connection(max_retries=3, delay=0)

    # Assert
    assert conn == mock_connection
    mock_connect.assert_called_once()

@patch('db_utils.time.sleep')
@patch('db_utils.pymysql.connect')
def test_get_db_connection_retry_success(mock_connect, mock_sleep):
    # Arrange
    mock_connection = MagicMock()
    # Fail twice, succeed on third try
    mock_connect.side_effect = [
        pymysql.err.OperationalError("Connection refused"),
        pymysql.err.OperationalError("Connection refused"),
        mock_connection
    ]

    # Act
    conn = get_db_connection(max_retries=3, delay=0)

    # Assert
    assert conn == mock_connection
    assert mock_connect.call_count == 3
    assert mock_sleep.call_count == 2

@patch('db_utils.time.sleep')
@patch('db_utils.pymysql.connect')
def test_get_db_connection_failure(mock_connect, mock_sleep):
    # Arrange
    # Always fail
    mock_connect.side_effect = pymysql.err.OperationalError("Connection refused")

    # Act & Assert
    with pytest.raises(Exception) as excinfo:
        get_db_connection(max_retries=3, delay=0)
    
    assert "Failed to connect to the database after multiple retries" in str(excinfo.value)
    assert mock_connect.call_count == 3
    assert mock_sleep.call_count == 3