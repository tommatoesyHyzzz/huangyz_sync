import os
import shutil
from pathlib import Path
import datetime
import time
import json
import hashlib
import re
import fnmatch

# 添加新的依赖
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    print("提示: 要使用文件监视功能，请安装watchdog库: pip install watchdog")
    WATCHDOG_AVAILABLE = False

try:
    import pathspec
    PATHSPEC_AVAILABLE = True
except ImportError:
    print("提示: 为获得更好的忽略规则支持，请安装pathspec库: pip install pathspec")
    PATHSPEC_AVAILABLE = False

class FileManager:
    """Windows文件管理器类，提供常见的文件和文件夹操作"""
    
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
                    print(f"  📄 {item} (文件, {FileManager.format_size(size)})")
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
                "大小": FileManager.format_size(file_stat.st_size),
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
    
    @staticmethod
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
    
    class IgnoreRules:
        """管理忽略规则，类似于.gitignore功能"""
        
        def __init__(self, ignore_file=None, patterns=None):
            """
            初始化忽略规则
            
            参数:
                ignore_file: 包含忽略规则的文件路径（类似.gitignore）
                patterns: 忽略规则列表
            """
            self.patterns = patterns or []
            self._spec = None
            
            # 如果提供了忽略文件，从文件加载规则
            if ignore_file and os.path.exists(ignore_file):
                self.load_from_file(ignore_file)
                
            # 编译规则
            self._compile_patterns()
        
        def load_from_file(self, ignore_file):
            """从文件加载忽略规则"""
            try:
                with open(ignore_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line in lines:
                    # 去除注释和空行
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.patterns.append(line)
                
                # 重新编译规则
                self._compile_patterns()
                print(f"从 {ignore_file} 加载了 {len(self.patterns)} 条忽略规则")
                return True
            except Exception as e:
                print(f"加载忽略规则时出错: {e}")
                return False
        
        def _compile_patterns(self):
            """编译忽略规则"""
            if PATHSPEC_AVAILABLE:
                # 使用pathspec库，能更好地支持Git风格的规则
                self._spec = pathspec.PathSpec.from_lines(
                    pathspec.patterns.GitWildMatchPattern, self.patterns)
            else:
                # 使用简单的编译，没有pathspec库时的备用方案
                self._compiled_patterns = []
                for pattern in self.patterns:
                    # 处理特殊前缀
                    is_negation = pattern.startswith('!')
                    if is_negation:
                        pattern = pattern[1:]
                    
                    is_directory = pattern.endswith('/')
                    if is_directory:
                        pattern = pattern[:-1]
                    
                    # 转换为正则表达式模式
                    regex_pattern = fnmatch.translate(pattern)
                    compiled = re.compile(regex_pattern)
                    
                    self._compiled_patterns.append({
                        'pattern': pattern,
                        'compiled': compiled,
                        'is_negation': is_negation,
                        'is_directory': is_directory
                    })
        
        def should_ignore(self, path, is_dir=False):
            """
            检查路径是否应该被忽略
            
            参数:
                path: 要检查的路径
                is_dir: 路径是否是目录
            
            返回:
                bool: 如果应该忽略返回True，否则返回False
            """
            # 对路径进行规范化
            path = path.replace('\\', '/')
            
            # 确保使用相对路径而不仅仅是basename
            # 不要截断为basename，这样会丢失嵌套路径信息
            if os.path.isabs(path):
                # 如果给定的是绝对路径，需要转换成适合匹配的形式
                path = os.path.basename(path)
            
            # 如果是目录，在路径末尾添加/以匹配目录模式
            if is_dir and not path.endswith('/'):
                path_with_slash = path + '/'
            else:
                path_with_slash = path
            
            if PATHSPEC_AVAILABLE:
                # 使用pathspec库检查，对目录尝试两种形式
                return self._spec.match_file(path) or (is_dir and self._spec.match_file(path_with_slash))
            else:
                # 使用自己的简单实现
                result = False
                
                for pattern_info in self._compiled_patterns:
                    # 检查是否匹配（标准形式）
                    if pattern_info['compiled'].match(path):
                        # 取反规则
                        if pattern_info['is_negation']:
                            result = False
                        else:
                            result = True
                        continue
                    
                    # 对目录尝试带斜杠的形式
                    if is_dir and pattern_info['is_directory'] and pattern_info['compiled'].match(path_with_slash):
                        if pattern_info['is_negation']:
                            result = False
                        else:
                            result = True
                
                return result
        
        def add_pattern(self, pattern):
            """添加一个忽略规则"""
            if pattern not in self.patterns:
                self.patterns.append(pattern)
                self._compile_patterns()
                return True
            return False
        
        def remove_pattern(self, pattern):
            """移除一个忽略规则"""
            if pattern in self.patterns:
                self.patterns.remove(pattern)
                self._compile_patterns()
                return True
            return False
    
    @staticmethod
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
                    ignore_rules = FileManager.IgnoreRules(ignore_file=ignore_rules)
                elif not isinstance(ignore_rules, FileManager.IgnoreRules):
                    ignore_rules = FileManager.IgnoreRules(patterns=ignore_rules if isinstance(ignore_rules, list) else [])
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
                        shutil.copy2(source_file, target_file)
                        operations["copied"].append(target_file)
                        continue
                    
                    # 检查文件是否需要更新
                    need_update = False
                    if compare_content:
                        # 通过哈希值比较文件内容
                        source_hash = FileManager.calculate_file_hash(source_file)
                        target_hash = FileManager.calculate_file_hash(target_file)
                        need_update = source_hash != target_hash
                    else:
                        # 通过修改时间比较
                        source_mtime = os.path.getmtime(source_file)
                        target_mtime = os.path.getmtime(target_file)
                        need_update = source_mtime > target_mtime
                    
                    if need_update:
                        shutil.copy2(source_file, target_file)
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
                            os.remove(target_file)
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
                                shutil.rmtree(target_dir_path)
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
    
    @staticmethod
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
    
    @staticmethod
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
                    self.ignore_rules = FileManager.IgnoreRules(ignore_file=ignore_rules)
                elif isinstance(ignore_rules, FileManager.IgnoreRules):
                    self.ignore_rules = ignore_rules
                else:
                    self.ignore_rules = FileManager.IgnoreRules(patterns=ignore_rules if isinstance(ignore_rules, list) else [])
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
                                FileManager.sync_directories(
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
                    self.ignore_rules = FileManager.IgnoreRules(ignore_file=ignore_rules)
                elif isinstance(ignore_rules, FileManager.IgnoreRules):
                    self.ignore_rules = ignore_rules
                else:
                    self.ignore_rules = FileManager.IgnoreRules(patterns=ignore_rules if isinstance(ignore_rules, list) else [])
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
                FileManager.sync_directories(
                    self.source_dir, self.target_dir, 
                    delete_extra=self.delete_extra,
                    ignore_rules=self.ignore_rules
                )
                
                self.running = True
                self._stop_flag = False
                
                if self.use_watchdog:
                    # 使用watchdog监视文件变化
                    self.watcher = FileManager.FolderWatcher(
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
                    FileManager.sync_directories(
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


# 添加新的演示函数
def watcher_demo():
    """演示文件夹监视功能"""
    if not WATCHDOG_AVAILABLE:
        print("请先安装watchdog库: pip install watchdog")
        return
        
    source_dir = os.path.join("D://Personal/test", "watch_source")
    target_dir = os.path.join("D://Personal/test", "watch_target")
    
    # 创建测试目录
    FileManager.create_directory(source_dir)
    FileManager.create_directory(target_dir)
    
    # 在源目录创建一些初始文件
    FileManager.create_file(os.path.join(source_dir, "initial.txt"), "初始文件内容")
    
    print("\n开始监视文件夹并自动同步...")
    print("请在另一个窗口中向以下文件夹添加/修改/删除文件:")
    print(f"源文件夹: {source_dir}")
    print("按Ctrl+C停止监视...\n")
    
    try:
        # 使用上下文管理器自动开始和停止监视
        with FileManager.FolderWatcher(source_dir, target_dir, sync_on_change=True) as watcher:
            # 让主线程继续运行，直到用户按Ctrl+C
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n监视已停止。")


def autosync_demo():
    """演示自动同步功能"""
    source_dir = os.path.join("D://Personal/test", "131e9ffa-e07f-466f-9d6c-f95ad528b811")
    target_dir = os.path.join("D://Personal/test", "131e9ffa-e07f-466f-9d6c-f95ad528b811-2")
    
    # 创建测试目录
    FileManager.create_directory(source_dir)
    FileManager.create_directory(target_dir)
    
    # 在源目录创建一些初始文件
    FileManager.create_file(os.path.join(source_dir, "initial.txt"), "初始文件内容")
    
    print("\n开始自动同步...")
    print("请在另一个窗口中向以下文件夹添加/修改/删除文件:")
    print(f"源文件夹: {source_dir}")
    print("变化将自动同步到目标文件夹。")
    print("按Ctrl+C停止同步...\n")
    
    try:
        # 使用上下文管理器自动开始和停止自动同步
        with FileManager.AutoSync(source_dir, target_dir, delete_extra=True) as auto_sync:
            # 同步会在后台自动进行，直到with块结束
            # 可以在这里做其他操作
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n自动同步已停止。")


def ignore_rules_demo():
    """演示文件忽略规则功能"""
    source_dir = os.path.join("D://Personal/test", "ignore_source")
    target_dir = os.path.join("D://Personal/test", "ignore_target")
    
    # 创建测试目录
    FileManager.create_directory(source_dir)
    FileManager.create_directory(target_dir)
    
    # 创建忽略规则文件
    ignore_file = os.path.join(source_dir, ".syncignore")
    with open(ignore_file, 'w', encoding='utf-8') as f:
        f.write("# 这是注释\n")
        f.write("*.tmp\n")          # 忽略所有.tmp文件
        f.write("temp/\n")          # 忽略temp目录
        f.write("logs/*.log\n")     # 忽略logs目录下的.log文件
        f.write("**/*.bak\n")       # 忽略所有.bak文件
    
    # 在源目录创建一些测试文件和文件夹
    FileManager.create_file(os.path.join(source_dir, "important.txt"), "重要文件内容")
    FileManager.create_file(os.path.join(source_dir, "temp.tmp"), "临时文件内容")
    FileManager.create_directory(os.path.join(source_dir, "temp"))
    FileManager.create_file(os.path.join(source_dir, "temp", "temp_file.txt"), "temp目录中的文件内容")
    FileManager.create_directory(os.path.join(source_dir, "logs"))
    FileManager.create_file(os.path.join(source_dir, "logs", "app.log"), "日志内容")
    FileManager.create_file(os.path.join(source_dir, "logs", "data.txt"), "日志目录中的非日志文件")
    FileManager.create_file(os.path.join(source_dir, "document.txt.bak"), "备份文件内容")
    
    # 创建忽略规则对象
    ignore_rules = FileManager.IgnoreRules(ignore_file=ignore_file)
    
    # 执行同步
    print("\n使用忽略规则同步目录:")
    FileManager.sync_directories(source_dir, target_dir, ignore_rules=ignore_rules)
    
    # 列出目标目录内容
    print("\n同步后的目标目录内容:")
    FileManager.list_directory_contents(target_dir)
    
    # 使用自动同步并带忽略规则
    print("\n启动带忽略规则的自动同步...")
    print("请在另一个窗口中向以下文件夹添加/修改/删除文件:")
    print(f"源文件夹: {source_dir}")
    print("忽略规则将应用于自动同步过程")
    print("按Ctrl+C停止同步...\n")
    
    try:
        # 使用上下文管理器自动开始和停止自动同步
        with FileManager.AutoSync(
            source_dir, target_dir, 
            delete_extra=True, 
            ignore_rules=ignore_file
        ) as auto_sync:
            # 让主线程继续运行，直到用户按Ctrl+C
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n带忽略规则的自动同步已停止。")


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
                ignore_rules = FileManager.IgnoreRules(ignore_file=ignore_file)
            elif ignore_patterns:
                ignore_rules = FileManager.IgnoreRules(patterns=ignore_patterns)
            
            # 执行同步
            try:
                operations = FileManager.sync_directories(
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
            FileManager.AutoSync: 自动同步实例
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
            ignore_rules = FileManager.IgnoreRules(ignore_file=ignore_file)
        elif ignore_patterns:
            ignore_rules = FileManager.IgnoreRules(patterns=ignore_patterns)
        
        # 创建并启动自动同步实例
        try:
            auto_sync = FileManager.AutoSync(
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


# 添加新的演示函数
def config_sync_demo():
    """演示通过配置文件进行同步"""
    config_file = os.path.join("D://Personal/test", "sync_config.json")
    
    # 创建配置管理器
    config_manager = SyncConfigManager()
    
    # 添加同步任务
    config_manager.add_task(
        source_dir=os.path.join("D://Personal/test", "config_source"),
        target_dir=os.path.join("D://Personal/test", "config_target"),
        name="测试同步",
        delete_extra=True,
        ignore_patterns=["*.tmp", "temp/", "*.log"]
    )
    
    # 保存配置到文件
    config_manager.save_config(config_file)
    
    # 创建源目录和一些测试文件
    source_dir = os.path.join("D://Personal/test", "config_source")
    FileManager.create_directory(source_dir)
    FileManager.create_file(os.path.join(source_dir, "important.txt"), "重要文件内容")
    FileManager.create_file(os.path.join(source_dir, "temporary.tmp"), "临时文件内容")
    FileManager.create_directory(os.path.join(source_dir, "temp"))
    FileManager.create_file(os.path.join(source_dir, "temp", "notes.txt"), "临时笔记")
    FileManager.create_file(os.path.join(source_dir, "app.log"), "日志内容")
    
    # 执行所有配置的同步任务
    print("\n执行配置文件中的同步任务:")
    config_manager.run_tasks()
    
    # 从文件重新加载配置并执行
    print("\n从文件重新加载配置:")
    new_config_manager = SyncConfigManager(config_file)
    new_config_manager.run_tasks()
    
    # 使用配置启动自动同步
    print("\n启动基于配置的自动同步...")
    print("请在另一个窗口中向源文件夹添加/修改/删除文件")
    print("变化将根据配置自动同步")
    print("按Ctrl+C停止同步...\n")
    
    try:
        auto_sync = new_config_manager.start_auto_sync("测试同步")
        # 让主线程继续运行，直到用户按Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n基于配置的自动同步已停止。")
        if auto_sync:
            auto_sync.stop()


if __name__ == "__main__":
    # 运行基本演示
    # demo()
    
    # 取消注释以运行额外的演示
    # sync_demo()
    # operation_tracker_demo()
    
    # 新的监视和自动同步演示
    # watcher_demo()
    # autosync_demo()
    
    # 新的忽略规则演示
    # ignore_rules_demo()
    
    # 通过配置文件进行同步的演示
    config_sync_demo()

   # FileManager.delete_directory("D://Personal/test/ignore_source",force=True)