"""
核心功能模块，提供基本的文件操作和同步功能
"""

from .file_manager import FileManager
from .sync import sync_directories, AutoSync

__all__ = ['FileManager', 'sync_directories', 'AutoSync'] 