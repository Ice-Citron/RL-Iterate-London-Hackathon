"""
MySQL Database Connector for Dynamic Ground Truth

This module provides direct access to the DVWA MySQL database
to query ground truth data in real-time instead of using static JSON.
"""

import os
from typing import Any, Dict, List, Optional
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env at import time so get_db_connector
# sees them before calling os.getenv.
load_dotenv()

try:
    import aiomysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("⚠ aiomysql not installed. Install with: pip install aiomysql")


class DVWADatabaseConnector:
    """Connects to DVWA MySQL database to query ground truth data"""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 3306,
        user: str = "dvwa",
        password: str = "dvwa_password",
        database: str = "dvwa"
    ):
        """
        Initialize database connector.

        Args:
            host: MySQL host (default: 127.0.0.1)
            port: MySQL port (default: 3306)
            user: MySQL username (default: dvwa)
            password: MySQL password (default: dvwa_password)
            database: Database name (default: dvwa)
        """
        if not MYSQL_AVAILABLE:
            raise ImportError("aiomysql not available. Install with: pip install aiomysql")
        self.config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "db": database,
            "charset": "utf8mb4",
            "autocommit": True
        }
        self.pool: Optional[aiomysql.Pool] = None

    async def connect(self):
        """Create connection pool"""
        if self.pool is None:
            self.pool = await aiomysql.create_pool(**self.config, minsize=1, maxsize=5)
            print(f"✓ Connected to DVWA MySQL database at {self.config['host']}:{self.config['port']}")

    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
            print("✓ Disconnected from DVWA MySQL database")

    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool"""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            yield conn

    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as list of dicts.

        Args:
            query: SQL query string
            params: Query parameters (for prepared statements)

        Returns:
            List of dictionaries, one per row
        """
        async with self.get_connection() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                result = await cursor.fetchall()
                return result

    # ========================================================================
    # Ground Truth Query Methods
    # ========================================================================

    async def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all users from DVWA users table.

        Returns:
            List of user dictionaries with keys: user_id, first_name, last_name, user, password
        """
        query = """
        SELECT
            user_id,
            first_name,
            last_name,
            user,
            password,
            avatar
        FROM users
        ORDER BY user_id
        """
        return await self.execute_query(query)

    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific user by ID"""
        query = "SELECT * FROM users WHERE user_id = %s"
        results = await self.execute_query(query, (user_id,))
        return results[0] if results else None

    async def get_user_count(self) -> int:
        """Get total number of users"""
        query = "SELECT COUNT(*) as count FROM users"
        result = await self.execute_query(query)
        return result[0]['count'] if result else 0

    async def get_guestbook_entries(self) -> List[Dict[str, Any]]:
        """
        Get all guestbook entries (for XSS testing).

        Returns:
            List of guestbook entries
        """
        query = """
        SELECT
            comment_id,
            name,
            comment
        FROM guestbook
        ORDER BY comment_id DESC
        """
        return await self.execute_query(query)

    async def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        query = """
        SELECT COUNT(*) as count
        FROM information_schema.tables
        WHERE table_schema = %s AND table_name = %s
        """
        result = await self.execute_query(query, (self.config['db'], table_name))
        return result[0]['count'] > 0 if result else False

    async def get_database_version(self) -> str:
        """Get MySQL database version"""
        query = "SELECT VERSION() as version"
        result = await self.execute_query(query)
        return result[0]['version'] if result else "unknown"

    async def get_table_count(self) -> int:
        """Get total number of tables in database"""
        query = """
        SELECT COUNT(*) as count
        FROM information_schema.tables
        WHERE table_schema = %s
        """
        result = await self.execute_query(query, (self.config['db'],))
        return result[0]['count'] if result else 0

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on database connection.

        Returns:
            Dictionary with health status
        """
        try:
            version = await self.get_database_version()
            user_count = await self.get_user_count()
            table_count = await self.get_table_count()

            return {
                "healthy": True,
                "version": version,
                "user_count": user_count,
                "table_count": table_count,
                "database": self.config['db']
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }


# Singleton instance
_db_connector: Optional[DVWADatabaseConnector] = None


def get_db_connector(
    host: Optional[str] = None,
    port: Optional[int] = None,
    user: Optional[str] = None,
    password: Optional[str] = None
) -> DVWADatabaseConnector:
    """
    Get or create the database connector singleton.

    Environment variables can override defaults:
    - DVWA_MYSQL_HOST
    - DVWA_MYSQL_PORT
    - DVWA_MYSQL_USER
    - DVWA_MYSQL_PASSWORD
    """
    global _db_connector

    if _db_connector is None:
        # Use environment variables with fallbacks
        _host = host or os.getenv("DVWA_DB_HOST", "127.0.0.1")
        _port = int(port or os.getenv("DVWA_DB_PORT", "3306"))
        _user = user or os.getenv("DVWA_DB_USER", "dvwa")
        _password = password or os.getenv("DVWA_DB_PASSWORD", "dvwa_password")
        print("PORT: ", _port)

        _db_connector = DVWADatabaseConnector(
            host=_host,
            port=_port,
            user=_user,
            password=_password
        )

    return _db_connector


async def test_connection():
    """Test database connection (for debugging)"""
    db = get_db_connector()

    try:
        await db.connect()

        print("\n=== Database Health Check ===")
        health = await db.health_check()
        for key, value in health.items():
            print(f"{key}: {value}")

        print("\n=== Users Table ===")
        users = await db.get_all_users()
        for user in users:
            print(f"ID: {user['user_id']}, Name: {user['first_name']} {user['last_name']}, User: {user['user']}")

        await db.disconnect()

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nMake sure:")
        print("  1. Docker container is running: docker-compose up -d")
        print("  2. MySQL port 3306 is exposed")
        print("  3. Credentials match docker-compose.yml")


if __name__ == "__main__":
    # Test the connection
    asyncio.run(test_connection())
