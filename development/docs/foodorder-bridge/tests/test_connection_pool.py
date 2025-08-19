"""
Tests for Odoo connection pool
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from app.services.connection_pool import OdooConnection, OdooConnectionPool, get_connection_pool


@pytest.fixture
def mock_xmlrpc_proxies():
    """Mock XML-RPC proxy objects"""
    common_proxy = Mock()
    models_proxy = Mock()
    
    # Mock authentication
    common_proxy.authenticate.return_value = 123  # Mock UID
    
    return common_proxy, models_proxy


@pytest.fixture
def mock_connection():
    """Create a mock Odoo connection"""
    common_proxy = Mock()
    models_proxy = Mock()
    
    connection = OdooConnection(
        common_proxy=common_proxy,
        models_proxy=models_proxy,
        uid=123,
        created_at=time.time()
    )
    
    return connection


def test_odoo_connection_creation():
    """Test OdooConnection object creation"""
    common_proxy = Mock()
    models_proxy = Mock()
    created_at = time.time()
    
    connection = OdooConnection(
        common_proxy=common_proxy,
        models_proxy=models_proxy,
        uid=123,
        created_at=created_at
    )
    
    assert connection.common_proxy == common_proxy
    assert connection.models_proxy == models_proxy
    assert connection.uid == 123
    assert connection.created_at == created_at
    assert connection.last_used == created_at
    assert connection.in_use is False
    assert isinstance(connection.connection_id, int)


def test_odoo_connection_mark_used(mock_connection):
    """Test marking connection as used"""
    original_time = mock_connection.last_used
    time.sleep(0.01)  # Small delay
    
    mock_connection.mark_used()
    
    assert mock_connection.last_used > original_time


def test_odoo_connection_expiration(mock_connection):
    """Test connection expiration logic"""
    # Fresh connection should not be expired
    assert not mock_connection.is_expired(max_age_seconds=3600)
    
    # Old connection should be expired
    mock_connection.created_at = time.time() - 7200  # 2 hours ago
    assert mock_connection.is_expired(max_age_seconds=3600)


def test_odoo_connection_idle_time(mock_connection):
    """Test connection idle time logic"""
    # Recently used connection should not be idle too long
    mock_connection.mark_used()
    assert not mock_connection.is_idle_too_long(max_idle_seconds=300)
    
    # Connection idle for too long
    mock_connection.last_used = time.time() - 600  # 10 minutes ago
    assert mock_connection.is_idle_too_long(max_idle_seconds=300)


@patch('app.services.connection_pool.xmlrpc.client.ServerProxy')
def test_connection_pool_creation(mock_server_proxy):
    """Test connection pool initialization"""
    # Mock XML-RPC proxies
    mock_common = Mock()
    mock_models = Mock()
    mock_common.authenticate.return_value = 123
    
    mock_server_proxy.side_effect = [mock_common, mock_models]
    
    pool = OdooConnectionPool(
        odoo_url="https://test.odoo.com",
        db="test_db",
        username="test_user",
        password="test_pass",
        max_connections=5
    )
    
    assert pool.odoo_url == "https://test.odoo.com"
    assert pool.db == "test_db" 
    assert pool.username == "test_user"
    assert pool.password == "test_pass"
    assert pool.max_connections == 5
    assert pool._pool.qsize() == 0
    assert len(pool._active_connections) == 0


@patch('app.services.connection_pool.xmlrpc.client.ServerProxy')
def test_connection_pool_create_connection(mock_server_proxy):
    """Test creating a new connection"""
    # Mock XML-RPC proxies
    mock_common = Mock()
    mock_models = Mock()
    mock_common.authenticate.return_value = 123
    
    mock_server_proxy.side_effect = [mock_common, mock_models]
    
    pool = OdooConnectionPool(
        odoo_url="https://test.odoo.com",
        db="test_db",
        username="test_user",
        password="test_pass"
    )
    
    connection = pool._create_connection()
    
    assert isinstance(connection, OdooConnection)
    assert connection.uid == 123
    assert connection.common_proxy == mock_common
    assert connection.models_proxy == mock_models
    assert pool._total_created == 1


@patch('app.services.connection_pool.xmlrpc.client.ServerProxy')
def test_connection_pool_get_connection(mock_server_proxy):
    """Test getting a connection from pool"""
    # Mock XML-RPC proxies
    mock_common = Mock()
    mock_models = Mock()
    mock_common.authenticate.return_value = 123
    
    mock_server_proxy.side_effect = [mock_common, mock_models]
    
    pool = OdooConnectionPool(
        odoo_url="https://test.odoo.com",
        db="test_db",
        username="test_user", 
        password="test_pass",
        max_connections=2
    )
    
    # First connection should be created
    conn1 = pool.get_connection()
    assert isinstance(conn1, OdooConnection)
    assert conn1.in_use is True
    assert len(pool._active_connections) == 1
    
    # Release and get again should reuse
    pool.release_connection(conn1)
    conn2 = pool.get_connection()
    assert conn2 is conn1  # Same connection object
    assert pool._total_reused >= 1


@patch('app.services.connection_pool.xmlrpc.client.ServerProxy')
def test_connection_pool_execute_kw(mock_server_proxy):
    """Test executing method using connection pool"""
    # Mock XML-RPC proxies
    mock_common = Mock()
    mock_models = Mock()
    mock_common.authenticate.return_value = 123
    mock_models.execute_kw.return_value = [{'id': 1, 'name': 'Test'}]
    
    mock_server_proxy.side_effect = [mock_common, mock_models]
    
    pool = OdooConnectionPool(
        odoo_url="https://test.odoo.com",
        db="test_db",
        username="test_user",
        password="test_pass"
    )
    
    result = pool.execute_kw(
        'product.product', 
        'search_read',
        [[]], 
        {'fields': ['id', 'name']}
    )
    
    assert result == [{'id': 1, 'name': 'Test'}]
    
    # Check that execute_kw was called with correct parameters
    mock_models.execute_kw.assert_called_once_with(
        "test_db",
        123,
        "test_pass",
        'product.product',
        'search_read',
        [[]],
        {'fields': ['id', 'name']}
    )


@patch('app.services.connection_pool.xmlrpc.client.ServerProxy')
def test_connection_pool_stats(mock_server_proxy):
    """Test getting connection pool statistics"""
    # Mock XML-RPC proxies
    mock_common = Mock()
    mock_models = Mock()
    mock_common.authenticate.return_value = 123
    
    mock_server_proxy.side_effect = [mock_common, mock_models]
    
    pool = OdooConnectionPool(
        odoo_url="https://test.odoo.com",
        db="test_db", 
        username="test_user",
        password="test_pass"
    )
    
    # Get initial stats
    stats = pool.get_pool_stats()
    assert stats['pool_size'] == 0
    assert stats['active_connections'] == 0
    assert stats['max_connections'] == 10  # default
    assert stats['total_created'] == 0
    assert stats['total_reused'] == 0
    
    # Create and use connection
    conn = pool.get_connection()
    stats = pool.get_pool_stats()
    assert stats['active_connections'] == 1
    assert stats['total_created'] == 1
    
    # Release connection
    pool.release_connection(conn)
    stats = pool.get_pool_stats()
    assert stats['active_connections'] == 0
    assert stats['pool_size'] == 1


def test_get_connection_pool_factory():
    """Test connection pool factory function"""
    with patch('app.services.connection_pool.OdooConnectionPool') as mock_pool_class:
        mock_pool = Mock()
        mock_pool_class.return_value = mock_pool
        
        # First call should create new pool
        pool1 = get_connection_pool(
            "https://test.odoo.com", 
            "db1", 
            "user1", 
            "pass1"
        )
        assert pool1 == mock_pool
        
        # Second call with same parameters should return cached pool
        pool2 = get_connection_pool(
            "https://test.odoo.com",
            "db1", 
            "user1",
            "pass1"
        )
        assert pool2 == mock_pool
        
        # Should only create one pool instance
        mock_pool_class.assert_called_once()