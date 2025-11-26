import aiohttp
from typing import Optional, Dict, Any

async def get_json(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None):
    async with aiohttp.ClientSession() as s:
        async with s.get(url, headers=headers, params=params, timeout=60) as r:
            r.raise_for_status()
            return await r.json()

async def get_bytes(url: str, headers: Optional[Dict[str, str]] = None):
    async with aiohttp.ClientSession() as s:
        async with s.get(url, headers=headers, timeout=180) as r:
            r.raise_for_status()
            data = await r.read()
            return data, r.headers.get("Content-Type")
