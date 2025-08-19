"""
Connection pool manager for Odoo XML-RPC connections
"""
import threading
import time
import xmlrpc.client
from typing import Dict, Any, Optional, Tuple
from queue import Queue, Empty
import logging

logger = logging.getLogger(__name__)


class OdooConnection:
    """Wrapper for Odoo XML-RPC connection with metadata"""
    
    def __init__(self, common_proxy, models_proxy, uid: int, created_at: float):
        self.common_proxy = common_proxy
        self.models_proxy = models_proxy
        self.uid = uid
        self.created_at = created_at
        self.last_used = created_at
        self.in_use = False
        self.connection_id = id(self)
    
    def mark_used(self):
        """Mark connection as recently used"""
        self.last_used = time.time()
    
    def is_expired(self, max_age_seconds: int = 3600) -> bool:
        """Check if connection is expired"""
        return (time.time() - self.created_at) > max_age_seconds
    
    def is_idle_too_long(self, max_idle_seconds: int = 300) -> bool:
        """Check if connection has been idle too long"""
        return (time.time() - self.last_used) > max_idle_seconds


class OdooConnectionPool:
    """Connection pool for Odoo XML-RPC connections"""
    
    def __init__(
        self, 
        odoo_url: str, 
        db: str, 
        username: str, 
        password: str,
        max_connections: int = 10,
        max_idle_time: int = 300,
        max_connection_age: int = 3600
    ):
        self.odoo_url = odoo_url
        self.db = db
        self.username = username
        self.password = password
        self.max_connections = max_connections
        self.max_idle_time = max_idle_time
        self.max_connection_age = max_connection_age
        
        self._pool = Queue(maxsize=max_connections)
        self._active_connections = {}
        self._lock = threading.Lock()
        self._total_created = 0
        self._total_reused = 0
        
        logger.info(f"Initialized Odoo connection pool: max_connections={max_connections}")
    
    def _create_connection(self) -> OdooConnection:
        """Create a new Odoo connection"""
        try:
            # Create common and models proxies
            common_proxy = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            models_proxy = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
            
            # Authenticate
            uid = common_proxy.authenticate(self.db, self.username, self.password, {})
            
            if not uid:
                raise ValueError(f"Failed to authenticate with Odoo")
            
            connection = OdooConnection(
                common_proxy=common_proxy,
                models_proxy=models_proxy,
                uid=uid,
                created_at=time.time()
            )
            
            self._total_created += 1
            logger.debug(f"Created new Odoo connection {connection.connection_id}")
            return connection
            
        except Exception as e:
            logger.error(f"Failed to create Odoo connection: {e}")
            raise
    
    def _cleanup_expired_connections(self):
        """Remove expired connections from pool"""
        with self._lock:
            # Clean up active connections
            expired_active = []
            for conn_id, conn in self._active_connections.items():
                if conn.is_expired(self.max_connection_age) or conn.is_idle_too_long(self.max_idle_time):
                    expired_active.append(conn_id)
            
            for conn_id in expired_active:
                del self._active_connections[conn_id]
                logger.debug(f"Removed expired active connection {conn_id}")
            
            # Clean up pooled connections
            pooled_connections = []
            try:
                while True:
                    conn = self._pool.get_nowait()
                    if not (conn.is_expired(self.max_connection_age) or conn.is_idle_too_long(self.max_idle_time)):
                        pooled_connections.append(conn)
                    else:
                        logger.debug(f"Removed expired pooled connection {conn.connection_id}")
            except Empty:
                pass
            
            # Put back valid connections
            for conn in pooled_connections:
                try:
                    self._pool.put_nowait(conn)
                except:
                    pass  # Pool might be full
    
    def get_connection(self) -> OdooConnection:
        """Get a connection from the pool"""
        # Cleanup expired connections periodically
        self._cleanup_expired_connections()
        
        # Try to get from pool first
        try:
            connection = self._pool.get_nowait()
            connection.mark_used()
            connection.in_use = True
            
            with self._lock:
                self._active_connections[connection.connection_id] = connection
            
            self._total_reused += 1
            logger.debug(f"Reused connection {connection.connection_id}")
            return connection
            
        except Empty:
            # Pool is empty, create new connection
            connection = self._create_connection()
            connection.in_use = True
            
            with self._lock:
                self._active_connections[connection.connection_id] = connection
            
            return connection
    
    def release_connection(self, connection: OdooConnection):
        """Return a connection to the pool"""
        if not connection:
            return
        
        connection.in_use = False
        connection.mark_used()
        
        with self._lock:
            # Remove from active connections
            if connection.connection_id in self._active_connections:
                del self._active_connections[connection.connection_id]
        
        # Return to pool if not expired and pool has space
        if not (connection.is_expired(self.max_connection_age) or connection.is_idle_too_long(self.max_idle_time)):
            try:
                self._pool.put_nowait(connection)
                logger.debug(f"Returned connection {connection.connection_id} to pool")
            except:
                # Pool is full, discard connection
                logger.debug(f"Pool full, discarding connection {connection.connection_id}")
        else:
            logger.debug(f"Connection {connection.connection_id} expired, not returning to pool")
    
    def execute_kw(self, model: str, method: str, args: list, kwargs: dict = None) -> Any:
        """Execute a method using a pooled connection"""
        connection = None
        try:
            connection = self.get_connection()
            
            result = connection.models_proxy.execute_kw(
                self.db, 
                connection.uid, 
                self.password,
                model, 
                method, 
                args, 
                kwargs or {}
            )
            
            return result
            
        finally:
            if connection:
                self.release_connection(connection)
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self._lock:
            return {
                "pool_size": self._pool.qsize(),
                "active_connections": len(self._active_connections),
                "max_connections": self.max_connections,
                "total_created": self._total_created,
                "total_reused": self._total_reused,
                "reuse_ratio": self._total_reused / max(1, self._total_created + self._total_reused)
            }
    
    def close_all(self):
        """Close all connections in the pool"""
        with self._lock:
            # Clear active connections
            self._active_connections.clear()
            
            # Clear pooled connections
            try:
                while True:
                    self._pool.get_nowait()
            except Empty:
                pass
        
        logger.info("Closed all connections in pool")


# Global connection pool instance
_connection_pools: Dict[Tuple[str, str, str], OdooConnectionPool] = {}
_pool_lock = threading.Lock()


def get_connection_pool(
    odoo_url: str, 
    db: str, 
    username: str, 
    password: str,
    max_connections: int = 10
) -> OdooConnectionPool:
    """Get or create a connection pool for the given Odoo instance"""
    pool_key = (odoo_url, db, username)
    
    with _pool_lock:
        if pool_key not in _connection_pools:
            _connection_pools[pool_key] = OdooConnectionPool(
                odoo_url=odoo_url,
                db=db,
                username=username,
                password=password,
                max_connections=max_connections
            )
        
        return _connection_pools[pool_key]


def close_all_pools():
    """Close all connection pools"""
    with _pool_lock:
        for pool in _connection_pools.values():
            pool.close_all()
        _connection_pools.clear()