import aiosqlite
import os

DB_PATH = "probound.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # 1. Enable WAL Mode for high-concurrency performance
        await db.execute("PRAGMA journal_mode=WAL;")
        
        # 2. Create the Users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                api_key TEXT
            )
        """)
        
        dummy_users = [
            (i, f"new_user_{i}", f"updated_key_{i}") 
            for i in range(1, 101)
        ]
        
        await db.executemany("INSERT OR IGNORE INTO users VALUES (?, ?, ?)", dummy_users)
        await db.commit()
        

        cursor = await db.execute("SELECT COUNT(*) FROM users")
        count = (await cursor.fetchone())[0]
        print(f"Database initialized. Total users: {count}")