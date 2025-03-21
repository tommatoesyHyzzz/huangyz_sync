"""
huangyz_sync 图形界面
"""
import sys
import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from huangyz_sync.models.config import SyncConfigManager
from huangyz_sync.core.sync import AutoSync
from huangyz_sync.utils.common import WATCHDOG_AVAILABLE

class SyncApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("huangyz_sync 文件同步工具")
        self.geometry("800x600")
        
        # 配置变量
        self.config_file = None
        self.config_manager = None
        self.auto_sync_instances = {}
        
        # 创建主界面
        self.create_widgets()
        
        # 尝试加载上次的配置
        self.try_load_last_config()
    
    def create_widgets(self):
        # 创建菜单栏
        self.create_menu()
        
        # 使用Notebook创建选项卡界面
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 任务选项卡
        self.tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tasks_frame, text="同步任务")
        self.create_tasks_tab()
        
        # 直接同步选项卡
        self.direct_sync_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.direct_sync_frame, text="直接同步")
        self.create_direct_sync_tab()
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_menu(self):
        menu_bar = tk.Menu(self)
        
        # 文件菜单
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="打开配置", command=self.open_config)
        file_menu.add_command(label="保存配置", command=self.save_config)
        file_menu.add_command(label="另存为", command=self.save_config_as)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit)
        menu_bar.add_cascade(label="文件", menu=file_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        
        self.config(menu=menu_bar)
    
    def create_tasks_tab(self):
        # 任务列表框架
        list_frame = ttk.LabelFrame(self.tasks_frame, text="同步任务列表")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建任务列表
        self.task_listbox = tk.Listbox(list_frame)
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.task_listbox.bind('<<ListboxSelect>>', self.on_task_select)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_listbox.config(yscrollcommand=scrollbar.set)
        
        # 任务详情框架
        details_frame = ttk.LabelFrame(self.tasks_frame, text="任务详情")
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 任务控制按钮
        control_frame = ttk.Frame(details_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="添加任务", command=self.add_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="编辑任务", command=self.edit_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="删除任务", command=self.delete_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="执行同步", command=self.run_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="开始监视", command=self.start_watch).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="停止监视", command=self.stop_watch).pack(side=tk.LEFT, padx=5)
        
        # 任务信息显示
        info_frame = ttk.Frame(details_frame)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.task_info_text = tk.Text(info_frame, wrap=tk.WORD, height=10)
        self.task_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.task_info_text.yview)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_info_text.config(yscrollcommand=info_scrollbar.set)
    
    def create_direct_sync_tab(self):
        # 源目录
        source_frame = ttk.Frame(self.direct_sync_frame)
        source_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(source_frame, text="源目录:").pack(side=tk.LEFT, padx=5)
        self.source_var = tk.StringVar()
        ttk.Entry(source_frame, textvariable=self.source_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(source_frame, text="浏览...", command=lambda: self.browse_directory(self.source_var)).pack(side=tk.LEFT, padx=5)
        
        # 目标目录
        target_frame = ttk.Frame(self.direct_sync_frame)
        target_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(target_frame, text="目标目录:").pack(side=tk.LEFT, padx=5)
        self.target_var = tk.StringVar()
        ttk.Entry(target_frame, textvariable=self.target_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(target_frame, text="浏览...", command=lambda: self.browse_directory(self.target_var)).pack(side=tk.LEFT, padx=5)
        
        # 选项
        options_frame = ttk.LabelFrame(self.direct_sync_frame, text="选项")
        options_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.delete_extra_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="删除目标目录中多余的文件", variable=self.delete_extra_var).pack(anchor=tk.W, padx=5, pady=2)
        
        self.compare_content_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="比较文件内容(而不只是修改时间)", variable=self.compare_content_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # 忽略规则
        ignore_frame = ttk.LabelFrame(self.direct_sync_frame, text="忽略规则")
        ignore_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        self.ignore_text = tk.Text(ignore_frame, wrap=tk.WORD, height=10)
        self.ignore_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ignore_scrollbar = ttk.Scrollbar(ignore_frame, orient=tk.VERTICAL, command=self.ignore_text.yview)
        ignore_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ignore_text.config(yscrollcommand=ignore_scrollbar.set)
        
        # 按钮
        button_frame = ttk.Frame(self.direct_sync_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="执行同步", command=self.run_direct_sync).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="开始监视", command=self.start_direct_watch).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="停止监视", command=self.stop_direct_watch).pack(side=tk.LEFT, padx=5)
        
        # 直接同步的自动同步实例
        self.direct_auto_sync = None
    
    def browse_directory(self, var):
        directory = filedialog.askdirectory()
        if directory:
            var.set(directory)
    
    def open_config(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.config_manager = SyncConfigManager(file_path)
            self.config_file = file_path
            self.update_task_list()
            self.status_var.set(f"已加载配置: {file_path}")
            # 保存为最后使用的配置
            self.save_last_config_path(file_path)
    
    def save_config(self):
        if not self.config_manager:
            return self.save_config_as()
        
        self.config_manager.save_config()
        self.status_var.set(f"配置已保存: {self.config_file}")
    
    def save_config_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            if not self.config_manager:
                self.config_manager = SyncConfigManager()
            self.config_manager.save_config(file_path)
            self.config_file = file_path
            self.status_var.set(f"配置已保存: {file_path}")
            # 保存为最后使用的配置
            self.save_last_config_path(file_path)
    
    def save_last_config_path(self, path):
        try:
            config_dir = Path.home() / ".huangyz_sync"
            config_dir.mkdir(exist_ok=True)
            with open(config_dir / "last_config.txt", "w") as f:
                f.write(path)
        except Exception as e:
            print(f"保存最后配置路径时出错: {e}")
    
    def try_load_last_config(self):
        try:
            config_path = Path.home() / ".huangyz_sync" / "last_config.txt"
            if config_path.exists():
                with open(config_path, "r") as f:
                    last_path = f.read().strip()
                if os.path.exists(last_path):
                    self.config_manager = SyncConfigManager(last_path)
                    self.config_file = last_path
                    self.update_task_list()
                    self.status_var.set(f"已加载上次配置: {last_path}")
        except Exception as e:
            print(f"加载上次配置路径时出错: {e}")
    
    def update_task_list(self):
        self.task_listbox.delete(0, tk.END)
        if self.config_manager:
            for i, task in enumerate(self.config_manager.tasks):
                status = "✓" if task.get("enabled", True) else "✗"
                self.task_listbox.insert(tk.END, f"{status} {task.get('name', f'Task_{i}')}")
    
    def on_task_select(self, event):
        if not self.config_manager:
            return
            
        selection = self.task_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if index < len(self.config_manager.tasks):
            task = self.config_manager.tasks[index]
            self.display_task_info(task)
    
    def display_task_info(self, task):
        self.task_info_text.delete(1.0, tk.END)
        
        # 格式化任务信息
        info = f"任务名称: {task.get('name', '')}\n"
        info += f"状态: {'启用' if task.get('enabled', True) else '禁用'}\n"
        info += f"源目录: {task.get('source_dir', '')}\n"
        info += f"目标目录: {task.get('target_dir', '')}\n\n"
        
        # 选项
        options = task.get('options', {})
        info += "选项:\n"
        info += f"  - 删除多余文件: {'是' if options.get('delete_extra', False) else '否'}\n"
        info += f"  - 比较文件内容: {'是' if options.get('compare_content', True) else '否'}\n\n"
        
        # 忽略规则
        ignore = task.get('ignore', {})
        info += "忽略规则:\n"
        
        if 'file' in ignore:
            info += f"  - 使用忽略规则文件: {ignore['file']}\n"
            
        if 'patterns' in ignore:
            info += "  - 忽略模式:\n"
            for pattern in ignore['patterns']:
                info += f"    * {pattern}\n"
        
        # 监视状态
        task_name = task.get('name', '')
        if task_name in self.auto_sync_instances:
            info += "\n状态: 正在监视中"
        else:
            info += "\n状态: 未监视"
            
        self.task_info_text.insert(1.0, info)
    
    def add_task(self):
        # 打开任务编辑对话框
        self.edit_task_dialog()
    
    def edit_task(self):
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个任务")
            return
            
        index = selection[0]
        task = self.config_manager.tasks[index]
        self.edit_task_dialog(task, index)
    
    def edit_task_dialog(self, task=None, task_index=None):
        dialog = tk.Toplevel(self)
        dialog.title("编辑任务" if task else "添加任务")
        dialog.geometry("500x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建表单
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 任务名称
        ttk.Label(form_frame, text="任务名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=task.get('name', '') if task else '')
        ttk.Entry(form_frame, textvariable=name_var, width=40).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 启用状态
        enabled_var = tk.BooleanVar(value=task.get('enabled', True) if task else True)
        ttk.Checkbutton(form_frame, text="启用此任务", variable=enabled_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 源目录
        ttk.Label(form_frame, text="源目录:").grid(row=2, column=0, sticky=tk.W, pady=5)
        source_var = tk.StringVar(value=task.get('source_dir', '') if task else '')
        ttk.Entry(form_frame, textvariable=source_var, width=40).grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Button(form_frame, text="浏览...", command=lambda: self.browse_directory(source_var)).grid(row=2, column=2, padx=5)
        
        # 目标目录
        ttk.Label(form_frame, text="目标目录:").grid(row=3, column=0, sticky=tk.W, pady=5)
        target_var = tk.StringVar(value=task.get('target_dir', '') if task else '')
        ttk.Entry(form_frame, textvariable=target_var, width=40).grid(row=3, column=1, sticky=tk.W, pady=5)
        ttk.Button(form_frame, text="浏览...", command=lambda: self.browse_directory(target_var)).grid(row=3, column=2, padx=5)
        
        # 选项
        options = task.get('options', {}) if task else {}
        
        ttk.Label(form_frame, text="选项:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        delete_extra_var = tk.BooleanVar(value=options.get('delete_extra', False))
        ttk.Checkbutton(form_frame, text="删除目标目录中多余的文件", variable=delete_extra_var).grid(row=5, column=0, columnspan=3, sticky=tk.W, padx=20)
        
        compare_content_var = tk.BooleanVar(value=options.get('compare_content', True))
        ttk.Checkbutton(form_frame, text="比较文件内容(而不只是修改时间)", variable=compare_content_var).grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=20)
        
        # 忽略规则
        ttk.Label(form_frame, text="忽略规则:").grid(row=7, column=0, sticky=tk.NW, pady=5)
        
        ignore = task.get('ignore', {}) if task else {}
        
        # 忽略规则文件
        ttk.Label(form_frame, text="忽略规则文件:").grid(row=8, column=0, sticky=tk.W, padx=20)
        ignore_file_var = tk.StringVar(value=ignore.get('file', ''))
        ttk.Entry(form_frame, textvariable=ignore_file_var, width=40).grid(row=8, column=1, sticky=tk.W)
        ttk.Button(form_frame, text="浏览...", command=lambda: self.browse_file(ignore_file_var)).grid(row=8, column=2, padx=5)
        
        # 忽略模式
        ttk.Label(form_frame, text="忽略模式(每行一条):").grid(row=9, column=0, sticky=tk.NW, padx=20, pady=5)
        
        patterns_frame = ttk.Frame(form_frame)
        patterns_frame.grid(row=9, column=1, columnspan=2, sticky=tk.NSEW, pady=5)
        
        patterns_text = tk.Text(patterns_frame, wrap=tk.WORD, width=40, height=10)
        patterns_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        patterns_scroll = ttk.Scrollbar(patterns_frame, orient=tk.VERTICAL, command=patterns_text.yview)
        patterns_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        patterns_text.config(yscrollcommand=patterns_scroll.set)
        
        # 填充忽略模式
        if 'patterns' in ignore:
            patterns_text.insert(1.0, "\n".join(ignore['patterns']))
        
        # 按钮区域
        button_frame = ttk.Frame(dialog, padding=10)
        button_frame.pack(fill=tk.X)
        
        def save_task():
            # 收集表单数据
            new_task = {
                "name": name_var.get(),
                "enabled": enabled_var.get(),
                "source_dir": source_var.get(),
                "target_dir": target_var.get(),
                "options": {
                    "delete_extra": delete_extra_var.get(),
                    "compare_content": compare_content_var.get()
                },
                "ignore": {}
            }
            
            # 忽略规则文件
            if ignore_file_var.get():
                new_task["ignore"]["file"] = ignore_file_var.get()
            
            # 忽略模式
            patterns_text_content = patterns_text.get(1.0, tk.END).strip()
            if patterns_text_content:
                patterns = [p for p in patterns_text_content.split("\n") if p.strip()]
                if patterns:
                    new_task["ignore"]["patterns"] = patterns
            
            # 验证
            if not new_task["name"]:
                messagebox.showerror("错误", "任务名称不能为空")
                return
                
            if not new_task["source_dir"]:
                messagebox.showerror("错误", "源目录不能为空")
                return
                
            if not new_task["target_dir"]:
                messagebox.showerror("错误", "目标目录不能为空")
                return
            
            # 保存任务
            if task_index is not None:
                # 更新现有任务
                self.config_manager.tasks[task_index] = new_task
            else:
                # 添加新任务
                self.config_manager.tasks.append(new_task)
            
            # 更新界面
            self.update_task_list()
            dialog.destroy()
        
        ttk.Button(button_frame, text="保存", command=save_task).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def browse_file(self, var):
        file_path = filedialog.askopenfilename()
        if file_path:
            var.set(file_path)
    
    def delete_task(self):
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个任务")
            return
            
        index = selection[0]
        task = self.config_manager.tasks[index]
        
        # 检查任务是否正在监视
        task_name = task.get("name", "")
        if task_name in self.auto_sync_instances:
            messagebox.showerror("错误", f"任务 '{task_name}' 正在监视中，请先停止监视")
            return
        
        # 确认删除
        if messagebox.askyesno("确认", f"确定要删除任务 '{task_name}' 吗?"):
            self.config_manager.tasks.pop(index)
            self.update_task_list()
            self.task_info_text.delete(1.0, tk.END)
    
    def run_task(self):
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个任务")
            return
            
        index = selection[0]
        task = self.config_manager.tasks[index]
        task_name = task.get("name", f"Task_{index}")
        
        # 执行同步
        result = self.config_manager.run_tasks([task_name])
        
        # 显示结果
        if task_name in result:
            task_result = result[task_name]
            if task_result["status"] == "success":
                ops = task_result["operations"]
                messagebox.showinfo("同步完成", 
                    f"任务 '{task_name}' 同步完成:\n" +
                    f"- 复制了 {len(ops['copied'])} 个新文件\n" +
                    f"- 更新了 {len(ops['updated'])} 个文件\n" +
                    f"- 删除了 {len(ops['deleted'])} 个多余文件\n" +
                    f"- 跳过了 {len(ops['skipped'])} 个相同文件\n" +
                    f"- 忽略了 {len(ops['ignored'])} 个文件/文件夹"
                )
            else:
                messagebox.showerror("同步失败", f"任务 '{task_name}' 同步失败: {task_result['message']}")
    
    def start_watch(self):
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个任务")
            return
            
        index = selection[0]
        task = self.config_manager.tasks[index]
        task_name = task.get("name", f"Task_{index}")
        
        # 检查是否已经在监视
        if task_name in self.auto_sync_instances:
            messagebox.showinfo("提示", f"任务 '{task_name}' 已经在监视中")
            return
        
        # 启动监视
        auto_sync = self.config_manager.start_auto_sync(task_name)
        if auto_sync:
            self.auto_sync_instances[task_name] = auto_sync
            self.status_var.set(f"已开始监视任务: {task_name}")
            # 更新显示
            self.display_task_info(task)
            
            # 如果是第一个监视任务，提示用户
            if len(self.auto_sync_instances) == 1:
                messagebox.showinfo("监视已启动", "文件监视已启动，程序将在后台运行。\n关闭窗口时监视将自动停止。")
        else:
            messagebox.showerror("启动失败", f"无法启动任务 '{task_name}' 的监视")
    
    def stop_watch(self):
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个任务")
            return
            
        index = selection[0]
        task = self.config_manager.tasks[index]
        task_name = task.get("name", f"Task_{index}")
        
        # 检查是否正在监视
        if task_name not in self.auto_sync_instances:
            messagebox.showinfo("提示", f"任务 '{task_name}' 未在监视中")
            return
        
        # 停止监视
        auto_sync = self.auto_sync_instances[task_name]
        auto_sync.stop()
        del self.auto_sync_instances[task_name]
        self.status_var.set(f"已停止监视任务: {task_name}")
        # 更新显示
        self.display_task_info(task)
    
    def run_direct_sync(self):
        source_dir = self.source_var.get()
        target_dir = self.target_var.get()
        
        if not source_dir or not target_dir:
            messagebox.showinfo("提示", "请指定源目录和目标目录")
            return
        
        if not os.path.exists(source_dir):
            messagebox.showerror("错误", f"源目录不存在: {source_dir}")
            return
        
        # 获取选项
        delete_extra = self.delete_extra_var.get()
        compare_content = self.compare_content_var.get()
        
        # 获取忽略规则
        ignore_patterns = None
        ignore_text_content = self.ignore_text.get(1.0, tk.END).strip()
        if ignore_text_content:
            ignore_patterns = [p for p in ignore_text_content.split("\n") if p.strip()]
        
        from huangyz_sync.utils.ignore import IgnoreRules
        ignore_rules = IgnoreRules(patterns=ignore_patterns) if ignore_patterns else None
        
        # 执行同步
        from huangyz_sync.core.sync import sync_directories
        try:
            self.status_var.set("正在同步...")
            operations = sync_directories(
                source_dir, target_dir,
                delete_extra=delete_extra,
                compare_content=compare_content,
                ignore_rules=ignore_rules
            )
            
            # 显示结果
            messagebox.showinfo("同步完成", 
                f"同步完成:\n" +
                f"- 复制了 {len(operations['copied'])} 个新文件\n" +
                f"- 更新了 {len(operations['updated'])} 个文件\n" +
                f"- 删除了 {len(operations['deleted'])} 个多余文件\n" +
                f"- 跳过了 {len(operations['skipped'])} 个相同文件\n" +
                f"- 忽略了 {len(operations['ignored'])} 个文件/文件夹"
            )
            self.status_var.set("同步完成")
        except Exception as e:
            messagebox.showerror("同步失败", f"同步过程中出错: {e}")
            self.status_var.set("同步失败")
    
    def start_direct_watch(self):
        source_dir = self.source_var.get()
        target_dir = self.target_var.get()
        
        if not source_dir or not target_dir:
            messagebox.showinfo("提示", "请指定源目录和目标目录")
            return
        
        if not os.path.exists(source_dir):
            messagebox.showerror("错误", f"源目录不存在: {source_dir}")
            return
            
        # 如果已经有监视实例在运行，先停止
        if self.direct_auto_sync:
            messagebox.showinfo("提示", "已有监视任务正在运行，请先停止")
            return
        
        # 获取选项
        delete_extra = self.delete_extra_var.get()
        
        # 获取忽略规则
        ignore_patterns = None
        ignore_text_content = self.ignore_text.get(1.0, tk.END).strip()
        if ignore_text_content:
            ignore_patterns = [p for p in ignore_text_content.split("\n") if p.strip()]
        
        from huangyz_sync.utils.ignore import IgnoreRules
        ignore_rules = IgnoreRules(patterns=ignore_patterns) if ignore_patterns else None
        
        # 启动监视
        try:
            from huangyz_sync.core.sync import AutoSync
            self.direct_auto_sync = AutoSync(
                source_dir, target_dir,
                delete_extra=delete_extra,
                ignore_rules=ignore_rules
            )
            self.direct_auto_sync.start()
            self.status_var.set(f"已开始监视: {source_dir} -> {target_dir}")
            
            messagebox.showinfo("监视已启动", "文件监视已启动，程序将在后台运行。\n关闭窗口时监视将自动停止。")
        except Exception as e:
            messagebox.showerror("启动失败", f"启动监视时出错: {e}")
    
    def stop_direct_watch(self):
        if not self.direct_auto_sync:
            messagebox.showinfo("提示", "没有运行中的监视任务")
            return
        
        try:
            self.direct_auto_sync.stop()
            self.direct_auto_sync = None
            self.status_var.set("已停止监视")
            messagebox.showinfo("监视已停止", "文件监视已停止")
        except Exception as e:
            messagebox.showerror("停止失败", f"停止监视时出错: {e}")
    
    def show_about(self):
        messagebox.showinfo(
            "关于", 
            "huangyz_sync 文件同步工具\n"
            "版本: 1.0.0\n\n"
            "一个简单、高效的文件同步工具，支持:\n"
            "- 基于配置的同步任务管理\n"
            "- 实时文件监视和自动同步\n"
            "- 文件内容比较\n"
            "- 忽略规则\n\n"
            "© 2023 huangyz"
        )
    
    def quit(self):
        """安全退出程序，确保停止所有监视任务"""
        if self.auto_sync_instances or self.direct_auto_sync:
            if messagebox.askyesno("确认", "有正在运行的监视任务，确定要退出吗？"):
                # 停止所有监视任务
                for task_name, auto_sync in list(self.auto_sync_instances.items()):
                    try:
                        auto_sync.stop()
                        print(f"已停止任务 '{task_name}' 的监视")
                    except:
                        pass
                
                if self.direct_auto_sync:
                    try:
                        self.direct_auto_sync.stop()
                        print("已停止直接监视任务")
                    except:
                        pass
                
                # 退出程序
                self.destroy()
        else:
            # 直接退出
            self.destroy()

def main():
    app = SyncApp()
    app.protocol("WM_DELETE_WINDOW", app.quit)  # 处理窗口关闭事件
    app.mainloop()

if __name__ == "__main__":
    main()