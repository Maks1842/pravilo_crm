import random

from fastapi import APIRouter


# Роутер для приветствия
router_welcome = APIRouter(
    prefix="/v1/GetWelcomeText",
    tags=["Admin"]
)


@router_welcome.get("/")
async def get_welcome_text():

    result = random.choice(welcome_list)

    return result


welcome_list = [
    'Ты сегодня прекрасно выглядишь! ;))',
    'Сегодня лучший день для достижения мечты! ВПЕРЕД!!!',
    'Великолепного, прекрасного, плодотворного дня!!!',
    'УЛЫБНИСЬ %)%)',
    'Выигрывают те, у кого больше степеней свободы и вариантов. Мечтай, Думай, Совершай!!!',
    'Если мы не управляем своими целями, то ими управляет кто-то другой.',
    'Ты ЛУЧШАЯ(ий)!!!',
]