 🚀 上传到 PyPI

  现在需要你手动上传到 PyPI，因为需要身份验证。有两种方式：

  方式 1: 使用 API Token（推荐）

  # 设置环境变量（使用你的 PyPI API token）
  export TWINE_USERNAME=__token__
  export TWINE_PASSWORD=pypi-AgEIcGl...  # 你的完整 API token

  # 上传
  python -m twine upload dist/*

  方式 2: 交互式输入

  python -m twine upload dist/*
  # 然后输入：
  # Username: __token__
  # Password: pypi-AgEIcGl...  # 你的 API token

  方式 3: 使用 .pypirc 配置文件

  在 ~/.pypirc (Windows: %USERPROFILE%\.pypirc) 中配置：

  [pypi]
  username = __token__
  password = pypi-AgEIcGl...  # 你的 API token

  然后直接运行：
  python -m twine upload dist/*

  ---
  📝 上传后验证

  上传成功后，你可以：

  1. 查看 PyPI 页面：https://pypi.org/project/wecom-notifier/0.1.5/
  2. 安装测试：
  pip install --upgrade wecom-notifier
  python -c "import wecom_notifier; print(wecom_notifier.__version__)"
  # 应该输出: 0.1.5
  3. 测试新功能：
  python test_pagination.py

  ---
  🎉 版本 0.1.5 更新内容

  - 页码标记优化：从 "续上页/未完待续" 改为清晰的 (Page X/Y) 格式
  - 智能显示：仅当分段数 > 1 时显示页码
  - 调试增强：SegmentInfo 新增页码信息字段

  准备好上传了吗？运行上面的任一命令即可！🚀