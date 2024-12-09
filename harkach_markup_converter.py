# harkach_markup_converter.py
import re
import logging

logger = logging.getLogger(__name__)

class HarkachMarkupConverter:
    def __init__(self):
        pass

    def replace_underline_span(self, input_str: str) -> str:
        # Regex для поиска <span class="u">...</span>
        regex = re.compile(r'<span class="u">(.*?)</span>', flags=re.DOTALL)
        result = input_str
        while True:
            match = regex.search(result)
            if not match:
                break
            to_replace = match.group(1)
            # Заменяем найденный фрагмент на <u>...</u>
            result = result[:match.start()] + f"<u>{to_replace}</u>" + result[match.end():]
        return result

    def convert_to_tg_html(self, input_str: str) -> str:
        """
        Преобразует разметку Харкача в формат, понятный Telegram (HTML parse_mode).
        - <span class="u"> -> <u>
        - <a href="/"> -> <a href="https://2ch.hk/
        - &quot; -> "
        - class="spoiler" -> class="tg-spoiler"
        - <br> -> двойной перевод строки (для корректного отображения в Telegram)
        """
        result = self.replace_underline_span(input_str)
        result = (result
                  .replace('<a href="/', '<a href="https://2ch.hk/')
                  .replace('&quot;', '"')
                  .replace('class="spoiler"', 'class="tg-spoiler"')
                  .replace('<br>', '\n\n'))
        return result

    def replace_underline_span_html(self, input_str: str) -> str:
        regex = re.compile(r'<span class="u">(.*?)</span>', flags=re.DOTALL)
        result = input_str
        while True:
            match = regex.search(result)
            if not match:
                break
            to_replace = match.group(1)
            result = result[:match.start()] + f"<u>{to_replace}</u>" + result[match.end():]
        return result

    def convert_to_html(self, input_str: str) -> str:
        """
        Аналог метода convertToHtml из вашего Java кода:
        - <span class="u"> -> <u>
        - <a href="/"> -> <a href="https://2ch.hk/
        - &quot; -> "
        - <br> -> <br />
        """
        result = self.replace_underline_span_html(input_str)
        result = (result
                  .replace('<a href="/', '<a href="https://2ch.hk/')
                  .replace('&quot;', '"')
                  .replace('<br>', '<br />'))
        return result
