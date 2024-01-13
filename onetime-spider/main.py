import spider
import client
from pydantic import BaseModel, Field, AnyUrl
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse


app = FastAPI(
    title="One-time spider",
    description="Сервис по единоразовому парсингу объектов страницы",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SpiderInput(BaseModel):
    """Схема данных для вызова метода сбора данных"""

    url: AnyUrl = Field(description="Ссылка на целевой ресурс", default=AnyUrl("https://quotes.toscrape.com/"))
    target: dict[str, str] = Field(
        description="Объект, который нужно собрать",
        default={
            "quote": '//div[@class="quote"]/span[@class="text"]/text()',
            "author": '//div[@class="quote"]//small[@class="author"]/text()',
        },
    )
    selectors_type: spider.SelectorsType = Field(
        description="Вид селектора, который используется в объекте",
        default=spider.SelectorsType.xpath,
    )


class SpiderOutput(BaseModel):
    """Схема данных для ответа по сбору данных"""

    result_data: list[dict] | dict = Field(description="Список собранных объектов (либо объект)")
    is_unpacked: bool = Field(description="Получилось ли превратить множество результатов в множество объектов?")


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/healthz", status_code=status.HTTP_200_OK, include_in_schema=False)
async def health_check() -> dict[str, int]:
    return {"status": status.HTTP_200_OK}


@app.post("/spider", tags=["spider"])
async def parse_target(spider_input: SpiderInput) -> SpiderOutput:
    page_text = await client.fetch_page(url=str(spider_input.url))
    one_time_spider = spider.OneTimeSpider(
        target=spider_input.target,
        page_content=page_text,
        selectors_type=spider_input.selectors_type,
    )
    return SpiderOutput(result_data=one_time_spider.results, is_unpacked=one_time_spider.is_unzipped)
