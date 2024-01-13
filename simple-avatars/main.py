import random
import math
import hashlib
import base64
from io import BytesIO
from PIL import Image, ImageOps
from pydantic import BaseModel, Field
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="Avatar Generation Service",
    description="Сервис по генерации рандомных аватаров",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AvatarInput(BaseModel):
    """Входная схема микросервиса генерации аватара"""

    nickname: str = Field(
        description="Никнейм для генерации аватара",
        default="akrbout_example",
    )
    image_upscale_size: int = Field(
        description="Размер апскейла изображения в пикселях (т.к. исходное генерируется в размере 7x7)",
        default=500,
    )


class AvatarOutput(BaseModel):
    """Выходная схема микросервиса генерации аватара"""

    origin_nickname: str = Field(description="Никнейм, на основе которого шла генерация")
    image_base64: str = Field(description="Сгенерированное изображение в Base64 строке")


class GeneratorContainer(BaseModel):
    image_size: int = Field(default=7, description="Размер аватара в пикселях")
    background_color: tuple = Field(default=(250, 251, 253), description="Цвет фона аватара в пространстве RGB")

    @property
    def image_size_half(self) -> int:
        return int(math.ceil(self.image_size / 2))


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/healthz", status_code=status.HTTP_200_OK, include_in_schema=False)
async def health_check() -> dict[str, int]:
    return {"status": status.HTTP_200_OK}


@app.post("/avatar", tags=["generator"], name="Получить аватар на основе никнейма")
async def generate_avatar(avatar_input: AvatarInput) -> AvatarOutput:
    buffer = BytesIO()
    generator_container = GeneratorContainer()
    seed = hashlib.md5(avatar_input.nickname.encode("utf-8")).digest()
    random.seed(seed)
    foreground_color = random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)
    with Image.new("P", (generator_container.image_size, generator_container.image_size), 0) as img:
        img.putpalette(generator_container.background_color + foreground_color)
        px = img.load()
        for _ in range(random.randint(5, 12)):
            x = random.randrange(0, generator_container.image_size_half)
            y = random.randrange(0, generator_container.image_size)
            px[x, y] = 1
            px[-1 - x, y] = 1
        img = img.resize((generator_container.image_size * 2, generator_container.image_size * 2), Image.NEAREST)
        img = ImageOps.expand(img, 1, 0)
        img = img.resize((avatar_input.image_upscale_size, avatar_input.image_upscale_size), Image.BOX)
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue())
    return AvatarOutput(origin_nickname=avatar_input.nickname, image_base64=img_base64)
