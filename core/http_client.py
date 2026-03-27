"""HTTP 客户端封装"""

from typing import Optional

import allure
import requests

from core.logger import get_logger


class HTTPClient:
    """HTTP 请求封装"""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = get_logger(__name__)

    def _build_url(self, path: str) -> str:
        """构建完整 URL"""
        return f"{self.base_url}/{path.lstrip('/')}"

    def _get_headers(self, headers: Optional[dict] = None) -> dict:
        """合并默认 Header"""
        default = {"Content-Type": "application/json"}
        if headers:
            default.update(headers)
        return default

    def request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        """统一请求入口"""
        url = self._build_url(path)
        headers = self._get_headers(headers)

        self.logger.info(f"{method} {url}")

        # 记录请求到 Allure
        req_info = f"{method} {url}\nHeaders: {headers}\nBody: {json}"
        allure.attach(req_info, name="Request", attachment_type=allure.attachment_type.TEXT)

        resp = self.session.request(
            method=method, url=url, params=params, data=data, json=json, headers=headers, timeout=self.timeout, **kwargs
        )

        self.logger.info(f"Response Status: {resp.status_code}")

        # 记录响应到 Allure
        resp_info = f"Status: {resp.status_code}\nBody: {resp.text}"
        allure.attach(resp_info, name="Response", attachment_type=allure.attachment_type.TEXT)
        return resp

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.request("DELETE", path, **kwargs)

    def patch(self, path: str, **kwargs) -> requests.Response:
        return self.request("PATCH", path, **kwargs)
