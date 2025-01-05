class LogAnalyzer:
    @staticmethod
    def print_stats(stats):
        """
        Функция для печати статистики в терминал.
        """
        for stat in stats:
            print(f"\nСтатистика для файла: {stat['file']}")
            print(f"Общее количество запросов: {stat['total_requests']}")
            print("Количество запросов по HTTP-методам:")
            for method, count in stat["total_stat"].items():
                print(f"  {method}: {count}")

            print("\nТоп 3 IP-адресов:")
            for ip, count in stat["top_ips"].items():
                print(f"  {ip}: {count}")

            print("\nТоп 3 самых долгих запросов:")
            for req in stat["top_longest"]:
                print(
                    f"  Метод: {req['method']}, URL: {req['url']}, IP: {req['ip']}, "
                    f"Длительность: {req['duration']}ms, Дата и время: {req['date']}"
                )
