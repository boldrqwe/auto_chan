# harkach_markup_converter.py
import re
import logging

logger = logging.getLogger(__name__)

class HarkachMarkupConverter:
    """
    Класс для преобразования разметки Харкача в HTML-разметку, поддерживаемую Telegram.
    """
    def __init__(self):
        # Можно добавить настройки, если понадобится
        pass

    def replace_underline_span(self, input_str: str) -> str:
        # Регулярное выражение для поиска <span class="u">...</span>
        regex = re.compile(r'<span class="u">(.*?)</span>', flags=re.DOTALL)
        result = input_str
        while True:
            matcher = regex.search(result)
            if not matcher:
                break
            to_replace = matcher.group(1)
            # Заменяем найденный фрагмент на <u>...</u>
            result = result[:matcher.start()] + f"<u>{to_replace}</u>" + result[matcher.end():]
        return result

    def convert_to_tg_html(self, input_str: str) -> str:
        """
        Преобразует HTML-разметку из 2ch в такую, которую корректно отобразит Telegram,
        используя parse_mode='HTML'.
        """
        # Сначала заменяем underline span
        result = self.replace_underline_span(input_str)
        # Заменяем ссылки, кавычки, спойлеры и переносы строк
        result = (result
                  .replace('<a href="/', '<a href="https://2ch.hk/')
                  .replace('&quot;', '"')
                  .replace('class="spoiler"', 'class="tg-spoiler"')
                  .replace('<br>', '\n\n'))
        logger.debug("Преобразованный caption: %s", result)
        return result
