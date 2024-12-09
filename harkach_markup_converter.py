import re
import logging

logger = logging.getLogger(__name__)

class HarkachMarkupConverter:
    def __init__(self):
        pass

    def replace_underline_span(self, input_str: str) -> str:
        # <span class="u">...</span> -> <u>...</u>
        regex = re.compile(r'<span class="u">(.*?)</span>', flags=re.DOTALL)
        result = input_str
        # Заменяем все вхождения
        while True:
            match = regex.search(result)
            if not match:
                break
            content = match.group(1)
            replacement = f"<u>{content}</u>"
            result = result[:match.start()] + replacement + result[match.end():]
        return result

    def replace_unkfunc_span(self, input_str: str) -> str:
        # <span class="unkfunc">...</span> -> <i>...</i>
        regex = re.compile(r'<span class="unkfunc">(.*?)</span>', flags=re.DOTALL)
        result = input_str
        while True:
            match = regex.search(result)
            if not match:
                break
            content = match.group(1)
            replacement = f"<i>{content}</i>"
            result = result[:match.start()] + replacement + result[match.end():]
        return result

    def replace_spoiler_span(self, input_str: str) -> str:
        # Если хотите сделать <span class="spoiler">...</span> в <spoiler>...</spoiler>
        # Если нет, можно просто удалять class="spoiler" атрибут.
        # Пример: <span class="spoiler">...content...</span> -> <spoiler>...content...</spoiler>
        regex = re.compile(r'<span class="spoiler">(.*?)</span>', flags=re.DOTALL)
        result = input_str
        while True:
            match = regex.search(result)
            if not match:
                break
            content = match.group(1)
            replacement = f"<spoiler>{content}</spoiler>"
            result = result[:match.start()] + replacement + result[match.end():]
        return result

    def  convert_to_tg_html(self, input_str: str) -> str:
        result = self.replace_underline_span(input_str)
        result = self.replace_unkfunc_span(result)
        result = self.replace_spoiler_span(result)

        # Заменяем <em> на <i> и <strong> на <b>
        result = (result
                  .replace("<em>", "<i>").replace("</em>", "</i>")
                  .replace("<strong>", "<b>").replace("</strong>", "</b>"))

        # Заменяем ссылки, кавычки и переносы строк
        result = (result
                  .replace('<a href="/', '<a href="https://2ch.hk/')
                  .replace('&quot;', '"')
                  # Если осталось class="spoiler" или другой атрибут, удалим его:
                  # Можем просто вырезать все class="..."
                  # Но аккуратно: например, удалить только class="spoiler"
                  .replace('class="spoiler"', '')
                  .replace("<br>", "\n"))

        # Можно при желании удалить target и rel атрибуты из ссылок:
        result = re.sub(r'target="_blank"', '', result)
        result = re.sub(r'rel="[^"]*"', '', result)

        return result

    def replace_underline_span_html(self, input_str: str) -> str:
        # Аналог для HTML без telegram-specific преобразований
        regex = re.compile(r'<span class="u">(.*?)</span>', flags=re.DOTALL)
        result = input_str
        while True:
            match = regex.search(result)
            if not match:
                break
            content = match.group(1)
            replacement = f"<u>{content}</u>"
            result = result[:match.start()] + replacement + result[match.end():]
        return result

    def convert_to_html(self, input_str: str) -> str:
        result = self.replace_underline_span_html(input_str)
        result = (result
                  .replace('<a href="/', '<a href="https://2ch.hk/')
                  .replace('&quot;', '"')
                  .replace("<br>", "<br />"))
        return result
