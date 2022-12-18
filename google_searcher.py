import aiohttp
from bs4 import BeautifulSoup
import asyncio
from requests import get

usr_agent = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/61.0.3163.100 Safari/537.36'
}


async def get_response_text(term, results, lang, start):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                url="https://www.google.com/search",
                headers=usr_agent,
                params=dict(
                    q=term,
                    num=results + 2,
                    hl=lang,
                    start=start,
                )
        ) as resp:
            return await resp.text()


class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, " \
               f"title={self.title}, " \
               f"description={self.description})"


async def search(term, num_results=10, lang="ru", advanced=False):
    escaped_term = term.replace(' ', '+')
    start = 0
    while start < num_results:
        resp = await get_response_text(escaped_term,
                                       num_results - start,
                                       lang,
                                       start)

        soup = BeautifulSoup(resp, 'html.parser')
        result_block = soup.find_all('div', attrs={'class': 'g'})
        for result in result_block[: num_results - start]:
            link = result.find('a', href=True)
            title = result.find('h3')
            description_box = result.find('div',
                                          {'style': '-webkit-line-clamp:2'})
            if description_box:
                description = description_box.find('span')
                if link and title and description:
                    start += 1
                    if advanced:
                        yield SearchResult(link['href'], title.text,
                                           description.text)
                    else:
                        yield link['href']


async def get_links(term, num_results=10, lang="ru"):
    return [link async for link in search(term, num_results, lang)]
