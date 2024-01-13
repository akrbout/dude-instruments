from aiohttp import ClientSession
from random_header_generator import HeaderGenerator


def generate_headers() -> dict:
    generator = HeaderGenerator(user_agents='scrape')
    return generator()


async def fetch_page(url: str) -> str:
    headers = generate_headers()
    async with ClientSession(headers=headers) as session:
        response = await session.get(url=url)
        return await response.text()
