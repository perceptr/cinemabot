import aiohttp

USER_AGENT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/61.0.3163.100 Safari/537.36"
}

URL = "https://www.googleapis.com/customsearch/v1"


async def get_response_json(term, api_key, cx):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=URL,
            headers=USER_AGENT,
            params=dict(key=api_key, cx=cx, q=term)
        ) as resp:
            return await resp.json()


async def get_link(term, api_key, cx):
    return (await get_response_json(term, api_key, cx))["items"][0]["formattedUrl"]
