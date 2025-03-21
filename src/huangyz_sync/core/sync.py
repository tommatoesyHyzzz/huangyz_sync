"""
文件同步模块，提供同步目录功能和自动同步
"""

import os
import time
import json

from .file_manager import FileManager
from ..utils.ignore import IgnoreRules
from ..utils.common import calculate_file_hash, WATCHDOG_AVAILABLE
from ..utils.watch import FolderWatcher

def sync_directories(source_dir, target_dir, delete_extra=False, compare_content=True, ignore_rules=None):
    """
    同步两个目录的内容
    
    参数:
        source_dir: 源目录路径
        target_dir: 目标目录路径
        delete_extra: 是否删除目标目录中多余的文件
        compare_content: 是否通过内容比较决定是否需要复制（而不仅仅依赖修改时间）
        ignore_rules: IgnoreRules对象或忽略规则文件路径
    """
    try:
        # 确保目标目录存在
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"已创建目标目录: {target_dir}")
        
        # 处理忽略规则
        if ignore_rules:
            if isinstance(ignore_rules, str) and os.path.exists(ignore_rules):
                ignore_rules = IgnoreRules(ignore_file=ignore_rules)
            elif not isinstance(ignore_rules, IgnoreRules):
                ignore_rules = IgnoreRules(patterns=ignore_rules if isinstance(ignore_rules, list) else [])
        else:
            ignore_rules = None
        
        # 记录操作日志
        operations = {
            "copied": [],
            "updated": [],
            "deleted": [],
            "skipped": [],
            "ignored": []
        }
        
        # 遍历源目录中的所有文件和文件夹
        for root, dirs, files in os.walk(source_dir):
            # 计算相对路径，用于在目标目录中创建对应结构
            rel_path = os.path.relpath(root, source_dir)
            target_root = os.path.join(target_dir, rel_path) if rel_path != '.' else target_dir
            
            # 如果当前目录应该被忽略，跳过
            if ignore_rules and rel_path != '.' and ignore_rules.should_ignore(rel_path, True):
                operations["ignored"].append(root)
                # 从dirs中移除所有子目录，避免继续遍历
                dirs[:] = []
                continue
            
            # 过滤掉被忽略的目录
            if ignore_rules:
                i = 0
                while i < len(dirs):
                    dir_path = os.path.join(rel_path, dirs[i]) if rel_path != '.' else dirs[i]
                    if ignore_rules.should_ignore(dir_path, True):
                        operations["ignored"].append(os.path.join(root, dirs[i]))
                        dirs.pop(i)
                    else:
                        i += 1
            
            # 确保目标目录中的子目录存在
            for dir_name in dirs:
                dir_rel_path = os.path.join(rel_path, dir_name) if rel_path != '.' else dir_name
                
                # 再次检查目录是否应该被忽略
                if ignore_rules and ignore_rules.should_ignore(dir_rel_path, True):
                    continue
                
                target_dir_path = os.path.join(target_dir, dir_rel_path)
                if not os.path.exists(target_dir_path):
                    os.makedirs(target_dir_path)
                    print(f"已创建目标子目录: {target_dir_path}")
            
            # 处理文件
            for file_name in files:
                # 检查文件是否应该被忽略
                file_rel_path = os.path.join(rel_path, file_name) if rel_path != '.' else file_name
                if ignore_rules and ignore_rules.should_ignore(file_rel_path, False):
                    operations["ignored"].append(os.path.join(root, file_name))
                    continue
                
                source_file = os.path.join(root, file_name)
                target_file = os.path.join(target_root, file_name)
                
                # 如果目标文件不存在，直接复制
                if not os.path.exists(target_file):
                    FileManager.copy_file(source_file, target_file)
                    operations["copied"].append(target_file)
                    continue
                
                # 检查文件是否需要更新
                need_update = False
                if compare_content:
                    # 通过哈希值比较文件内容
                    source_hash = calculate_file_hash(source_file)
                    target_hash = calculate_file_hash(target_file)
                    need_update = source_hash != target_hash
                else:
                    # 通过修改时间比较
                    source_mtime = os.path.getmtime(source_file)
                    target_mtime = os.path.getmtime(target_file)
                    need_update = source_mtime > target_mtime
                
                if need_update:
                    FileManager.copy_file(source_file, target_file)
                    operations["updated"].append(target_file)
                else:
                    operations["skipped"].append(target_file)
        
        # 如果需要，删除目标目录中多余的文件
        if delete_extra:
            for root, dirs, files in os.walk(target_dir):
                # 计算相对路径，用于在源目录中查找对应文件
                rel_path = os.path.relpath(root, target_dir)
                source_root = os.path.join(source_dir, rel_path) if rel_path != '.' else source_dir
                
                # 如果当前目录应该被忽略，跳过
                if ignore_rules and rel_path != '.' and ignore_rules.should_ignore(rel_path, True):
                    continue
                
                # 处理文件
                i = 0
                while i < len(files):
                    file_name = files[i]
                    file_rel_path = os.path.join(rel_path, file_name) if rel_path != '.' else file_name
                    
                    # 如果文件应该被忽略，跳过
                    if ignore_rules and ignore_rules.should_ignore(file_rel_path, False):
                        i += 1
                        continue
                    
                    target_file = os.path.join(root, file_name)
                    source_file = os.path.join(source_root, file_name)
                    
                    # 如果源文件不存在，删除目标文件
                    if not os.path.exists(source_file):
                        FileManager.delete_file(target_file)
                        operations["deleted"].append(target_file)
                    
                    i += 1
                
                # 处理多余的目录（从后向前遍历，确保先处理子目录）
                i = len(dirs) - 1
                while i >= 0:
                    dir_name = dirs[i]
                    dir_rel_path = os.path.join(rel_path, dir_name) if rel_path != '.' else dir_name
                    
                    # 如果目录应该被忽略，跳过
                    if ignore_rules and ignore_rules.should_ignore(dir_rel_path, True):
                        i -= 1
                        continue
                    
                    target_dir_path = os.path.join(root, dir_name)
                    source_dir_path = os.path.join(source_root, dir_name)
                    
                    if not os.path.exists(source_dir_path):
                        try:
                            FileManager.delete_directory(target_dir_path, force=True)
                            operations["deleted"].append(target_dir_path)
                            # 防止os.walk继续处理已删除的目录
                            dirs.pop(i)
                        except Exception as e:
                            print(f"删除目录时出错: {e}")
                    
                    i -= 1
        
        # 打印同步结果
        print(f"同步完成! 源目录: {source_dir} -> 目标目录: {target_dir}")
        print(f"忽略了 {len(operations['ignored'])} 个文件/文件夹")
        print(f"复制了 {len(operations['copied'])} 个新文件")
        print(f"更新了 {len(operations['updated'])} 个文件")
        print(f"删除了 {len(operations['deleted'])} 个多余文件")
        print(f"跳过了 {len(operations['skipped'])} 个相同文件")
        
        return operations
    except Exception as e:
        print(f"同步目录时出错: {e}")
        return None

