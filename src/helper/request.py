import httpx
from typing import Any, Dict, Optional


class MyRequest:

    def __init__(self, client: httpx.AsyncClient, base_urls: Dict[str, str]):
        self.client = client
        self.base_urls = base_urls

    def _build_url(self, service: str, path: str) -> str:
        base = self.base_urls.get(service)
        if not base:
            raise ValueError(f"Unknown service: {service}")
        return base.rstrip("/") + "/" + path.lstrip("/")

    async def get(
        self, service: str, path: str, params: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        url = self._build_url(service, path)
        print("url")
        return await self.client.get(url, params=params)

    async def post(
        self, service: str, path: str, data: Any = None, json: Any = None
    ) -> httpx.Response:
        url = self._build_url(service, path)
        return await self.client.post(url, data=data, json=json)

    async def put(
        self, service: str, path: str, data: Any = None, json: Any = None
    ) -> httpx.Response:
        url = self._build_url(service, path)
        return await self.client.put(url, data=data, json=json)

    async def delete(self, service: str, path: str) -> httpx.Response:
        url = self._build_url(service, path)
        return await self.client.delete(url)

    def to_json(self, resp):
        return resp.json()
