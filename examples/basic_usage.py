"""
文件操作库基本使用示例
"""

import os
import sys
import time

# 添加父目录到路径，以便导入file_ops包
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 修改导入方式，从正确的子模块导入
from src.huangyz_sync.core.file_manager import FileManager
from src.huangyz_sync.models.config import SyncConfigManager
from src.huangyz_sync.core.sync import AutoSync

def basic_file_operations_demo():
    """演示基本文件操作"""
    print("\n=== 基本文件操作示例 ===")
    
    # 创建临时测试目录
    test_dir = os.path.join(os.getcwd(), "test_file_ops")
    FileManager.create_directory(test_dir)
    
    # 创建文件
    test_file = os.path.join(test_dir, "test.txt")
    FileManager.create_file(test_file, "这是一个测试文件的内容")
    
    # 获取文件信息
    FileManager.get_file_info(test_file)
    
    # 列出目录内容
    FileManager.list_directory_contents(test_dir)
    
    # 复制文件
    copy_file = os.path.join(test_dir, "test_copy.txt")
    FileManager.copy_file(test_file, copy_file)
    
    # 重命名文件
    FileManager.rename_file_or_directory(copy_file, "test_renamed.txt")
    
    # 删除文件和目录
    FileManager.delete_file(test_file)
    FileManager.delete_directory(test_dir, force=True)

def sync_demo():
    """演示目录同步功能"""
    print("\n=== 目录同步示例 ===")
    
    # 创建源和目标目录
    source_dir = os.path.join(os.getcwd(), "sync_source")
    target_dir = os.path.join(os.getcwd(), "sync_target")
    
    FileManager.create_directory(source_dir)
    FileManager.create_directory(target_dir)
    
    # 在源目录中创建一些文件
    FileManager.create_file(os.path.join(source_dir, "file1.txt"), "文件1的内容")
    FileManager.create_file(os.path.join(source_dir, "file2.txt"), "文件2的内容")
    
    # 创建子目录
    sub_dir = os.path.join(source_dir, "subdir")
    FileManager.create_directory(sub_dir)
    FileManager.create_file(os.path.join(sub_dir, "file3.txt"), "文件3的内容")
    
    # 创建忽略规则
    ignore_rules = FileManager.IgnoreRules(patterns=["*.tmp", "temp/"])
    
    # 同步目录
    from src.huangyz_sync.core.sync import sync_directories
    sync_directories(source_dir, target_dir, delete_extra=True, ignore_rules=ignore_rules)
    
    # 清理
    FileManager.delete_directory(source_dir, force=True)
    FileManager.delete_directory(target_dir, force=True)

def config_sync_demo():
    """演示通过配置文件进行同步"""
    # 使用相对路径而非硬编码路径
    config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src/huangyz_sync/config", "sync-config.json")
  
    
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
        auto_sync = new_config_manager.start_auto_sync("Test_Sync")
        # 让主线程继续运行，直到用户按Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n基于配置的自动同步已停止。")
        if auto_sync:
            auto_sync.stop()

def config_sync_demo2():
    """演示通过配置文件进行同步"""
    print("\n=== 配置文件同步示例 ===")
    
    # 创建测试目录
    source_dir = os.path.join(os.getcwd(), "config_source")
    target_dir = os.path.join(os.getcwd(), "config_target")
    
    FileManager.create_directory(source_dir)
    FileManager.create_directory(target_dir)
    
    # 在源目录中创建一些文件
    FileManager.create_file(os.path.join(source_dir, "config1.txt"), "配置示例文件1")
    FileManager.create_file(os.path.join(source_dir, "config2.txt"), "配置示例文件2")
    
    # 创建配置文件
    config_file = os.path.join(os.getcwd(), "sync_config.json")
    
    # 创建配置管理器
    config_manager = SyncConfigManager(config_file)
    
    # 添加同步任务
    config_manager.add_task(
        source_dir=source_dir,
        target_dir=target_dir,
        name="Test_Sync",
        delete_extra=True,
        ignore_patterns=["*.bak", "*.tmp"]
    )
    
    # 保存配置
    config_manager.save_config()
    
    # 执行同步任务
    config_manager.run_tasks()
    
    # 清理
    FileManager.delete_directory(source_dir, force=True)
    FileManager.delete_directory(target_dir, force=True)
    FileManager.delete_file(config_file)

def auto_sync_demo():
    """演示自动同步功能"""
    print("\n=== 自动同步示例 ===")
    
    # 创建测试目录
    source_dir = os.path.join(os.getcwd(), "auto_source")
    target_dir = os.path.join(os.getcwd(), "auto_target")
    
    FileManager.create_directory(source_dir)
    
    # 初始化自动同步
    auto_sync = AutoSync(
        source_dir=source_dir,
        target_dir=target_dir,
        interval=5,  # 使用轮询方式时的间隔(秒)
        use_watchdog=False,  # 使用轮询而不是watchdog，以便演示
        delete_extra=True
    )
    
    # 启动自动同步
    auto_sync.start()
    
    # 在源目录中创建一个文件
    print("\n添加一个文件到源目录...")
    FileManager.create_file(os.path.join(source_dir, "auto_file.txt"), "自动同步测试文件")
    
    # 等待同步完成
    print("等待5秒钟同步...")
    time.sleep(5)
    
    # 检查目标目录
    print("\n检查目标目录:")
    FileManager.list_directory_contents(target_dir)
    
    # 停止自动同步
    auto_sync.stop()
    
    # 清理
    FileManager.delete_directory(source_dir, force=True)
    FileManager.delete_directory(target_dir, force=True)

if __name__ == "__main__":
    try:
        # basic_file_operations_demo()
        # sync_demo()
        # config_sync_demo()
        config_sync_demo()
        
        print("\n所有示例已成功运行！")
    except Exception as e:
        import traceback
        print(f"运行示例时出错: {e}")
        traceback.print_exc() 