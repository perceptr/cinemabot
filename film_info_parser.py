from abc import ABCMeta

import aiohttp

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/"
    "xml;q=0.9,image/webp,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/89.0.4389.114 Safari/537.36",
}


class Searcher(metaclass=ABCMeta):
    def __init__(self, url: str, token: str) -> None:
        self._url = url
        self._token = token

    async def fetch(self, params: dict) -> dict:
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(**params) as response:
                return await response.json()


class IMDBSearcher(Searcher):
    def __init__(self, url: str, token: str):
        super().__init__(url, token)
        self._url += f"?apikey={token}"

    async def get_film_info_by_title(self, title: str) -> dict:
        params = {"url": self._url + f"&t={title}", "headers": HEADERS}
        return await self.fetch(params)


class KinopoiskSearcher(Searcher):
    def __init__(self, url: str, token: str):
        super().__init__(url, token)

    async def get_film_info_by_title(self, title: str) -> dict:
        params = {
            "url": self._url + f"films/search-by-keyword?" f"keyword={title}&page=1",
            "headers": HEADERS | {"X-API-KEY": self._token},
        }
        return await self.fetch(params)
