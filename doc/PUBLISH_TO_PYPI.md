# 发布到 PyPI 指南

本文档介绍如何将本项目 `wecom-notifier` 打包并发布到 TestPyPI 与正式 PyPI。

## 先决条件

- Python 3.7+
- 已创建 PyPI 与 TestPyPI 账户
- 已创建 API Token（推荐，不使用用户名/密码）

## 一次性环境准备

```bash
python -m pip install --upgrade pip
pip install -e .[dev]
```

说明：`dev` 额外依赖中已包含 `build` 与 `twine`，用于构建与上传。

## 版本号与变更日志

- 版本源：
  - 项目版本定义在 `pyproject.toml` 的 `project.version`。
  - 包内导出版本在 `wecom_notifier/__init__.py` 的 `__version__`，需与上面保持一致。
- 每次发布：
  - 更新 `CHANGELOG.md`
  - 同步修改 `pyproject.toml` 与 `wecom_notifier/__init__.py` 的版本号（遵循语义化版本）

## 本地构建

清理旧产物（可选）：

```bash
rm -rf dist build *.egg-info wecom_notifier.egg-info
```

构建 sdist 与 wheel：

```bash
python -m build
``;

产物将生成到 `dist/` 目录，例如：

- `wecom_notifier-<version>.tar.gz`
- `wecom_notifier-<version>-py3-none-any.whl`

校验元数据：

```bash
twine check dist/*
```

## 先发布到 TestPyPI（推荐）

1) 在 TestPyPI 创建 API Token，并在本机保存到安全位置。

2) 上传：

```bash
twine upload -r testpypi dist/*
```

提示输入用户名与密码：

- 用户名：`__token__`
- 密码：复制你的 TestPyPI token（以 `pypi-` 开头）

3) 从 TestPyPI 安装验证：

```bash
python -m venv .venv_testpypi && . .venv_testpypi/Scripts/activate  # Windows PowerShell
pip install -i https://test.pypi.org/simple/ wecom-notifier==<version>
python -c "import wecom_notifier as wn; print(wn.__version__)"
```

或运行示例：

```bash
python examples/basic_usage.py
```

## 发布到正式 PyPI

确认在 TestPyPI 验证通过后，上传到 PyPI：

```bash
twine upload dist/*
```

与 TestPyPI 相同：

- 用户名：`__token__`
- 密码：你的 PyPI token

上传成功后，可通过：

```bash
pip install wecom-notifier==<version>
```

## 常见问题与排查

- `File already exists`：
  - PyPI 不允许覆盖已存在的版本。请提升版本号（例如 `0.1.1` -> `0.1.2`），重新构建并上传。
- `twine check` 失败：
  - 检查 `README.md` 的渲染错误（表格/链接），或缺失 `long_description` 类型；本项目已通过 `readme = "README.md"` 自动设置为 Markdown。
- 缺少 LICENSE：
  - 已在 `pyproject.toml` 中包含 `license-files`，确保 wheel 包含 `LICENSE`。如仍缺失，执行一次清理后再构建。
- 依赖未随包安装：
  - `dependencies` 已在 `pyproject.toml` 定义（例如 `requests`）。确认未在运行环境内被其他约束覆盖。

## 安全与合规

- 不要将真实 Webhook 或 Token 写入仓库；示例中使用占位符。
- 不要提交 `dist/` 或 `.egg-info/` 等构建产物到版本库。
- 请将 PyPI/TestPyPI Token 存放在密码管理器或 CI 的密钥存储中。

## 可选：GitHub Actions 自动发布

如需启用自动发布（打 tag 触发），可在仓库添加工作流（示例片段）：

```yaml
name: release
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
      - run: python -m pip install --upgrade pip
      - run: pip install build twine
      - run: python -m build
      - env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

注意：

- 在仓库的 Secrets 中添加 `PYPI_API_TOKEN`。
- 确保你在打 tag 前已同步更新版本号与 `CHANGELOG.md`。

## 快速清单（Checklist）

- [ ] 更新版本号：`pyproject.toml` 与 `wecom_notifier/__init__.py`
- [ ] 更新 `CHANGELOG.md`
- [ ] 本地构建：`python -m build`
- [ ] 校验：`twine check dist/*`
- [ ] 先发 TestPyPI 验证
- [ ] 正式 PyPI 发布
- [ ] 在 README 中更新安装与用法说明（如有变更）

