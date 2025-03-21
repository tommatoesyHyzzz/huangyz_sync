"""
核心文件操作模块，提供基本的文件和目录处理功能
"""

import os
import shutil
from pathlib import Path
import datetime

from ..utils.common import format_size, calculate_file_hash
from ..utils.ignore import IgnoreRules

class FileManager:
    """文件管理器类，提供常见的文件和文件夹操作"""
    
    @staticmethod
    def create_directory(directory_path):
        """创建新文件夹"""
        try:
            os.makedirs(directory_path, exist_ok=True)
            print(f"文件夹创建成功: {directory_path}")
            return True
        except Exception as e:
            print(f"创建文件夹时出错: {e}")
            return False
    
    @staticmethod
    def create_file(file_path, content=""):
        """创建新文件，可选添加内容"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"文件创建成功: {file_path}")
            return True
        except Exception as e:
            print(f"创建文件时出错: {e}")
            return False
    
    @staticmethod
    def copy_file(source_path, destination_path):
        """复制文件"""
        try:
            shutil.copy2(source_path, destination_path)
            print(f"文件复制成功: {source_path} -> {destination_path}")
            return True
        except Exception as e:
            print(f"复制文件时出错: {e}")
            return False
    
    @staticmethod
    def copy_directory(source_dir, destination_dir):
        """复制整个文件夹"""
        try:
            shutil.copytree(source_dir, destination_dir)
            print(f"文件夹复制成功: {source_dir} -> {destination_dir}")
            return True
        except Exception as e:
            print(f"复制文件夹时出错: {e}")
            return False
    
    @staticmethod
    def move_file_or_directory(source_path, destination_path):
        """移动文件或文件夹"""
        try:
            shutil.move(source_path, destination_path)
            print(f"移动成功: {source_path} -> {destination_path}")
            return True
        except Exception as e:
            print(f"移动时出错: {e}")
            return False
    
    @staticmethod
    def rename_file_or_directory(source_path, new_name):
        """重命名文件或文件夹"""
        try:
            path = Path(source_path)
            new_path = path.parent / new_name
            os.rename(source_path, new_path)
            print(f"重命名成功: {source_path} -> {new_path}")
            return True
        except Exception as e:
            print(f"重命名时出错: {e}")
            return False
    
    @staticmethod
    def delete_file(file_path):
        """删除文件"""
        try:
            os.remove(file_path)
            print(f"文件删除成功: {file_path}")
            return True
        except Exception as e:
            print(f"删除文件时出错: {e}")
            return False
    
    @staticmethod
    def delete_directory(directory_path, force=False):
        """删除文件夹，force=True时删除非空文件夹"""
        try:
            if force:
                shutil.rmtree(directory_path)
            else:
                os.rmdir(directory_path)
            print(f"文件夹删除成功: {directory_path}")
            return True
        except Exception as e:
            print(f"删除文件夹时出错: {e}")
            return False
    
    @staticmethod
    def list_directory_contents(directory_path):
        """列出文件夹内容"""
        try:
            contents = os.listdir(directory_path)
            print(f"文件夹 {directory_path} 的内容:")
            for item in contents:
                full_path = os.path.join(directory_path, item)
                if os.path.isdir(full_path):
                    print(f"  📁 {item} (文件夹)")
                else:
                    size = os.path.getsize(full_path)
                    print(f"  📄 {item} (文件, {format_size(size)})")
            return contents
        except Exception as e:
            print(f"列出文件夹内容时出错: {e}")
            return []
    
    @staticmethod
    def get_file_info(file_path):
        """获取文件信息"""
        try:
            file_stat = os.stat(file_path)
            file_info = {
                "文件名": os.path.basename(file_path),
                "路径": os.path.abspath(file_path),
                "大小": format_size(file_stat.st_size),
                "创建时间": datetime.datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                "修改时间": datetime.datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                "访问时间": datetime.datetime.fromtimestamp(file_stat.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
            }
            print("文件信息:")
            for key, value in file_info.items():
                print(f"  {key}: {value}")
            return file_info
        except Exception as e:
            print(f"获取文件信息时出错: {e}")
            return None
    
    @staticmethod
    def search_files(directory_path, keyword, search_subdirs=True):
        """搜索文件"""
        results = []
        try:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if keyword.lower() in file.lower():
                        results.append(os.path.join(root, file))
                if not search_subdirs:
                    break  # 如果不搜索子目录，则只处理顶层目录
            
            print(f"找到 {len(results)} 个匹配 '{keyword}' 的文件:")
            for item in results:
                print(f"  {item}")
            return results
        except Exception as e:
            print(f"搜索文件时出错: {e}")
            return [] 