"""
工具函数模块，提供各模块共享的实用功能
"""

import os
import hashlib
import datetime

def format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes} 字节"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def calculate_file_hash(file_path):
    """计算文件的MD5哈希值以比较文件内容"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"计算文件哈希值时出错: {e}")
        return None

def check_dependencies():
    """检查可选依赖并返回可用状态"""
    results = {}
    
    # 检查 watchdog
    try:
        from watchdog.observers import Observer
        results['WATCHDOG_AVAILABLE'] = True
    except ImportError:
        print("提示: 要使用文件监视功能，请安装watchdog库: pip install watchdog")
        results['WATCHDOG_AVAILABLE'] = False
    
    # 检查 pathspec
    try:
        import pathspec
        results['PATHSPEC_AVAILABLE'] = True
    except ImportError:
        print("提示: 为获得更好的忽略规则支持，请安装pathspec库: pip install pathspec")
        results['PATHSPEC_AVAILABLE'] = False
    
    return results

# 运行时检查依赖
DEPENDENCIES = check_dependencies()
WATCHDOG_AVAILABLE = DEPENDENCIES['WATCHDOG_AVAILABLE']
PATHSPEC_AVAILABLE = DEPENDENCIES['PATHSPEC_AVAILABLE'] 