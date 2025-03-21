@echo off
chcp 65001 >nul
echo 正在安装依赖...
pip install -e .
pip install pyinstaller

echo 选择打包类型:
echo 1. 命令行工具
echo 2. 图形界面应用
echo 3. 两者都打包

set /p packtype="请输入打包类型的数字(1/2/3): "

if "%packtype%"=="1" (
    echo 正在打包命令行工具...
    python -m PyInstaller huangyz_sync.spec
    echo 命令行工具打包完成！
    echo 可执行文件位于 dist/huangyz_sync.exe
) else if "%packtype%"=="2" (
    echo 正在打包图形界面应用...
    python -m PyInstaller huangyz_sync_gui.spec
    echo 图形界面应用打包完成！
    echo 可执行文件位于 dist/huangyz_sync_gui.exe
) else if "%packtype%"=="3" (
    echo 正在打包命令行工具...
    python -m PyInstaller huangyz_sync.spec
    echo 命令行工具打包完成！
    
    echo 正在打包图形界面应用...
    python -m PyInstaller huangyz_sync_gui.spec
    echo 图形界面应用打包完成！
    
    echo 两个应用都已打包完成！
    echo 命令行工具: dist/huangyz_sync.exe
    echo 图形界面应用: dist/huangyz_sync_gui.exe
) else (
    echo 无效的选择，将打包两者
    echo 正在打包命令行工具...
    python -m PyInstaller huangyz_sync.spec
    echo 命令行工具打包完成！
    
    echo 正在打包图形界面应用...
    python -m PyInstaller huangyz_sync_gui.spec
    echo 图形界面应用打包完成！
    
    echo 两个应用都已打包完成！
    echo 命令行工具: dist/huangyz_sync.exe
    echo 图形界面应用: dist/huangyz_sync_gui.exe
)

pause 