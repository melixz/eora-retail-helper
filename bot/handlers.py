from aiogram import types
from aiogram.filters import Command
from bot.bot import router
from utils.gigachat_service import generate_answer
from data.database import fetch_context_from_db


# Обработчик команды /start
async def start_command(message: types.Message):
    await message.answer("Привет! Я могу помочь ответить на вопросы о возможностях для ритейлеров.")


# Обработчик текстовых вопросов
async def handle_question(message: types.Message):
    user_question = message.text
    context = await fetch_context_from_db(user_question)
    answer = await generate_answer(user_question, context)
    await message.answer(answer)


# Регистрируем обработчики команд и сообщений
router.message.register(start_command, Command(commands=['start']))
router.message.register(handle_question)
