"""
huangyz_sync 文件同步工具主程序
"""

import os
import sys
import json
import argparse
import time
from pathlib import Path

from huangyz_sync.models.config import SyncConfigManager
from huangyz_sync.core.sync import sync_directories, AutoSync
from huangyz_sync.utils.ignore import IgnoreRules

def main():
    parser = argparse.ArgumentParser(description="huangyz_sync 文件同步工具")
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # sync 子命令
    sync_parser = subparsers.add_parser("sync", help="执行同步任务")
    sync_parser.add_argument("--config", "-c", help="配置文件路径")
    sync_parser.add_argument("--tasks", "-t", nargs="*", help="要执行的任务名称，不指定则执行所有已启用的任务")
    sync_parser.add_argument("--source", "-s", help="源目录路径（直接同步模式）")
    sync_parser.add_argument("--target", "-d", help="目标目录路径（直接同步模式）")
    sync_parser.add_argument("--delete", action="store_true", help="是否删除目标目录中多余的文件")
    
    # watch 子命令
    watch_parser = subparsers.add_parser("watch", help="监视文件夹并自动同步")
    watch_parser.add_argument("--config", "-c", help="配置文件路径")
    watch_parser.add_argument("--task", "-t", help="要监视的任务名称")
    watch_parser.add_argument("--source", "-s", help="源目录路径（直接监视模式）")
    watch_parser.add_argument("--target", "-d", help="目标目录路径（直接监视模式）")
    watch_parser.add_argument("--interval", "-i", type=int, default=60, help="同步间隔（秒）")
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 如果没有指定命令，显示帮助信息
    if not args.command:
        parser.print_help()
        return
    
    # 处理 sync 命令
    if args.command == "sync":
        if args.config:
            # 使用配置文件执行同步
            config_manager = SyncConfigManager(args.config)
            if args.tasks:
                config_manager.run_tasks(args.tasks)
            else:
                config_manager.run_tasks()
        elif args.source and args.target:
            # 直接执行同步
            print(f"直接同步: {args.source} -> {args.target}")
            sync_directories(args.source, args.target, delete_extra=args.delete)
        else:
            print("错误: 必须提供配置文件或源目录和目标目录")
            sync_parser.print_help()
    
    # 处理 watch 命令
    elif args.command == "watch":
        if args.config and args.task:
            # 使用配置文件启动监视
            config_manager = SyncConfigManager(args.config)
            auto_sync = config_manager.start_auto_sync(args.task, interval=args.interval)
            if auto_sync:
                print("监视已启动，按 Ctrl+C 停止...")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("正在停止监视...")
                    auto_sync.stop()
        elif args.source and args.target:
            # 直接启动监视
            from huangyz_sync.core.sync import AutoSync
            print(f"直接监视: {args.source} -> {args.target}")
            auto_sync = AutoSync(args.source, args.target, interval=args.interval)
            auto_sync.start()
            print("监视已启动，按 Ctrl+C 停止...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("正在停止监视...")
                auto_sync.stop()
        else:
            print("错误: 必须提供配置文件和任务名称，或源目录和目标目录")
            watch_parser.print_help()

if __name__ == "__main__":
    main() 