# link_decoder.py

import base64
import jwt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_username(link: str) -> str:
    """
    Extract username from encoded subscription link
    Args:
        link (str): The subscription link
    Returns:
        str: Extracted username or None if extraction fails
    """
    try:
        encoded = link.split('/')[-1].strip()
        
        # Try JWT decoding first
        try:
            decoded = jwt.decode(encoded, options={"verify_signature": False})
            username = str(decoded.get('sub', '')).strip()
            if username:
                logger.info(f"Username extracted using JWT: {username}")
                return username
        except Exception as e:
            logger.debug(f"JWT decoding failed: {str(e)}")

        # Try Base64 decoding if JWT fails
        try:
            cleaned = ''.join(c for c in encoded if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
            cleaned = cleaned[:-(len(cleaned) % 4)] if len(cleaned) % 4 else cleaned
            while len(cleaned) % 4:
                cleaned += '='
                
            decoded = base64.b64decode(cleaned)
            for encoding in ['utf-8', 'ascii', 'iso-8859-1']:
                try:
                    decoded_str = decoded.decode(encoding)
                    if ',' in decoded_str:
                        username = decoded_str.split(',')[0].strip()
                        if username:
                            logger.info(f"Username extracted using Base64: {username}")
                            return username
                except Exception as e:
                    logger.debug(f"Base64 decoding failed with {encoding}: {str(e)}")
                    continue
        except Exception as e:
            logger.debug(f"Base64 decoding failed: {str(e)}")
        
        return None
    except Exception as e:
        logger.error(f"Username extraction failed: {str(e)}")
        return None