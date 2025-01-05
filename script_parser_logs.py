import os
import json
from datetime import datetime
from pages.log_parser import LogParser
from pages.log_analyzer import LogAnalyzer


def main():
    # Запрос пути к файлу или директории у пользователя
    input_path = input("Введите путь к файлу или директории с логами: ").strip()

    # Обработка файла или директории
    if os.path.isfile(input_path):
        # Если передан файл, обрабатываем только его
        print(f"Обрабатываем файл: {input_path}")
        parser = LogParser(input_path)  # Создаем объект LogParser с путем
        stats = parser.analyze_log_file()  # Вызываем метод для анализа одного файла

        if stats:  # Проверка, что данные не None
            LogAnalyzer.print_stats([stats])

            # Сохранение статистики в JSON-файл в папку с текущей датой
            output_dir = os.path.join(
                os.getcwd(), "statistics", datetime.now().strftime("%Y-%m-%d")
            )
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            output_json_path = os.path.join(
                output_dir, f"{os.path.basename(input_path)}_stats.json"
            )
            with open(output_json_path, "w", encoding="utf-8") as json_file:
                json.dump(stats, json_file, indent=4, ensure_ascii=False)
        else:
            print("Не удалось обработать файл или файл пустой.")

    elif os.path.isdir(input_path):
        # Если передан каталог, обрабатываем все лог-файлы в нем
        print(f"Обрабатываем логи в директории: {input_path}")
        parser = LogParser(input_path)  # Создаем объект LogParser с путем к директории
        stats = (
            parser.analyze_logs_in_directory()
        )  # Вызываем метод для анализа всех логов в директории

        if stats:  # Проверка, что данные не None
            LogAnalyzer.print_stats(stats)
        else:
            print("Не удалось обработать логи в директории.")

    else:
        print(
            "Ошибка: указанный путь не существует или не является файлом/директорией!"
        )


if __name__ == "__main__":
    main()
