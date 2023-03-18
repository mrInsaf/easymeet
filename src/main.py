import os
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from dateutil.parser import parse
from aiogram.utils import executor
import asyncio
import logging
from geo_api import get_coordinates_by_address, get_data_by_coordinates
from db import db_add_group, db_create_user, check_user_in_group, user_exist, get_chat_id_by_username, \
    add_user_to_group, see_group_list
from weather import get_weather_by_coordinates

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
    await massage.reply("Привет, я EasyMeet.\nПопробуй команду /help чтобы посмотреть на что я способен.")


@dp.message_handler(commands=["help"])
async def help_command(massage: types.Message):
    help_data = "/create_group [дата] [время] [адрес] - создать группу поездки. Бот вернёт id группы\n" \
                "/change_group_date [дата] - изменить дату встречи\n" \
                "/change_group_time [время] - изменить время встречи\n" \
                "/change_group_address [адрес] - изменить адрес встречи\n" \
                "/add_user_to_group [id группы] [username] - добавить пользователя в группу\n" \
                "/delete_user_from_group [id группы] [username] - удалить пользователя из группы\n" \
                "/ask_to_join_group [id группы] - попросить присоединиться к группе\n" \
                "/leave_group [id группы] - покинуть группу\n" \
                "/get_group_list [id группы] - посмотреть участников группы\n" \
                "/add_departure [id группы] [адрес] - задать место отправления для пользователя в группе\n" \
                "/change_departure [id группы] [адрес] - измениить место отправления для пользователя в группе\n" \
                "/notice_me [id группы] [количество минут] - попросить бота напомнить о поездке за определённое количтво минут\n" \
                "/get_weather [адрес] - текущий прогноз погоды по адресу\n" \
                "/get_weather [id группы] - текущий прогноз погоды по адресу встречи\n"
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

        group_id = db_add_group(trip_date, trip_address, address_coordinates, massage.from_user.id)
        if group_id is None:
            raise RuntimeError("Не смог создать группу")

        # hide to easy test
        # add_user_to_group(group_id, massage.from_user.id)
        await massage.reply(f"Создал группу.\nДата: {trip_date}.\nАдрес: {trip_address}\nID группы: {group_id}")
    except Exception as ex:
        logger.warning(ex)
        await massage.reply("Неправильный ввод")


async def invite_user_to_join_group(group_id, my_username, invite_username):
    keyboard = types.InlineKeyboardMarkup()
    menu_1 = types.InlineKeyboardButton(text='Присоединиться', callback_data="user accept invite to group")
    menu_2 = types.InlineKeyboardButton(text='Отказаться', callback_data="user decline invite to group")
    keyboard.add(menu_1, menu_2)
    chat_id = get_chat_id_by_username(invite_username)
    await bot.send_message(chat_id, f"Пользователь {my_username} пригласил вас в группу {group_id}",
                           reply_markup=keyboard)


@dp.message_handler(commands=["add_user_to_group"])
async def user_to_group(massage: types.Message):
    trip_data = massage.text.split()
    try:
        group_id = int(trip_data[1])
        username = trip_data[2]
        if not user_exist(username):
            raise RuntimeError("User does not exist")
        if not check_user_in_group(group_id, username):
            await invite_user_to_join_group(group_id, massage.from_user.username, username)
        else:
            await bot.send_message(massage.from_user.id, "Пользователь уже в группе")
    except Exception as ex:
        logger.warning(ex)
        await massage.reply("Неправильный ввод")


@dp.message_handler(commands=["get_group_list"])
async def get_group_list(massage: types.Message):
    trip_data = massage.text.split()
    try:
        group_id = int(trip_data[1])
        group_list = see_group_list(group_id)
        if len(group_list):
            await massage.reply(f"Участники группы: {', '.join(group_list)}")
        else:
            await massage.reply("Группа пока пуста(")
    except Exception as ex:
        logger.warning(ex)
        await massage.reply("Неправильный ввод")


@dp.message_handler(commands=["get_weather"])
async def weather_by_address(massage: types.Message):
    trip_data = massage.text.split()
    try:
        trip_address = ' '.join(trip_data[1:])
        address_coordinates = get_coordinates_by_address(trip_address)
        if not address_coordinates:
            raise ValueError("Неправильный адрес")
        weather = get_weather_by_coordinates(address_coordinates)
        await bot.send_message(massage.from_user.id, weather)
    except Exception as ex:
        logger.warning(ex)
        await massage.reply("Ты что-то ввёл не так(")


@dp.callback_query_handler()
async def trip_callback(callback: types.CallbackQuery):
    await bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    if callback.data == "user accept invite to group":
        group_id = int(callback.message.text.split()[-1])
        invitor_username = get_chat_id_by_username(callback.message.text.split()[1])
        add_user_to_group(group_id, callback.from_user.id)
        await bot.send_message(callback.from_user.id, f"Вы присоединились у группе {group_id}!")
        await bot.send_message(invitor_username,
                               f"Пользователь {callback.from_user.username} присоединился к группе {group_id}")
    elif callback.data == "user decline invite to group":
        group_id = int(callback.message.text.split()[-1])
        invitor_username = get_chat_id_by_username(callback.message.text.split()[1])
        await bot.send_message(invitor_username,
                               f"Пользователь {callback.from_user.username} отказался присоединятся к группе {group_id}")


if __name__ == "__main__":
    executor.start_polling(dp)
