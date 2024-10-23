from typing import List, Union
from telebot.types import Message
from db import RequestHistory
from loader import bot
from functions import get_movies, format_result
from telebot import types

ALLOWED_GENRES: List[str] = [
    "драма", "комедия", "мелодрама", "детектив", "фантастика",
    "ужасы", "триллер", "боевик", "приключения", "анимация",
    "документальный", "фэнтези", "аниме"
]


@bot.message_handler(commands=['hello'])
def send_hello(message: Message) -> None:
    bot.reply_to(message, f"Привет, {message.from_user.first_name} {message.from_user.last_name}")


@bot.message_handler(commands=['low', 'high'])
def genre_rating(message: Message) -> None:
    rating_filter: str = '1-4' if message.text == '/low' else '7-10'
    bot.send_message(message.chat.id, "Введите жанр")
    bot.register_next_step_handler(message, ask_quantity, rating_filter)


@bot.message_handler(commands=['custom'])
def custom_query(message: Message) -> None:
    bot.send_message(message.chat.id, "Введите свой запрос для получения фильмов (в формате 'жанр, количество'):")
    bot.register_next_step_handler(message, process_custom_query)


@bot.message_handler(commands=['history'])
def show_history(message: Message) -> None:
    user_id: int = message.from_user.id
    history_entries = RequestHistory.select().where(RequestHistory.user_id == user_id)

    if not history_entries:
        bot.send_message(message.chat.id, "История запросов пуста.")
    else:
        response = "История ваших запросов:\n" + "\n".join([entry.query for entry in history_entries])
        bot.send_message(message.chat.id, response)


def process_custom_query(message: Message) -> None:
    user_id: int = message.from_user.id
    input_text: str = message.text.lower().strip()

    try:
        genre, quantity_str = map(str.strip, input_text.split(','))
        quantity: int = int(quantity_str)
    except ValueError:
        bot.send_message(message.chat.id,
                         "Неправильный формат. Убедитесь, что вы используете формат 'жанр, количество'.")
        return

    if genre not in ALLOWED_GENRES or quantity <= 0:
        bot.send_message(message.chat.id,
                         f"Недопустимый ввод. Пожалуйста, введите жанр из списка: {', '.join(ALLOWED_GENRES)} и положительное количество фильмов.")
        return

    RequestHistory.create(user_id=user_id, query=f"{genre}, {quantity}")

    rating: int = 7
    sort_type: str = "1"
    bot.send_message(message.chat.id, f"Получаем {quantity} фильмов жанра '{genre}'...")
    movies = get_movies(genre, quantity, rating, sort_type)

    if isinstance(movies, str):
        bot.send_message(message.chat.id, movies)
    else:
        if not movies:
            bot.send_message(message.chat.id, "Не найдено фильмов для заданных параметров.")
            return
        result = format_result(movies)
        bot.send_message(message.chat.id, result)


def ask_quantity(message: Message, rating_filter: str) -> None:
    genre: str = message.text.lower()
    if genre not in ALLOWED_GENRES:
        bot.send_message(message.chat.id,
                         f"Недопустимый жанр. Пожалуйста, введите один из следующих жанров: {', '.join(ALLOWED_GENRES)}")
        bot.register_next_step_handler(message, ask_quantity, rating_filter)
        return
    bot.send_message(message.chat.id, f"Вы выбрали жанр: {genre}. Теперь введите количество фильмов:")
    bot.register_next_step_handler(message, quan_movies, genre, rating_filter)


def quan_movies(message: Message, genre: str, rating_filter: str) -> None:
    quan: str = message.text
    if not quan.isdigit() or int(quan) <= 0:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное количество фильмов (положительное число).")
        bot.register_next_step_handler(message, quan_movies, genre, rating_filter)
        return

    sort_type: str = "1" if rating_filter == '7-10' else "-1"
    rating: int = 7 if rating_filter == '7-10' else 1
    bot.send_message(message.chat.id, f"Получаем {quan} фильмов жанра '{genre}' с рейтингом {rating_filter}...")
    movies = get_movies(genre, int(quan), rating, sort_type)

    if isinstance(movies, str):
        bot.send_message(message.chat.id, movies)
    else:
        if not movies:
            bot.send_message(message.chat.id, "Не найдено фильмов для заданных параметров.")
            return
        result = format_result(movies)
        bot.send_message(message.chat.id, result)


@bot.message_handler(func=lambda message: True)
def echo_all(message: Message) -> None:
    bot.reply_to(message, message.text)
