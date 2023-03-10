import os
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from dateutil.parser import parse
from aiogram.utils import executor
import asyncio
import logging
from geo_api import get_coordinates_by_address, get_data_by_coordinates
from db import db_add_group, db_create_user

FORMAT = '%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_command(massage: types.Message):
    db_create_user(massage.from_user.id, massage.from_user.username, massage.from_user.first_name,
                   massage.from_user.last_name)
    await massage.reply("Привет, я имя .\nПопробуй команду /help чтобы посмотреть на что я способен.")


@dp.message_handler(commands=["help"])
async def help_command(massage: types.Message):
    help_data = "TODO"
    await bot.send_message(massage.from_user.id, help_data)


@dp.message_handler(commands=["create_group"])
async def create_group(massage: types.Message):
    try:
        trip_data = massage.text.split()

        trip_date = parse(' '.join(trip_data[1:3]))

        trip_address = ' '.join(trip_data[3:])
        address_coordinates = get_coordinates_by_address(trip_address)
        if not address_coordinates:
            raise ValueError("Неправильный адрес")

        trip_id = db_add_group(trip_date, trip_address, address_coordinates)
        if not trip_id:
            raise RuntimeError("Не смог создать группу")

        await massage.reply(f"Создал группу.\nДата: {trip_date}.\nАдрес: {trip_address}\nID группы{trip_id}")
    except Exception as ex:
        logger.warning(ex)
        await massage.reply("Неправильный ввод")


@dp.callback_query_handler()
async def trip_callback(callback: types.CallbackQuery):
    await bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    if callback.data == "yes_remind":
        await asyncio.sleep(30)
        await bot.send_message(callback.from_user.id, "Пора выходить")
    await callback.answer("Удачи в дороге")


if __name__ == "__main__":
    executor.start_polling(dp)
