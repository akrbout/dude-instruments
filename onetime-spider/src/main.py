import src.spider as spider
import src.client as client
from pydantic import BaseModel, Field, AnyUrl
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse


app = FastAPI(
    title="One-time spider",
    description="Сервис по единоразовому парсингу объектов страницы",
    version="1.1.0",
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
    target: dict = Field(
        description="Объект, который нужно собрать",
        default={
            "quote_item": {
                "_parent_object": "//div[@class='quote']",
                "quote": ["./span[@class='text']/text()", "string"],
                "author": [".//small[@class='author']/text()", "string"],
                "tags": ["./div[@class='tags']/a/text()", "array"],
            },
            "top_tags": ["//div[contains(@class, 'tags-box')]/span/a/text()", "array"],
        },
    )
    selectors_type: spider.SelectorsType = Field(
        description="Вид селектора, который используется в объекте",
        default=spider.SelectorsType.xpath,
    )


class SpiderOutput(BaseModel):
    """Схема данных для ответа по сбору данных"""

    result_data: list[dict] | dict = Field(description="Список собранных объектов (либо объект)")


class SpiderException(BaseModel):
    """Схема данных для ответа при исключении"""

    exception: str = Field(description="Текст исключения")


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/healthz", status_code=status.HTTP_200_OK, include_in_schema=False)
async def health_check() -> dict[str, int]:
    return {"status": status.HTTP_200_OK}


@app.post(
    "/crawl",
    tags=["spider"],
    description="""Метод позволяет собрать все совпадающие объекты, описанные в схеме. 
    Если требуется собрать несколько объектов одного формата, 
    то для такого объекта необходимо указание селектора '_parent_object'.""",
    name="crawl_page",
    response_model=SpiderOutput,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": SpiderException,
            "description": "Возвращает сообщение с ошибкой",
        },
        status.HTTP_200_OK: {
            "model": SpiderOutput,
            "description": "Возвращает скрауленные объекты",
        },
    },
)
async def parse_target(spider_input: SpiderInput) -> SpiderOutput | SpiderException:
    page_text = await client.fetch_page(url=str(spider_input.url))
    try:
        one_time_spider = spider.OneTimeSpider(
            target=spider_input.target,
            page_content=page_text,
            selectors_type=spider_input.selectors_type,
        )
        return SpiderOutput(result_data=one_time_spider.result)
    except Exception as ex:
        return SpiderException(exception=str(ex))
