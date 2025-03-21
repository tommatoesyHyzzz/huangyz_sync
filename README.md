# Huangyz-sync

## 项目信息

同步window11文件夹或者文件



## 依赖版本

```
pytest>=6.0
black>=21.5b2
isort>=5.9.1
watchdog>=2.0.0
pathspec>=0.9.0 
```



## 项目结构

```
file_ops/
    __init__.py      # 包入口点，导出主要类
    core.py          # 核心文件操作功能
    ignore.py        # 忽略规则功能（类似.gitignore）
    sync.py          # 文件同步功能
    watch.py         # 文件监视功能
    track.py         # 操作跟踪功能
    config.py        # 配置管理功能
    utils.py      	 # 工具函数
```



## 配置信息

```
[
  {
    name: 'Documents_Backup', // 任务名称
    enabled: false, // 是否启用
    source_dir: '~/Documents', // 源目录
    target_dir: '~/Backups/Documents', // 目标目录
    options: {
      delete_extra: true, // 是否删除目标目录中多余的文件
      compare_content: true, // 是否比较文件内容而不只是时间戳
    },
    ignore: {
      patterns: ['*.tmp', '*.bak', 'temp/', 'logs/*.log'], // 忽略规则
      //file: '~/Projects/MyApp/.syncignore', // 忽略规则文件
    },
  }
]
```

