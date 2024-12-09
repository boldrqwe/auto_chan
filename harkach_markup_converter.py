import re
import logging

logger = logging.getLogger(__name__)

class HarkachMarkupConverter:
    def __init__(self):
        pass

    def replace_underline_span(self, input_str: str) -> str:
        # Найти <span class="u">...</span> и заменить на <u>...</u>
        regex = re.compile(r'<span class="u">(.*?)</span>', flags=re.DOTALL)
        result = input_str
        while True:
            match = regex.search(result)
            if not match:
                break
            to_replace = match.group(1)
            result = result[:match.start()] + f"<u>{to_replace}</u>" + result[match.end():]
        return result

    def replace_spoiler_span(self, input_str: str) -> str:
        # Найти <span class="spoiler">...</span> и заменить на <spoiler>...</spoiler>
        # Предполагается, что спойлер всегда обёрнут в span class="spoiler"
        # Если встречается <span class="spoiler">...content...</span>
        spoiler_regex = re.compile(r'<span class="spoiler">(.*?)</span>', flags=re.DOTALL)
        result = input_str
        while True:
            match = spoiler_regex.search(result)
            if not match:
                break
            to_replace = match.group(1)
            # Заменяем на <spoiler>...content...</spoiler>
            result = result[:match.start()] + f"<spoiler>{to_replace}</spoiler>" + result[match.end():]
        return result

    def convert_to_tg_html(self, input_str: str) -> str:
        result = self.replace_underline_span(input_str)
        result = self.replace_spoiler_span(result)

        # Заменяем <em> на <i> и <strong> на <b>
        result = result.replace('<em>', '<i>').replace('</em>', '</i>')
        result = result.replace('<strong>', '<b>').replace('</strong>', '</b>')

        result = (result
                  .replace('<a href="/', '<a href="https://2ch.hk/')
                  .replace('&quot;', '"')
                  .replace('class="spoiler"', '')  # если где-то осталось
                  .replace('<br>', '\n'))

        # Также можно убирать target и rel из ссылок, если они есть:
        # Например, с помощью регулярок удалить target="_blank" и rel="...":
        result = re.sub(r'target="_blank"', '', result)
        result = re.sub(r'rel="[^"]*"', '', result)

        return result

    def replace_underline_span_html(self, input_str: str) -> str:
        # Аналогично для HTML без Telegram специфики
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
        Аналог метода convertToHtml:
        - <span class="u"> -> <u>
        - <a href="/"> -> <a href="https://2ch.hk/
        - &quot; -> "
        - <br> -> <br />
        """
        result = self.replace_underline_span_html(input_str)
        # Для обычного HTML оставляем <br /> в качестве самозакрывающегося тега
        result = (result
                  .replace('<a href="/', '<a href="https://2ch.hk/')
                  .replace('&quot;', '"')
                  .replace('<br>', '<br />'))
        return result
