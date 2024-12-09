import requests

class TwoCHApiClient:
    def __init__(self, base_url="https://2ch.hk"):
        self.base_url = base_url.rstrip('/')

    def get_boards(self):
        """
        Получение списка досок и их настроек
        Метод: GET /api/mobile/v2/boards
        """
        url = f"{self.base_url}/api/mobile/v2/boards"
        r = requests.get(url)
        r.raise_for_status()
        return r.json()  # Возвращает JSON с данными о досках

    def get_thread_posts_after(self, board: str, thread_id: int, post_num: int):
        """
        Получение постов в треде >= указанного поста
        Метод: GET /api/mobile/v2/after/{board}/{thread}/{num}
        """
        url = f"{self.base_url}/api/mobile/v2/after/{board}/{thread_id}/{post_num}"
        r = requests.get(url)
        r.raise_for_status()
        return r.json()

    def get_thread_info(self, board: str, thread_id: int):
        """
        Получение информации о треде
        Метод: GET /api/mobile/v2/info/{board}/{thread}
        """
        url = f"{self.base_url}/api/mobile/v2/info/{board}/{thread_id}"
        r = requests.get(url)
        r.raise_for_status()
        return r.json()

    def get_post(self, board: str, post_num: int):
        """
        Получение информации о посте
        Метод: GET /api/mobile/v2/post/{board}/{num}
        """
        url = f"{self.base_url}/api/mobile/v2/post/{board}/{post_num}"
        r = requests.get(url)
        r.raise_for_status()
        return r.json()

    def get_captcha_id(self, board: str = None, thread_id: int = None):
        """
        Получение ID для emoji капчи
        Метод: GET /api/captcha/emoji/id
        Параметры: board, thread (опционально)
        """
        url = f"{self.base_url}/api/captcha/emoji/id"
        params = {}
        if board:
            params['board'] = board
        if thread_id:
            params['thread'] = thread_id
        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json()

    def show_emoji_captcha(self, captcha_id: str):
        """
        Получение состояния emoji капчи
        Метод: GET /api/captcha/emoji/show?id={captcha_id}
        """
        url = f"{self.base_url}/api/captcha/emoji/show"
        params = {'id': captcha_id}
        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json()

    def click_emoji_captcha(self, captchaTokenID: str, emojiNumber: int):
        """
        Клик на emoji клавиатуре
        Метод: POST /api/captcha/emoji/click
        """
        url = f"{self.base_url}/api/captcha/emoji/click"
        payload = {
            "captchaTokenID": captchaTokenID,
            "emojiNumber": emojiNumber
        }
        r = requests.post(url, json=payload)
        r.raise_for_status()
        return r.json()

    def get_app_id(self, public_key: str, board: str = None, thread_id: int = None):
        """
        Получение app_response_id для отправки поста
        Метод: GET /api/captcha/app/id/{public_key}
        """
        url = f"{self.base_url}/api/captcha/app/id/{public_key}"
        params = {}
        if board:
            params['board'] = board
        if thread_id:
            params['thread'] = thread_id
        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json()

    # Аналогично можно добавить методы для /user/posting, /user/report, /user/passlogin, /api/like, /api/dislike
    # В них потребуется отправлять POST запросы с multipart/form-data (например, для /user/posting).
    # Ниже пример создания поста (упрощённый):

    def create_post(self, board: str, captcha_type: str, comment: str,
                    thread_id: int = None, files: list = None,
                    name: str = None, email: str = None, subject: str = None):
        """
        Создание нового поста или треда
        Метод: POST /user/posting

        Параметры для body: multipart/form-data
        """
        url = f"{self.base_url}/user/posting"
        data = {
            "captcha_type": captcha_type,
            "board": board,
            "comment": comment
        }
        if thread_id:
            data["thread"] = str(thread_id)
        if name:
            data["name"] = name
        if email:
            data["email"] = email
        if subject:
            data["subject"] = subject

        files_payload = []
        if files:
            # files - список путей к файлам
            # Пример: files = ["image.jpg"]
            # Мы должны прикрепить их в формате files[] = open('image.jpg', 'rb')
            for f in files:
                files_payload.append(('file[]', (f, open(f, 'rb'))))

        r = requests.post(url, data=data, files=files_payload if files else None)
        r.raise_for_status()
        return r.json()
