import requests
from loader import bot
from typing import List, Union, Dict, Any

url = "https://api.kinopoisk.dev/v1.4/movie"
API_KEY = "T56JKAM-T5544FG-K3RGQHF-5DHRXXD"


def get_movies(genre: str, quan: int, rating: str, sort_type: str) -> Union[List[Dict[str, Any]], str]:
    """
    Получает список фильмов из API Кинопоиска по заданным критериям.

    Параметры:
    :param genre: Жанр фильмов для поиска.
    :param quan: Количество фильмов для получения.
    :param rating: Критерий рейтинга для сортировки: «1» по возрастанию, в противном случае по убыванию.
    :param sort_type: Тип применяемой сортировки, хотя он переопределяется рейтингом.

    :return:
    Union[List[Dict[str, Any]], str]: список словарей, содержащих сведения о фильме в случае успешного запроса,
    в противном случае строка сообщения об ошибке.

    """
    headers: Dict[str, str] = {
        "accept": "application/json",
        "X-API-KEY": API_KEY
    }

    sort_type = '1' if rating == '1' else '-1'

    params: Dict[str, Union[int, str, List[str]]] = {
        "limit": int(quan),
        'genres.name': genre,
        "sortField": "rating.kp",
        "sortType": sort_type,
        "selectFields": ['id', 'name', 'type', 'year', 'rating', 'genres']
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json().get("docs", [])
    else:
        return f"Не удалось выполнить поиск: {response.status_code} Client Error: {response.text}"


def format_result(movies: List[Dict[str, Any]]) -> Union[str, None]:
    """
    Форматирует список фильмов в удобочитаемую строку.

    :param movies: (List[Dict[str, Any]]): список словарей, содержащих сведения о фильмах.

    :return: Union[str, None]: форматированное строковое представление списка фильмов или None, если список пуст.

    """
    if not movies:
        return None

    result: str = ""
    for index, movie in enumerate(movies):
        result += f"{index + 1}. {movie['name']} ({movie.get('year', 'Неизвестно')}) - Рейтинг: {movie.get('rating', 'Неизвестно')}\n"

    return result
