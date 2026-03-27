"""鉴权管理"""

from core.http_client import HTTPClient
from core.logger import get_logger


class AuthManager:
    """Token 管理"""

    def __init__(self, http_client: HTTPClient, username: str, password: str):
        self.client = http_client
        self.username = username
        self.password = password
        self.token: str | None = None
        self.logger = get_logger(__name__)

    def login(self) -> str:
        """登录获取 Token"""
        resp = self.client.post("/auth/login", json={"username": self.username, "password": self.password})

        if resp.status_code == 200:
            self.token = resp.json().get("token")
            self.logger.info(f"登录成功，Token: {self.token[:10]}...")
            return self.token
        else:
            self.logger.error(f"登录失败: {resp.status_code} - {resp.text}")
            resp.raise_for_status()

    def get_token(self, force_refresh: bool = False) -> str:
        """获取 Token（缓存机制）"""
        if not self.token or force_refresh:
            self.login()
        return self.token or ""

    def get_auth_headers(self) -> dict:
        """获取带鉴权的 Header"""
        token = self.get_token()
        return {"Cookie": f"token={token}"}

    def clear(self):
        """清除 Token"""
        self.token = None
