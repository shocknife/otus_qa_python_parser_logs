import json
import re
from collections import defaultdict
from datetime import datetime
import os

# Шаблон для парсинга строки лога
LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+) - (?P<user>\S+|-) \[(?P<date>.*?)\] "(?P<request>.*?)" (?P<status>\d{3}) (?P<size>\S+|-) "(?P<referer>.*?)" "(?P<user_agent>.*?)" (?P<duration>\d+|-)'
)

# HTTP-методы, которые будем отслеживать
HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]


class LogParser:
    def __init__(self, path):
        self.path = path  # Путь к файлу или директории

    def parse_log_line(self, line):
        """
        Парсит строку лога с помощью регулярного выражения.
        Возвращает словарь с данными, если строка соответствует шаблону.
        """
        match = LOG_PATTERN.match(line)
        if match:
            return match.groupdict()
        else:
            print(
                f"Skipped line: {line.strip()}"
            )  # Логируем строки, которые не соответствуют паттерну
        return None

    def analyze_log_file(self):
        """
        Анализирует лог-файл, подсчитывает количество запросов по методам,
        топ 3 IP адреса и топ 3 самых долгих запросов.
        """
        method_count = defaultdict(int)
        total_requests = 0
        ip_count = defaultdict(int)
        longest_requests = []

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if not line:  # Пропускаем пустые строки
                        continue

                    data = self.parse_log_line(line)
                    if data:
                        method = data["request"].split()[0]  # Извлекаем метод запроса
                        ip = data["ip"]  # IP-адрес
                        duration = data["duration"]  # Длительность запроса
                        size = data["size"]  # Размер ответа
                        date = data["date"]  # Дата запроса
                        url = data["request"].split()[1]  # URL запроса

                        # Если размер или длительность запроса недоступны, заменяем на 0
                        duration = int(duration) if duration != "-" else 0
                        size = int(size) if size != "-" else 0

                        # Подсчет общего числа запросов
                        total_requests += 1
                        method_count[method] += (
                            1  # Подсчитываем количество запросов по методу
                        )
                        ip_count[ip] += 1  # Подсчитываем количество запросов по IP

                        # Добавляем самые долгие запросы в список
                        longest_requests.append(
                            {
                                "ip": ip,
                                "date": date,
                                "method": method,
                                "url": url,
                                "duration": duration,
                            }
                        )
        except PermissionError as e:
            print(f"Ошибка доступа к файлу: {e}")
            return None
        except Exception as e:
            print(f"Ошибка при обработке файла: {e}")
            return None

        if not longest_requests:
            print(
                "Файл не содержит валидных данных или не удалось найти долгие запросы."
            )
            return None

        # Сортируем по длительности и выбираем топ 3 самых долгих запросов
        longest_requests.sort(key=lambda x: x["duration"], reverse=True)
        top_longest = longest_requests[:3]

        # Сортируем и выбираем топ 3 IP адреса с наибольшим количеством запросов
        top_ips = sorted(ip_count.items(), key=lambda x: x[1], reverse=True)[:3]

        # Формируем итоговую статистику
        stat = {
            "file": self.path,
            "top_ips": dict(top_ips),
            "top_longest": top_longest,
            "total_stat": dict(method_count),
            "total_requests": total_requests,
        }

        return stat

    def analyze_logs_in_directory(self):
        """
        Функция для анализа всех логов в указанной директории.
        """
        all_stats = []
        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = os.path.join(os.getcwd(), "statistics", current_date)

        # Создаем папку с именем текущей даты, если её нет
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file.endswith(".log"):  # обрабатываем только файлы .log
                    file_path = os.path.join(root, file)
                    print(f"Обрабатываем файл: {file_path}")
                    parser = LogParser(
                        file_path
                    )  # Для каждого файла создаем новый экземпляр
                    stat = parser.analyze_log_file()  # Получаем статистику для файла

                    if stat:
                        all_stats.append(stat)

                        # Сохранение статистики в JSON-файл в папку с текущей датой
                        output_json_path = os.path.join(
                            output_dir, f"{file}_stats.json"
                        )
                        with open(output_json_path, "w", encoding="utf-8") as json_file:
                            json.dump(stat, json_file, indent=4, ensure_ascii=False)

        if not all_stats:
            print("Не удалось обработать логи в директории или все файлы пустые.")
            return None

        return all_stats
