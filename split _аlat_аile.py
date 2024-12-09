import os
import pyperclip

# Укажите папку для сохранения разделённых файлов
output_dir = "."

# Убедитесь, что директория для вывода существует
os.makedirs(output_dir, exist_ok=True)

# Чтение данных из буфера обмена
clipboard_data = pyperclip.paste()

# Разделение данных по строкам
lines = clipboard_data.splitlines()

current_file = None
current_content = []

# Список файлов для исключения
excluded_files = ["harkach_markup_converter.py"]

for line in lines:
    # Проверка на начало нового файла
    if line.startswith("===") and line.endswith("==="):
        # Сохранение текущего файла, если есть
        if current_file and current_content:
            if current_file not in excluded_files:
                with open(os.path.join(output_dir, current_file), "w", encoding="utf-8") as out_file:
                    out_file.writelines(current_content)

        # Установка имени нового файла (без добавления ".py" к имени, если оно уже есть)
        current_file_name = line.strip("= ").replace(" ", "_").lower()
        if current_file_name.endswith(".py.py"):
            current_file = current_file_name[:-3]  # Удаление лишнего ".py"
        else:
            current_file = current_file_name if current_file_name.endswith(".py") else current_file_name + ".py"
        current_content = []  # Очистка содержимого для нового файла
    else:
        # Добавление строки в текущий файл
        current_content.append(line + "\n")

# Сохранение последнего файла
if current_file and current_content:
    if current_file not in excluded_files:
        with open(os.path.join(output_dir, current_file), "w", encoding="utf-8") as out_file:
            out_file.writelines(current_content)

print(f"Файлы успешно разделены и сохранены в папке '{output_dir}'")
