"""
操作跟踪模块，记录和重放文件操作
"""

import os
import json
import datetime
from ..core.file_manager import FileManager

class OperationTracker:
    """跟踪文件操作并保存操作历史，以便后续同步"""
    
    def __init__(self, base_dir=None):
        """初始化操作跟踪器"""
        self.operations = []
        self.base_dir = base_dir
    
    def record_operation(self, operation_type, source_path, target_path=None, content=None):
        """记录一个文件操作"""
        timestamp = datetime.datetime.now().isoformat()
        
        # 如果设置了基础目录，记录相对路径
        if self.base_dir:
            if source_path and os.path.isabs(source_path):
                source_path = os.path.relpath(source_path, self.base_dir)
            if target_path and os.path.isabs(target_path):
                target_path = os.path.relpath(target_path, self.base_dir)
        
        operation = {
            "type": operation_type,
            "timestamp": timestamp,
            "source": source_path,
            "target": target_path,
            "content": content
        }
        
        self.operations.append(operation)
        return operation
    
    def save_to_file(self, filename):
        """将操作历史保存到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "base_dir": self.base_dir,
                    "operations": self.operations
                }, f, ensure_ascii=False, indent=2)
            print(f"操作历史已保存到: {filename}")
            return True
        except Exception as e:
            print(f"保存操作历史时出错: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filename):
        """从文件加载操作历史"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tracker = cls(data.get("base_dir"))
            tracker.operations = data.get("operations", [])
            print(f"从 {filename} 加载了操作历史")
            return tracker
        except Exception as e:
            print(f"加载操作历史时出错: {e}")
            return None
    
    def apply_operations(self, target_base_dir=None):
        """应用记录的操作到目标目录"""
        if not target_base_dir and not self.base_dir:
            print("错误: 未指定目标目录")
            return False
        
        base = target_base_dir or self.base_dir
        success_count = 0
        error_count = 0
        
        for op in self.operations:
            try:
                op_type = op["type"]
                source = op["source"]
                target = op.get("target")
                content = op.get("content")
                
                # 转换为绝对路径
                if source and not os.path.isabs(source):
                    source = os.path.join(base, source)
                if target and not os.path.isabs(target):
                    target = os.path.join(base, target)
                
                # 根据操作类型执行相应的操作
                if op_type == "create_directory":
                    FileManager.create_directory(source)
                elif op_type == "create_file":
                    FileManager.create_file(source, content or "")
                elif op_type == "copy_file":
                    FileManager.copy_file(source, target)
                elif op_type == "copy_directory":
                    FileManager.copy_directory(source, target)
                elif op_type == "move_file_or_directory":
                    FileManager.move_file_or_directory(source, target)
                elif op_type == "rename_file_or_directory":
                    FileManager.rename_file_or_directory(source, target)
                elif op_type == "delete_file":
                    FileManager.delete_file(source)
                elif op_type == "delete_directory":
                    FileManager.delete_directory(source, force=True)
                else:
                    print(f"未知操作类型: {op_type}")
                    error_count += 1
                    continue
                
                success_count += 1
            except Exception as e:
                print(f"应用操作时出错: {e}, 操作: {op}")
                error_count += 1
        
        print(f"操作应用完成: {success_count} 成功, {error_count} 失败")
        return error_count == 0 