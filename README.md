# Huangyz-sync

## 项目描述

通过配置同步window11目录或者文件



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
huangyz_sync/
├── src/
│   ├── huangyz_sync/          # 主包
│   │   ├── config/            # 配置文件目录
│   │   ├── core/              # 核心功能模块
│   │   ├── models/            # 数据模型模块
│   │   ├── utils/             # 工具类模块
│   │   ├── tools/             # 开发工具模块
│   │   └── __init__.py
│   ├── huangyz_sync_gui.py    # GUI应用入口
│   └── main.py                # 命令行入口
├── examples/                  # 示例代码
├── README.md
├── LICENSE
├── .gitignore
├── pyproject.toml            # 项目配置和依赖
└── build.bat                 # 构建脚本
```



##  功能特性

```
- ✅ 可通过配置文件配置信息和忽略规则
```



## 配置文件
JSON格式

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

