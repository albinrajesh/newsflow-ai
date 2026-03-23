import sqlite3
import datetime

DB_PATH = "mcp/memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS research_memory
                 (id INTEGER PRIMARY KEY, query TEXT, summary TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def save_memory(query: str, summary: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO research_memory (query, summary, timestamp) VALUES (?, ?, ?)",
              (query, summary, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def search_memory(query: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Simple keyword search for portfolio version
    c.execute("SELECT summary FROM research_memory WHERE query LIKE ? ORDER BY timestamp DESC LIMIT 1", 
              (f'%{query}%',))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Initialize on import
init_db()