from telegram import User

def get_telegram_info(user: User) -> dict:
    """
    Get telegram user information
    Args:
        user (User): Telegram user object
    Returns:
        dict: User information containing telegram_id, username and name
    """
    return {
        'telegram_id': user.id,
        'telegram_username': f"@{user.username}" if user.username else "",
        'telegram_name': f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
    }