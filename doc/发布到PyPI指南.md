# 发布到 PyPI 指南

本文档介绍如何将 `wecom-notifier` 打包并发布到 TestPyPI 与正式 PyPI。

## 📋 目录

- [先决条件](#先决条件)
- [快速发布流程](#快速发布流程)
- [详细步骤](#详细步骤)
  - [1. 版本号与变更日志](#1-版本号与变更日志)
  - [2. 本地构建](#2-本地构建)
  - [3. 先发布到 TestPyPI（推荐）](#3-先发布到-testpypi推荐)
  - [4. 发布到正式 PyPI](#4-发布到正式-pypi)
- [上传方式详解](#上传方式详解)
- [常见问题与排查](#常见问题与排查)
- [GitHub Actions 自动发布](#github-actions-自动发布)
- [快速清单](#快速清单)

---

## 先决条件

- Python 3.7+
- 已创建 [PyPI](https://pypi.org/) 与 [TestPyPI](https://test.pypi.org/) 账户
- 已创建 API Token（推荐，不使用用户名/密码）
  - [PyPI Token 创建](https://pypi.org/manage/account/token/)
  - [TestPyPI Token 创建](https://test.pypi.org/manage/account/token/)

### 一次性环境准备

```bash
python -m pip install --upgrade pip
pip install -e .[dev]
```

说明：`dev` 额外依赖中已包含 `build` 与 `twine`，用于构建与上传。

---

## 快速发布流程

如果你已经熟悉流程，可以直接执行：

```bash
# 1. 清理旧产物
rm -rf dist build *.egg-info wecom_notifier.egg-info

# 2. 构建包
python -m build

# 3. 校验
twine check dist/*

# 4. 上传到 TestPyPI 测试
twine upload -r testpypi dist/*

# 5. 验证安装
pip install -i https://test.pypi.org/simple/ wecom-notifier==0.3.0

# 6. 确认无误后上传到 PyPI
twine upload dist/*
```

---

## 详细步骤

### 1. 版本号与变更日志

**版本源**：
- 项目版本定义在 `pyproject.toml` 的 `project.version`
- 包内导出版本在 `wecom_notifier/__init__.py` 的 `__version__`

**每次发布前**：
1. 更新 `CHANGELOG.md` - 记录本次版本的所有变更
2. 同步修改版本号（遵循[语义化版本](https://semver.org/lang/zh-CN/)）：
   - `pyproject.toml` → `version = "0.3.0"`
   - `wecom_notifier/__init__.py` → `__version__ = "0.3.0"`

### 2. 本地构建

**清理旧产物**（可选但推荐）：

```bash
rm -rf dist build *.egg-info wecom_notifier.egg-info
```

**构建 sdist 与 wheel**：

```bash
python -m build
```

产物将生成到 `dist/` 目录：
- `wecom_notifier-<version>.tar.gz` - 源代码分发包
- `wecom_notifier-<version>-py3-none-any.whl` - 预编译wheel包

**校验元数据**：

```bash
twine check dist/*
```

输出应显示：
```
Checking dist/wecom_notifier-0.3.0-py3-none-any.whl: PASSED
Checking dist/wecom_notifier-0.3.0.tar.gz: PASSED
```

### 3. 先发布到 TestPyPI（推荐）

TestPyPI 是 PyPI 的测试环境，可以安全地测试发布流程。

**上传到 TestPyPI**：

```bash
twine upload -r testpypi dist/*
```

或使用完整URL：

```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

**提示输入凭证**：
- Username: `__token__`
- Password: 你的 TestPyPI Token（以 `pypi-` 开头）

**从 TestPyPI 安装验证**：

```bash
# 创建新的虚拟环境
python -m venv .venv_test
source .venv_test/bin/activate  # Linux/Mac
# 或
.venv_test\Scripts\activate  # Windows

# 从 TestPyPI 安装
pip install -i https://test.pypi.org/simple/ wecom-notifier==0.3.0

# 验证版本
python -c "import wecom_notifier; print(wecom_notifier.__version__)"
# 应输出: 0.3.0

# 测试基本功能
python -c "from wecom_notifier import WeComNotifier, FeishuNotifier; print('导入成功')"
```

### 4. 发布到正式 PyPI

确认在 TestPyPI 验证通过后，上传到正式 PyPI：

```bash
twine upload dist/*
```

**提示输入凭证**：
- Username: `__token__`
- Password: 你的 PyPI Token

**上传成功后验证**：

1. 查看 PyPI 页面：https://pypi.org/project/wecom-notifier/0.3.0/

2. 安装测试：
```bash
pip install --upgrade wecom-notifier
python -c "import wecom_notifier; print(wecom_notifier.__version__)"
# 应输出: 0.3.0
```

3. 测试新功能：
```bash
# 测试企业微信
python examples/basic_usage.py

# 测试飞书
python examples/feishu_usage.py

# 测试多平台
python examples/multi_platform.py
```

---

## 上传方式详解

### 方式 1: 使用 API Token（推荐）

设置环境变量：

```bash
# Linux/Mac
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcGl...  # 你的完整 API token

# Windows PowerShell
$env:TWINE_USERNAME="__token__"
$env:TWINE_PASSWORD="pypi-AgEIcGl..."

# Windows CMD
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-AgEIcGl...
```

然后直接上传：

```bash
python -m twine upload dist/*
```

### 方式 2: 交互式输入

直接运行上传命令，然后输入凭证：

```bash
python -m twine upload dist/*
# Username: __token__
# Password: pypi-AgEIcGl...  # 你的 API token（输入时不显示）
```

### 方式 3: 使用 .pypirc 配置文件

在 `~/.pypirc` (Linux/Mac) 或 `%USERPROFILE%\.pypirc` (Windows) 中配置：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcGl...  # 你的 PyPI API token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcGl...  # 你的 TestPyPI API token
```

然后直接运行：

```bash
twine upload dist/*              # 上传到 PyPI
twine upload -r testpypi dist/*  # 上传到 TestPyPI
```

**注意**：`.pypirc` 文件包含敏感信息，确保：
- 设置正确的文件权限：`chmod 600 ~/.pypirc`
- 不要提交到版本控制系统

---

## 常见问题与排查

### 1. `File already exists`

**问题**：PyPI 不允许覆盖已存在的版本。

**解决**：
- 提升版本号（例如 `0.3.0` → `0.3.1`）
- 更新 `pyproject.toml` 和 `__init__.py`
- 重新构建并上传

### 2. `twine check` 失败

**问题**：README 渲染错误或元数据问题。

**解决**：
- 检查 `README.md` 的 Markdown 语法（表格、链接）
- 确认 `pyproject.toml` 中 `readme = "README.md"` 已正确设置
- 验证所有必需字段已填写

### 3. 缺少 LICENSE

**问题**：wheel 包中缺少 LICENSE 文件。

**解决**：
- 确认 `pyproject.toml` 中有 `license-files = ["LICENSE"]`
- 清理后重新构建：`rm -rf dist build && python -m build`

### 4. 依赖未随包安装

**问题**：用户安装后缺少依赖。

**解决**：
- 确认 `pyproject.toml` 中 `dependencies` 已正确定义
- 对于可选依赖，使用 `optional-dependencies`：
  ```toml
  [project.optional-dependencies]
  moderation = ["pypinyin>=0.44.0", "pyahocorasick>=2.0.0"]
  ```
- 用户可通过 `pip install wecom-notifier[moderation]` 安装可选依赖

### 5. 包结构不完整

**问题**：子包未包含在分发包中。

**解决**：
- 使用 `find_packages` 自动发现：
  ```toml
  [tool.setuptools.packages.find]
  where = ["."]
  include = ["wecom_notifier*"]
  ```
- 验证构建产物：
  ```bash
  tar -tzf dist/wecom_notifier-0.3.0.tar.gz | grep wecom_notifier
  ```

### 6. 网络问题

**问题**：上传超时或连接失败。

**解决**：
- 使用国内镜像源可能导致上传失败，确保直接连接 PyPI
- 检查防火墙和代理设置
- 使用 `--verbose` 查看详细日志：
  ```bash
  twine upload --verbose dist/*
  ```

---

## GitHub Actions 自动发布

如需启用自动发布（打 tag 触发），在仓库创建 `.github/workflows/publish.yml`：

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - "v*"

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

**设置步骤**：
1. 在仓库的 **Settings** → **Secrets and variables** → **Actions** 中添加 `PYPI_API_TOKEN`
2. 确保在打 tag 前已同步更新版本号与 `CHANGELOG.md`
3. 创建并推送 tag：
   ```bash
   git tag v0.3.0
   git push origin v0.3.0
   ```

---

## 快速清单

发布前检查：

- [ ] 更新版本号：`pyproject.toml` 与 `wecom_notifier/__init__.py`
- [ ] 更新 `CHANGELOG.md` - 记录所有变更
- [ ] 清理旧产物：`rm -rf dist build *.egg-info`
- [ ] 本地构建：`python -m build`
- [ ] 校验：`twine check dist/*` - 确保 PASSED
- [ ] 先发 TestPyPI 验证：`twine upload -r testpypi dist/*`
- [ ] 从 TestPyPI 安装测试：确认功能正常
- [ ] 正式 PyPI 发布：`twine upload dist/*`
- [ ] 验证 PyPI 页面和安装
- [ ] 在 README 中更新安装与用法说明（如有变更）
- [ ] 创建 GitHub Release 并附上 CHANGELOG

---

## 安全与合规

- ✅ 不要将真实 Webhook 或 Token 写入仓库
- ✅ 不要提交 `dist/`、`build/`、`*.egg-info/` 等构建产物
- ✅ 将 PyPI Token 存放在密码管理器或 CI 密钥存储中
- ✅ `.pypirc` 文件设置正确权限：`chmod 600 ~/.pypirc`
- ✅ 使用 `.gitignore` 排除敏感文件和构建产物

---

## 🎉 v0.3.0 版本更新内容

**主要新特性**：
- ✨ 新增飞书（Feishu/Lark）平台支持
- ✨ 多平台架构重构（core + platforms）
- ✨ 内容审核功能改为可选依赖 `[moderation]`
- ✨ 完整的向后兼容性保证

**升级说明**：
- 基础安装：`pip install wecom-notifier`
- 带审核功能：`pip install wecom-notifier[moderation]`

详见 [CHANGELOG.md](../CHANGELOG.md)

---

准备好发布 v0.3.0 了吗？运行以下命令开始：

```bash
# 上传到 TestPyPI 测试
twine upload -r testpypi dist/*

# 确认无误后上传到 PyPI
twine upload dist/*
```

🚀 祝发布顺利！
