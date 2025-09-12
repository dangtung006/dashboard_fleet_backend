import httpx
from typing import Any, Dict, Optional

## test: https://jsonplaceholder.typicode.com/posts/1


class MyAsyncRequest:

    def __init__(self, base_urls: Dict[str, str]):
        self.base_urls = base_urls

    def _build_url(self, service: str, path: str) -> str:
        base = self.base_urls.get(service)
        if not base:
            raise ValueError(f"Unknown service: {service}")
        return base.rstrip("/") + "/" + path.lstrip("/")

    def to_json(self, resp):
        return resp.json()

    async def get(
        self, service: str, path: str, params: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            url = self._build_url(service, path)
            return await client.get(url, params=params)

    async def post(
        self, service: str, path: str, data: Any = None, json: Any = None
    ) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            url = self._build_url(service, path)
            return await client.post(url, data=data, json=json)

    async def put(
        self, service: str, path: str, data: Any = None, json: Any = None
    ) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            url = self._build_url(service, path)
            return await client.put(url, data=data, json=json)

    async def delete(self, service: str, path: str) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            url = self._build_url(service, path)
            return await client.delete(url)

    async def next_get(self, data: int, service: str, path: str) -> Any:
        for i in range(data):
            resp = await self.get(service=service, path=path, params=i + 1)
            yield resp
