import aiohttp
import base64
import os
import time

# Глобальные переменные для хранения токена и времени его окончания
access_token = None
token_expires_at = 0


async def get_access_token():
    """Функция для получения или обновления access_token для GigaChat API."""
    global access_token, token_expires_at

    # Проверяем, если токен уже существует и не истек
    if access_token and token_expires_at > time.time():
        return access_token

    client_id = os.getenv('GIGACHAT_CLIENT_ID')
    client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')

    if not client_id or not client_secret:
        raise ValueError("Необходимо указать GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET в .env файле.")

    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    # Создаем строку с авторизационными данными (Basic Auth)
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'Authorization': f'Basic {auth}'
    }

    data = 'scope=GIGACHAT_API_PERS'

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            if response.status == 200:
                result = await response.json()
                access_token = result['access_token']
                token_expires_in = 30 * 60  # 30 минут по умолчанию
                token_expires_at = time.time() + token_expires_in  # Обновляем время окончания токена
                return access_token
            else:
                raise Exception(f"Ошибка получения токена: {response.status} - {await response.text()}")


# Пример использования функции
if __name__ == "__main__":
    import asyncio

    access_token = asyncio.run(get_access_token())
    print(f"Access Token: {access_token}")
