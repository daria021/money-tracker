from enum import Enum

import plotly.express as px
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import InlineKeyboardButton

from config import config
from keyboards.utils import chunk
from wastes.WastesRepo import WastesRepo


async def statistics(month: int, user_id: int, session: AsyncSession):
    stats_one_month = await WastesRepo.waste_one_month(user_id=user_id, month=month, session=session)
    sum_money = []
    kind = []
    for item in stats_one_month:
        kind.append(item.category.title)
        sum_money.append(item.amount)

    fig = px.pie(values=sum_money, names=kind)
    fig.write_image(f"{config.graphs_dir}/{user_id}.png")
    graph = f"{config.graphs_dir}/{user_id}.png"

    month_name = get_name_by_key(Monthes, month)
    message = f'Общая сумма за {month_name} - {sum(sum_money)}'
    return graph, message


def get_name_by_key(cls, value):
    for month in cls:
        if month.value == value:
            return month.name
    return None


class Monthes(Enum):
    January = 1
    February = 2
    March = 3
    April = 4
    May = 5
    June = 6
    July = 7
    August = 8
    September = 9
    October = 10
    November = 11
    December = 12


kinds_month = chunk([InlineKeyboardButton(name.name, callback_data=str(name.value)) for name in Monthes])
