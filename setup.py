from setuptools import setup, find_packages

setup(
    name="huangyz_sync",
    version="1.0.0",
    description="文件同步工具",
    author="huangyz",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "watchdog>=2.1.0",
        "pathspec>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "huangyz-sync=main:main",
        ],
    },
    python_requires=">=3.6",
) 