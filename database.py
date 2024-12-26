# database.py

import mysql.connector
from datetime import datetime
import logging
from config import DB_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        """Initialize database connection"""
        self.connection = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise

    def save_user(self, username: str, telegram_id: int, telegram_username: str, telegram_name: str):
        """
        Save user information to database
        Args:
            username (str): Extracted username from subscription link
            telegram_id (int): Telegram user ID
            telegram_username (str): Telegram username
            telegram_name (str): Telegram display name
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            cursor = self.connection.cursor()
            
            query = """
            INSERT INTO users 
            (username, telegram_id, telegram_username, telegram_name, start_bot, last_message) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            telegram_username = %s,
            telegram_name = %s,
            last_message = %s
            """
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            values = (
                username,
                telegram_id,
                telegram_username,
                telegram_name,
                current_time,
                current_time,
                telegram_username,
                telegram_name,
                current_time
            )
            
            cursor.execute(query, values)
            self.connection.commit()
            logger.info(f"User data saved successfully for telegram_id: {telegram_id}")
            
        except Exception as e:
            logger.error(f"Failed to save user data: {str(e)}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")