# 接口自动化测试项目

## 项目结构

```
auto-api/
├── config/
│   └── config.yaml        # 环境配置
├── core/
│   ├── http_client.py     # HTTP 封装
│   ├── auth.py           # 鉴权管理
│   └── logger.py         # 日志
├── testcases/
│   └── test_booking.py   # 测试用例
├── reports/              # 测试报告
├── conftest.py           # Pytest fixtures
├── pytest.ini            # Pytest 配置
└── requirements.txt      # 依赖
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行测试
pytest

# 3. 使用allure（需要安装 allure）
# 3.1 生成报告
pytest --alluredir=reports/allure
# 3.2 启动本地服务器查看报告
allure serve reports/allure

# 4. 直接html查看简单版本报告
# 4.1 生成报告
pytest --html=reports/report.html
# 4.2 文件形式查看报告
open report.html
```

## 环境

- dev: 开发环境
- staging: 预发布环境
- prod: 生产环境

切换环境：`pytest --env=staging`
