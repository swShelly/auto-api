"""Pytest 配置和 Fixtures"""

from pathlib import Path

import pytest
import yaml

from core.auth import AuthManager
from core.http_client import HTTPClient

# 读取配置
CONFIG_PATH = Path(__file__).parent / "config" / "config.yaml"


def load_config() -> dict:
    """加载配置文件"""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def pytest_addoption(parser):
    """添加命令行选项"""
    parser.addoption("--env", action="store", default="dev", help="选择环境: dev/staging/prod")


@pytest.fixture(scope="session")
def config(request):
    """全局配置"""
    env = request.config.getoption("--env")
    cfg = load_config()
    cfg["current_env"] = env
    cfg["base_url"] = cfg["env"][env]["base_url"]
    return cfg


@pytest.fixture(scope="session")
def http_client(config):
    """HTTP 客户端（Session 级复用）"""
    return HTTPClient(base_url=config["base_url"], timeout=config.get("timeout", 30))


@pytest.fixture(scope="session")
def auth_manager(http_client, config):
    """鉴权管理器"""
    auth_cfg = config["auth"]
    return AuthManager(http_client=http_client, username=auth_cfg["username"], password=auth_cfg["password"])


@pytest.fixture(scope="session")
def token(auth_manager):
    """获取 Token（Session 级，整个测试周期复用）"""
    return auth_manager.get_token()