def save_operations_log(operations, log_file):
    """保存操作日志到文件"""
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(operations, f, ensure_ascii=False, indent=2)
        print(f"操作日志已保存到: {log_file}")
        return True
    except Exception as e:
        print(f"保存操作日志时出错: {e}")
        return False

def load_operations_log(log_file):
    """从文件加载操作日志"""
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            operations = json.load(f)
        print(f"从 {log_file} 加载了操作日志")
        return operations
    except Exception as e:
        print(f"加载操作日志时出错: {e}")
        return None

class AutoSync:
    """持续自动同步两个目录"""
    
    def __init__(self, source_dir, target_dir, interval=60, 
                 use_watchdog=True, delete_extra=False, ignore_rules=None):
        """
        初始化自动同步器
        
        参数:
            source_dir: 源目录
            target_dir: 目标目录
            interval: 使用轮询方式时的同步间隔(秒)
            use_watchdog: 是否使用watchdog监视文件变化(推荐)
            delete_extra: 是否删除目标目录中多余的文件
            ignore_rules: IgnoreRules对象、忽略规则文件路径或规则列表
        """
        self.source_dir = os.path.abspath(source_dir)
        self.target_dir = os.path.abspath(target_dir)
        self.interval = interval
        self.use_watchdog = use_watchdog and WATCHDOG_AVAILABLE
        self.delete_extra = delete_extra
        self.running = False
        self.watcher = None
        self._stop_flag = False
        
        # 处理忽略规则
        if ignore_rules:
            if isinstance(ignore_rules, str) and os.path.exists(ignore_rules):
                self.ignore_rules = IgnoreRules(ignore_file=ignore_rules)
            elif isinstance(ignore_rules, IgnoreRules):
                self.ignore_rules = ignore_rules
            else:
                self.ignore_rules = IgnoreRules(patterns=ignore_rules if isinstance(ignore_rules, list) else [])
        else:
            self.ignore_rules = None
        
        # 确保目录存在
        if not os.path.exists(self.source_dir):
            raise FileNotFoundError(f"源目录不存在: {self.source_dir}")
            
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)
    
    def start(self):
        """开始自动同步"""
        if self.running:
            print("自动同步已经在运行中")
            return False
            
        try:
            # 执行初始同步
            print(f"执行初始同步: {self.source_dir} -> {self.target_dir}")
            sync_directories(
                self.source_dir, self.target_dir, 
                delete_extra=self.delete_extra,
                ignore_rules=self.ignore_rules
            )
            
            self.running = True
            self._stop_flag = False
            
            if self.use_watchdog:
                # 使用watchdog监视文件变化
                self.watcher = FolderWatcher(
                    self.source_dir,
                    self.target_dir,
                    sync_on_change=True,
                    auto_start=True,
                    ignore_rules=self.ignore_rules
                )
            else:
                # 使用轮询方式定期同步
                import threading
                self._thread = threading.Thread(target=self._polling_sync)
                self._thread.daemon = True
                self._thread.start()
                print(f"开始轮询同步，间隔 {self.interval} 秒")
            
            return True
        
        except Exception as e:
            print(f"开始自动同步时出错: {e}")
            self.running = False
            return False
    
    def _polling_sync(self):
        """在后台线程中执行轮询同步"""
        while not self._stop_flag:
            try:
                sync_directories(
                    self.source_dir, self.target_dir, 
                    delete_extra=self.delete_extra,
                    ignore_rules=self.ignore_rules
                )
            except Exception as e:
                print(f"轮询同步期间出错: {e}")
            
            # 等待下一次同步，每秒检查一次停止标志
            for _ in range(self.interval):
                if self._stop_flag:
                    break
                time.sleep(1)
    
    def stop(self):
        """停止自动同步"""
        if not self.running:
            print("自动同步未运行")
            return False
            
        try:
            if self.use_watchdog and self.watcher:
                self.watcher.stop()
                self.watcher = None
            else:
                self._stop_flag = True
                # 不需要join，因为是daemon线程
            
            self.running = False
            print("自动同步已停止")
            return True
        
        except Exception as e:
            print(f"停止自动同步时出错: {e}")
            return False
    
    def __enter__(self):
        """上下文管理器支持 - 进入"""
        if not self.running:
            self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器支持 - 退出"""
        if self.running:
            self.stop() 