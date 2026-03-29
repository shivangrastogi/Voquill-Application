import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    """Handles local storage for history and dictionary."""
    
    def __init__(self, db_path="voquill.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes tables if they don't exist and handles migrations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # History table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                raw_text TEXT,
                clean_text TEXT,
                mode TEXT,
                app_context TEXT
            )
        """)
        
        # Migration: Check if app_context exists, if not add it
        cursor.execute("PRAGMA table_info(history)")
        columns = [column[1] for column in cursor.fetchall()]
        if "app_context" not in columns:
            print("Migrating history table: adding app_context column...")
            cursor.execute("ALTER TABLE history ADD COLUMN app_context TEXT DEFAULT 'Unknown'")
        
        # Dictionary table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dictionary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE,
                replacement TEXT
            )
        """)
        
        # Migration: Add replacement column to dictionary if missing
        cursor.execute("PRAGMA table_info(dictionary)")
        columns = [column[1] for column in cursor.fetchall()]
        if "replacement" not in columns:
            cursor.execute("ALTER TABLE dictionary ADD COLUMN replacement TEXT")

        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                password_hash TEXT,
                name TEXT,
                created_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()

    def add_history(self, raw, clean, mode, app_context="Unknown"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO history (timestamp, raw_text, clean_text, mode, app_context) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().isoformat(), raw, clean, mode, app_context)
        )
        conn.commit()
        conn.close()

    def get_history(self, limit=50):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,))
        data = cursor.fetchall()
        conn.close()
        return data

    def add_word(self, word, replacement=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # We use word as the key for replacements
            cursor.execute("INSERT OR REPLACE INTO dictionary (word, replacement) VALUES (?, ?)", (word, replacement))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()

    def get_dictionary_map(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT word, replacement FROM dictionary")
        # If replacement is NULL, we'll use the word itself as fallback (but Engine handles empty)
        mapping = {row[0]: row[1] for row in cursor.fetchall() if row[1]}
        conn.close()
        return mapping

    def get_dictionary(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT word FROM dictionary")
        words = [row[0] for row in cursor.fetchall()]
        conn.close()
        return words

    def set_setting(self, key, value):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()

    def get_setting(self, key):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def get_usage_stats(self):
        """Calculates actual usage streaks and word counts."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 1. Total Words
            cursor.execute("SELECT clean_text FROM history")
            all_text = cursor.fetchall()
            total_words = sum(len(row[0].split()) for row in all_text if row[0])
            
            # 2. Words this month
            now = datetime.now()
            month_start = datetime(now.year, now.month, 1).isoformat()
            cursor.execute("SELECT clean_text FROM history WHERE timestamp >= ?", (month_start,))
            month_text = cursor.fetchall()
            month_words = sum(len(row[0].split()) for row in month_text if row[0])
            
            # 3. Day Streak
            cursor.execute("SELECT DISTINCT date(timestamp) FROM history ORDER BY date(timestamp) DESC")
            dates = [row[0] for row in cursor.fetchall()]
            
            streak = 0
            if dates:
                today = datetime.now().date()
                # Real streak logic
                first_date = datetime.strptime(dates[0], "%Y-%m-%d").date()
                
                from datetime import timedelta
                if first_date == today or first_date == (today - timedelta(days=1)):
                    streak = 0
                    check_date = first_date
                    for d_str in dates:
                        d = datetime.strptime(d_str, "%Y-%m-%d").date()
                        if d == check_date:
                            streak += 1
                            check_date -= timedelta(days=1)
                        else:
                            break
            
            conn.close()
            # If no history but app is open, we count today as 1
            return {
                "total_words": total_words,
                "month_words": month_words,
                "streak": max(streak, 1)
            }
        except Exception as e:
            print(f"Error calculating stats: {e}")
            return {"total_words": 0, "month_words": 0, "streak": 1}
