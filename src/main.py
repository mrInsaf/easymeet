from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from config import TG_BOT_TOKEN
import asyncio

bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_command(massage: types.Message):
    await massage.reply("Hi, my name is EasyMeet")


@dp.message_handler(commands=["add_trip"])
async def add_trip(massage: types.Message):
    markup_inline = types.InlineKeyboardMarkup()
    item_yes = types.InlineKeyboardButton(text="Да", callback_data='yes_remind')
    item_no = types.InlineKeyboardButton(text="Нет", callback_data='no_remind')
    markup_inline.add(item_yes, item_no)
    await bot.send_message(massage.from_user.id, "Хотите чтобы я предупредил вас за 5 минут до выхода?",
                           reply_markup=markup_inline)


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
