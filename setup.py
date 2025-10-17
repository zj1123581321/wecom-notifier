"""
企业微信通知器安装脚本
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wecom-notifier",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="企业微信机器人通知组件，支持频率控制、长文本分段等功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/wecom-notifier",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Chat",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    keywords="wecom wechat enterprise-wechat robot notification webhook",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/wecom-notifier/issues",
        "Source": "https://github.com/yourusername/wecom-notifier",
    },
)
