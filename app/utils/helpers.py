import uuid
import hashlib
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


def generate_campaign_id() -> str:
    """Generate a unique campaign ID."""
    return f"camp_{uuid.uuid4().hex[:12]}"


def generate_hash(data: str) -> str:
    """Generate MD5 hash of string data."""
    return hashlib.md5(data.encode()).hexdigest()


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text."""
    hashtag_pattern = r'#\w+'
    hashtags = re.findall(hashtag_pattern, text)
    return list(set(hashtags))  # Remove duplicates


def count_characters(text: str, include_spaces: bool = True) -> int:
    """Count characters in text."""
    if include_spaces:
        return len(text)
    return len(text.replace(' ', ''))


def validate_platform(platform: str) -> bool:
    """Validate if platform is supported."""
    supported_platforms = ['instagram', 'twitter', 'linkedin', 'facebook', 'tiktok']
    return platform.lower() in supported_platforms


def clean_text(text: str) -> str:
    """Clean and normalize text input."""
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s#@.,!?-]', '', text)
    
    return text.strip()


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def get_platform_character_limits() -> Dict[str, int]:
    """Get character limits for different platforms."""
    return {
        'twitter': 280,
        'instagram': 2200,
        'linkedin': 3000,
        'facebook': 63206,
        'tiktok': 150
    }


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def parse_datetime(dt_string: str) -> datetime:
    """Parse ISO datetime string."""
    return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename.strip()


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary."""
    try:
        return dictionary.get(key, default)
    except (KeyError, AttributeError):
        return default


def calculate_progress_percentage(current_step: int, total_steps: int) -> int:
    """Calculate progress percentage."""
    if total_steps == 0:
        return 0
    
    percentage = (current_step / total_steps) * 100
    return min(100, max(0, int(percentage)))