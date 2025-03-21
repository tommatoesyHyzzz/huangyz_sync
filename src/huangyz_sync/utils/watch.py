"""
文件监视模块，提供文件夹变化监视功能
"""

import os
import time

from .common import WATCHDOG_AVAILABLE
from .ignore import IgnoreRules

if WATCHDOG_AVAILABLE:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

class FolderWatcher:
    """文件夹监视器 - 监视文件夹变化并执行操作"""
    
    def __init__(self, source_folder, target_folder=None, sync_on_change=False, 
                 callback=None, auto_start=False, recursive=True, ignore_rules=None):
        """
        初始化文件夹监视器
        
        参数:
            source_folder: 要监视的源文件夹
            target_folder: 同步的目标文件夹(如果启用了sync_on_change)
            sync_on_change: 是否在检测到变化时自动同步
            callback: 检测到变化时调用的自定义回调函数
            auto_start: 是否自动启动监视
            recursive: 是否递归监视子文件夹
            ignore_rules: IgnoreRules对象、忽略规则文件路径或规则列表
        """
        if not WATCHDOG_AVAILABLE:
            raise ImportError("请先安装watchdog库: pip install watchdog")
        
        self.source_folder = os.path.abspath(source_folder)
        self.target_folder = os.path.abspath(target_folder) if target_folder else None
        self.sync_on_change = sync_on_change
        self.callback = callback
        self.recursive = recursive
        self.observer = None
        self.running = False
        self.event_handler = None
        
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
        
        # 确保源文件夹存在
        if not os.path.exists(self.source_folder):
            raise FileNotFoundError(f"源文件夹不存在: {self.source_folder}")
            
        # 如果设置了同步但没有提供目标文件夹，报错
        if self.sync_on_change and not self.target_folder:
            raise ValueError("启用同步时必须提供目标文件夹")
            
        # 如果自动启动，初始化并启动监视
        if auto_start:
            self.start()
    
    def start(self):
        """启动文件夹监视"""
        if self.running:
            print("监视器已经在运行中")
            return False
            
        try:
            # 创建一个自定义事件处理器
            class ChangeHandler(FileSystemEventHandler):
                def __init__(self, watcher):
                    self.watcher = watcher
                    self.processing = False
                    # 添加一个小延迟避免同一变化多次触发
                    self.last_processed = time.time()
                    
                def on_any_event(self, event):
                    # 忽略目录创建事件，因为这些通常会伴随文件创建事件
                    if event.is_directory and event.event_type == 'created':
                        return
                        
                    # 忽略隐藏文件/目录
                    if os.path.basename(event.src_path).startswith('.'):
                        return
                    
                    # 检查是否应该忽略
                    if self.watcher.ignore_rules:
                        # 获取相对路径用于检查
                        rel_path = os.path.relpath(
                            event.src_path, self.watcher.source_folder)
                        if self.watcher.ignore_rules.should_ignore(
                            rel_path, event.is_directory):
                            print(f"忽略变化: {event.event_type} - {event.src_path}")
                            return
                        
                    # 添加一个小延迟避免频繁触发
                    current_time = time.time()
                    if current_time - self.last_processed < 1:  # 1秒内不重复处理
                        return
                        
                    self.last_processed = current_time
                    
                    # 如果正在处理，不再触发新事件
                    if self.processing:
                        return
                        
                    self.processing = True
                    try:
                        print(f"检测到变化: {event.event_type} - {event.src_path}")
                        
                        # 如果设置了要同步
                        if self.watcher.sync_on_change:
                            print("正在同步变更...")
                            from ..core.sync import sync_directories
                            sync_directories(
                                self.watcher.source_folder, 
                                self.watcher.target_folder,
                                delete_extra=True,
                                ignore_rules=self.watcher.ignore_rules
                            )
                                
                        # 如果有自定义回调，调用它
                        if self.watcher.callback:
                            self.watcher.callback(event)
                    finally:
                        self.processing = False
            
            # 创建事件处理器实例
            self.event_handler = ChangeHandler(self)
            
            # 创建观察者
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler, 
                self.source_folder, 
                recursive=self.recursive
            )
            
            # 启动观察者
            self.observer.start()
            self.running = True
            print(f"开始监视文件夹: {self.source_folder}")
            if self.sync_on_change:
                print(f"变化将自动同步到: {self.target_folder}")
            if self.ignore_rules:
                print(f"使用忽略规则，共 {len(self.ignore_rules.patterns)} 条")
            return True
        
        except Exception as e:
            print(f"启动文件夹监视时出错: {e}")
            if self.observer:
                self.observer.stop()
                self.observer = None
            self.running = False
            return False
    
    def stop(self):
        """停止文件夹监视"""
        if not self.running:
            print("监视器未运行")
            return False
            
        try:
            self.observer.stop()
            self.observer.join()  # 等待观察者线程终止
            self.observer = None
            self.running = False
            print(f"停止监视文件夹: {self.source_folder}")
            return True
        except Exception as e:
            print(f"停止文件夹监视时出错: {e}")
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