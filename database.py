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

    def check_subscription_exists(self, telegram_id: int, username: str) -> bool:
        """
        Check if a subscription already exists
        Args:
            telegram_id (int): Telegram user ID
            username (str): Extracted username from subscription link
        Returns:
            bool: True if subscription exists, False otherwise
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            cursor = self.connection.cursor()
            query = """
            SELECT COUNT(*) 
            FROM users 
            WHERE telegram_id = %s AND username = %s
            """
            cursor.execute(query, (telegram_id, username))
            result = cursor.fetchone()
            return result[0] > 0
        except Exception as e:
            logger.error(f"Error checking subscription: {str(e)}")
            return False
        finally:
            if cursor:
                cursor.close()

    def save_user(self, username: str, telegram_id: int, telegram_username: str, telegram_name: str):
        """
        Save user information to database
        Args:
            username (str): Extracted username from subscription link
            telegram_id (int): Telegram user ID
            telegram_username (str): Telegram username
            telegram_name (str): Telegram display name
        Returns:
            bool: True if saved successfully, False if already exists
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            # Check if subscription already exists
            if self.check_subscription_exists(telegram_id, username):
                logger.info(f"Subscription already exists for telegram_id: {telegram_id}, username: {username}")
                return False

            cursor = self.connection.cursor()
            query = """
            INSERT INTO users 
            (username, telegram_id, telegram_username, telegram_name, start_bot, last_message) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (
                username,
                telegram_id,
                telegram_username,
                telegram_name,
                current_time,
                current_time
            )
            
            cursor.execute(query, values)
            self.connection.commit()
            logger.info(f"User data saved successfully for telegram_id: {telegram_id}")
            return True
            
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
