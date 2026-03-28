"""
Database module - MySQL operations for fake news detection
"""

from .db import (
    connect_db,
    initialize_db,
    save_result,
    fetch_results,
    fetch_recent_results,
    is_database_connected
)

__all__ = [
    'connect_db',
    'initialize_db',
    'save_result',
    'fetch_results',
    'fetch_recent_results',
    'is_database_connected'
]
