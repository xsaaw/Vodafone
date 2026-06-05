# database.py
"""
قاعدة بيانات محلية للمستخدمين والعمليات
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "vodafone_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """تهيئة قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                vodafone_number TEXT,
                full_name TEXT,
                balance REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # جدول العمليات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                operation_type TEXT,
                amount REAL,
                from_number TEXT,
                to_number TEXT,
                status TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        ''')
        
        # جدول الجلسات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                telegram_id INTEGER,
                vodafone_token TEXT,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_user(self, telegram_id: int, vodafone_number: str, full_name: str):
        """حفظ مستخدم جديد"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (telegram_id, vodafone_number, full_name, last_login)
            VALUES (?, ?, ?, ?)
        ''', (telegram_id, vodafone_number, full_name, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def log_transaction(self, telegram_id: int, operation_type: str, 
                       amount: float, from_number: str, to_number: str, 
                       status: str = "pending", details: str = ""):
        """تسجيل عملية جديدة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions 
            (telegram_id, operation_type, amount, from_number, to_number, status, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (telegram_id, operation_type, amount, from_number, to_number, status, details))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return transaction_id
    
    def get_user_stats(self, telegram_id: int) -> Dict:
        """الحصول على إحصائيات المستخدم"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as total_transactions,
                   SUM(amount) as total_amount,
                   operation_type,
                   COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed
            FROM transactions 
            WHERE telegram_id = ?
            GROUP BY operation_type
        ''', (telegram_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        stats = {
            "total_transactions": 0,
            "total_amount": 0,
            "by_type": {}
        }
        
        for row in results:
            stats["total_transactions"] += row[0]
            stats["total_amount"] += row[1] if row[1] else 0
            stats["by_type"][row[2]] = {
                "count": row[0],
                "completed": row[3]
            }
        
        return stats

# نسخة وحيدة من مدير قاعدة البيانات
db_manager = DatabaseManager()