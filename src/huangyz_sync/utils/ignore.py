"""
忽略规则模块，提供类似.gitignore的忽略文件和目录的功能
"""

import os
import re
import fnmatch

from .common import PATHSPEC_AVAILABLE

if PATHSPEC_AVAILABLE:
    import pathspec

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