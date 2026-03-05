"""HTTP 客户端封装"""
import requests
import base64
from typing import Dict, Any, Optional
from core.logger import get_logger


class HTTPClient:
    """HTTP 请求封装"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = get_logger(__name__)
        self.api_key: Optional[str] = None
        
    def set_api_key(self, api_key: str):
        """设置 API Key（用于 Stripe 等服务）"""
        self.api_key = api_key
        
    def _build_url(self, path: str) -> str:
        """构建完整 URL"""
        return f"{self.base_url}/{path.lstrip('/')}"
    
    def _get_headers(self, headers: Optional[Dict] = None) -> Dict:
        """合并默认 Header"""
        default = {"Content-Type": "application/x-www-form-urlencoded"}
        
        # 如果设置了 API Key，使用 Stripe 认证
        if self.api_key:
            auth = base64.b64encode(f"{self.api_key}:".encode()).decode()
            default["Authorization"] = f"Basic {auth}"
        
        if headers:
            default.update(headers)
        return default
    
    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """统一请求入口"""
        url = self._build_url(path)
        headers = self._get_headers(headers)
        
        # 记录完整请求信息
        self.logger.info(f"=== REQUEST ===")
        self.logger.info(f"{method} {url}")
        if params:
            self.logger.info(f"Params: {params}")
        if json:
            self.logger.info(f"Body(JSON): {json}")
        if data:
            self.logger.info(f"Body(Data): {data}")
        if self.api_key:
            self.logger.info(f"Auth: Bearer {self.api_key[:10]}...")
        
        resp = self.session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            timeout=self.timeout,
            **kwargs
        )
        
        # 记录完整响应信息
        self.logger.info(f"=== RESPONSE ===")
        self.logger.info(f"Status: {resp.status_code}")
        self.logger.info(f"Body: {resp.text[:500]}")  # 限制长度
        
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
