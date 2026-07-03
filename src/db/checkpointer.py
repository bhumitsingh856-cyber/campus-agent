# db.py
from langgraph.store.postgres.aio import AsyncPostgresStore

from psycopg_pool import AsyncConnectionPool

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import os

DB_URI = os.getenv("PGSQL_URL")


pool = AsyncConnectionPool(
    conninfo=DB_URI,
    min_size=1,
    max_size=10,
    open=False,
    max_idle=300,  
    max_lifetime=3600, 
    num_workers=3,
    kwargs={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
        "connect_timeout": 10,
    },
    check=AsyncConnectionPool.check_connection,
)
# These will be set during app startup
store = None
checkpointer = None


async def init_db():
    """Call during app startup"""
    global store, checkpointer
    
    await pool.open()
    checkpointer = AsyncPostgresSaver(pool)
    store = AsyncPostgresStore(pool)
    await checkpointer.setup()
    await store.setup()
async def close_db():
    """Call during app shutdown"""
    await pool.close()

