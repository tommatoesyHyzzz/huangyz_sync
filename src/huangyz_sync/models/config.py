"""
配置管理模块，处理同步任务配置
"""

import os
import json
from ..core.file_manager import FileManager
from ..utils.ignore import IgnoreRules
from ..core.sync import sync_directories, AutoSync

class SyncConfigManager:
    """管理同步配置，支持从配置文件加载和保存配置"""
    
    def __init__(self, config_file=None):
        """
        初始化同步配置管理器
        
        参数:
            config_file: 配置文件路径，如果提供，将从中加载配置
        """
        self.config_file = config_file
        self.tasks = []
        
        if config_file and os.path.exists(config_file):
            self.load_config()
    
    def load_config(self, config_file=None):
        """
        从配置文件加载同步任务配置
        
        参数:
            config_file: 可选的配置文件路径，如果不提供则使用初始化时的路径
        
        返回:
            bool: 加载是否成功
        """
        file_path = config_file or self.config_file
        if not file_path:
            print("错误: 未指定配置文件路径")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if isinstance(config, dict):
                # 单个任务配置
                self.tasks = [config]
            elif isinstance(config, list):
                # 多个任务配置
                self.tasks = config
            else:
                print(f"错误: 无效的配置格式，应为字典或列表")
                return False
            
            # 更新当前配置文件路径
            if config_file:
                self.config_file = config_file
                
            print(f"从 {file_path} 加载了 {len(self.tasks)} 个同步任务配置")
            return True
        except Exception as e:
            print(f"加载配置文件时出错: {e}")
            return False
    
    def save_config(self, config_file=None):
        """
        保存当前配置到文件
        
        参数:
            config_file: 可选的配置文件路径，如果不提供则使用初始化时的路径
        
        返回:
            bool: 保存是否成功
        """
        file_path = config_file or self.config_file
        if not file_path:
            print("错误: 未指定配置文件路径")
            return False
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
            
            # 更新当前配置文件路径
            if config_file:
                self.config_file = config_file
                
            print(f"配置已保存到: {file_path}")
            return True
        except Exception as e:
            print(f"保存配置文件时出错: {e}")
            return False
    
    def add_task(self, source_dir, target_dir, name=None, enabled=True, 
                 delete_extra=False, compare_content=True, ignore_file=None, ignore_patterns=None):
        """
        添加一个同步任务配置
        
        参数:
            source_dir: 源目录路径
            target_dir: 目标目录路径
            name: 任务名称
            enabled: 是否启用此任务
            delete_extra: 是否删除目标目录中多余的文件
            compare_content: 是否比较文件内容而不只是时间戳
            ignore_file: 忽略规则文件路径
            ignore_patterns: 忽略规则列表
        
        返回:
            dict: 添加的任务配置
        """
        task = {
            "name": name or f"Task_{len(self.tasks) + 1}",
            "enabled": enabled,
            "source_dir": os.path.abspath(source_dir),
            "target_dir": os.path.abspath(target_dir),
            "options": {
                "delete_extra": delete_extra,
                "compare_content": compare_content
            },
            "ignore": {}
        }
        
        if ignore_file:
            task["ignore"]["file"] = ignore_file
        
        if ignore_patterns:
            task["ignore"]["patterns"] = ignore_patterns
        
        self.tasks.append(task)
        return task
    
    def remove_task(self, task_index_or_name):
        """
        移除指定的同步任务
        
        参数:
            task_index_or_name: 任务索引或名称
        
        返回:
            bool: 是否成功移除
        """
        if isinstance(task_index_or_name, int):
            if 0 <= task_index_or_name < len(self.tasks):
                self.tasks.pop(task_index_or_name)
                return True
        else:
            for i, task in enumerate(self.tasks):
                if task.get("name") == task_index_or_name:
                    self.tasks.pop(i)
                    return True
        
        print(f"错误: 未找到任务: {task_index_or_name}")
        return False
    
    def update_task(self, task_index_or_name, **kwargs):
        """
        更新指定任务的配置
        
        参数:
            task_index_or_name: 任务索引或名称
            **kwargs: 要更新的配置项
        
        返回:
            bool: 是否成功更新
        """
        task_index = None
        
        if isinstance(task_index_or_name, int):
            if 0 <= task_index_or_name < len(self.tasks):
                task_index = task_index_or_name
        else:
            for i, task in enumerate(self.tasks):
                if task.get("name") == task_index_or_name:
                    task_index = i
                    break
        
        if task_index is None:
            print(f"错误: 未找到任务: {task_index_or_name}")
            return False
        
        # 更新配置
        task = self.tasks[task_index]
        
        # 更新顶层属性
        for key in ["name", "enabled", "source_dir", "target_dir"]:
            if key in kwargs:
                task[key] = kwargs[key]
        
        # 更新选项
        if "options" in kwargs:
            if not "options" in task:
                task["options"] = {}
            for opt_key, opt_value in kwargs["options"].items():
                task["options"][opt_key] = opt_value
        
        # 更新忽略规则
        if "ignore_file" in kwargs or "ignore_patterns" in kwargs:
            if not "ignore" in task:
                task["ignore"] = {}
            
            if "ignore_file" in kwargs:
                task["ignore"]["file"] = kwargs["ignore_file"]
            
            if "ignore_patterns" in kwargs:
                task["ignore"]["patterns"] = kwargs["ignore_patterns"]
        
        return True
    
    def run_tasks(self, task_indices_or_names=None):
        """
        执行指定的同步任务，如果未指定则执行所有已启用的任务
        
        参数:
            task_indices_or_names: 要执行的任务索引或名称列表，如果为None则执行所有已启用的任务
        
        返回:
            dict: 每个任务的执行结果
        """
        results = {}
        tasks_to_run = []
        
        # 确定要执行的任务
        if task_indices_or_names is None:
            # 执行所有已启用的任务
            tasks_to_run = [(i, task) for i, task in enumerate(self.tasks) if task.get("enabled", True)]
        else:
            # 执行指定的任务
            for index_or_name in task_indices_or_names:
                if isinstance(index_or_name, int):
                    if 0 <= index_or_name < len(self.tasks):
                        tasks_to_run.append((index_or_name, self.tasks[index_or_name]))
                else:
                    for i, task in enumerate(self.tasks):
                        if task.get("name") == index_or_name:
                            tasks_to_run.append((i, task))
                            break
        
        # 执行每个任务
        for i, task in tasks_to_run:
            task_name = task.get("name", f"Task_{i}")
            print(f"\n执行同步任务: {task_name}")
            
            source_dir = task.get("source_dir")
            target_dir = task.get("target_dir")
            
            if not source_dir or not os.path.exists(source_dir):
                print(f"错误: 源目录不存在: {source_dir}")
                results[task_name] = {"status": "error", "message": "源目录不存在"}
                continue
            
            # 提取选项
            options = task.get("options", {})
            delete_extra = options.get("delete_extra", False)
            compare_content = options.get("compare_content", True)
            
            # 处理忽略规则
            ignore_config = task.get("ignore", {})
            ignore_file = ignore_config.get("file")
            ignore_patterns = ignore_config.get("patterns")
            
            ignore_rules = None
            if ignore_file and os.path.exists(ignore_file):
                ignore_rules = IgnoreRules(ignore_file=ignore_file)
            elif ignore_patterns:
                ignore_rules = IgnoreRules(patterns=ignore_patterns)
            
            # 执行同步
            try:
                operations = sync_directories(
                    source_dir, target_dir, 
                    delete_extra=delete_extra,
                    compare_content=compare_content,
                    ignore_rules=ignore_rules
                )
                
                results[task_name] = {
                    "status": "success",
                    "operations": operations
                }
            except Exception as e:
                print(f"执行任务 {task_name} 时出错: {e}")
                results[task_name] = {
                    "status": "error",
                    "message": str(e)
                }
        
        return results
    
    def start_auto_sync(self, task_index_or_name, interval=60, use_watchdog=True):
        """
        启动指定任务的自动同步
        
        参数:
            task_index_or_name: 任务索引或名称
            interval: 同步间隔(秒)
            use_watchdog: 是否使用watchdog监视文件变化
        
        返回:
            AutoSync: 自动同步实例
        """
        task = None
        
        if isinstance(task_index_or_name, int):
            if 0 <= task_index_or_name < len(self.tasks):
                task = self.tasks[task_index_or_name]
        else:
            for t in self.tasks:
                if t.get("name") == task_index_or_name:
                    task = t
                    break
        
        if not task:
            print(f"错误: 未找到任务: {task_index_or_name}")
            return None
        
        if not task.get("enabled", True):
            print(f"警告: 任务 {task.get('name')} 已禁用，但仍将启动自动同步")
        
        source_dir = task.get("source_dir")
        target_dir = task.get("target_dir")
        
        if not source_dir or not os.path.exists(source_dir):
            print(f"错误: 源目录不存在: {source_dir}")
            return None
        
        # 提取选项
        options = task.get("options", {})
        delete_extra = options.get("delete_extra", False)
        
        # 处理忽略规则
        ignore_config = task.get("ignore", {})
        ignore_file = ignore_config.get("file")
        ignore_patterns = ignore_config.get("patterns")
        
        ignore_rules = None
        if ignore_file and os.path.exists(ignore_file):
            ignore_rules = IgnoreRules(ignore_file=ignore_file)
        elif ignore_patterns:
            ignore_rules = IgnoreRules(patterns=ignore_patterns)
        
        # 创建并启动自动同步实例
        try:
            auto_sync = AutoSync(
                source_dir, target_dir,
                interval=interval,
                use_watchdog=use_watchdog,
                delete_extra=delete_extra,
                ignore_rules=ignore_rules
            )
            
            auto_sync.start()
            print(f"已启动任务 {task.get('name')} 的自动同步")
            return auto_sync
        except Exception as e:
            print(f"启动自动同步时出错: {e}")
            return None

    @staticmethod
    def create_example_config(config_file):
        """
        创建示例配置文件
        
        参数:
            config_file: 配置文件路径
        
        返回:
            bool: 是否成功创建
        """
        example_config = [
            {
                "name": "Documents_Backup",
                "enabled": True,
                "source_dir": os.path.expanduser("~/Documents"),
                "target_dir": os.path.expanduser("~/Backups/Documents"),
                "options": {
                    "delete_extra": True,
                    "compare_content": True
                },
                "ignore": {
                    "patterns": [
                        "*.tmp",
                        "*.bak",
                        "temp/",
                        "logs/*.log"
                    ]
                }
            },
            {
                "name": "Project_Sync",
                "enabled": False,
                "source_dir": os.path.expanduser("~/Projects/MyApp"),
                "target_dir": os.path.expanduser("~/Backups/Projects/MyApp"),
                "options": {
                    "delete_extra": False,
                    "compare_content": True
                },
                "ignore": {
                    "file": os.path.expanduser("~/Projects/MyApp/.syncignore")
                }
            }
        ]
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(example_config, f, ensure_ascii=False, indent=2)
            
            print(f"示例配置文件已创建: {config_file}")
            return True
        except Exception as e:
            print(f"创建示例配置文件时出错: {e}")
            return False

    def get_task_names(self):
        """
        获取所有同步任务的名称列表
        
        返回:
            list: 所有任务的名称列表
        """
        return [task.get("name") for task in self.tasks] 