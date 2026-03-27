import random

class TicketDistributor:
    @staticmethod
    def distribute(students: list | tuple, tickets_amount: int) -> dict[str: list[int]]:
        '''
        Распределяет билеты между студентами.

        Args:
            students: список студентов (строки).
            tickets_amount: общее количество билетов.

        Returns:
            Словарь {студент: [номера_билетов]}.
        '''
        # Проверки
        if not students:
            return {}
        if tickets_amount <= 0:
            return {student: [] for student in students}

        # Преобразуем в список, если передан numpy array
        students_list = list(students)

        n = len(students_list)
        base = tickets_amount // n          # базовое количество билетов для каждого
        extra = tickets_amount % n          # сколько студентов получат +1 билет

        # Выбираем студентов, которые получат дополнительный билет
        extra_students = random.sample(students_list, extra) if extra > 0 else []
        # Генерируем все номера билетов и перемешиваем их
        all_tickets = list(range(1, tickets_amount + 1))
        random.shuffle(all_tickets)

        # Инициализируем словарь
        distribution = {student: [] for student in students_list}

        # Раздаём билеты
        idx = 0  # текущий индекс в списке билетов
        for student in students_list:
            # Каждому студенту даём base билетов
            for _ in range(base):
                distribution[student].append(all_tickets[idx])
                idx += 1
            # Если студент в списке extra, даём ещё один билет
            if student in extra_students:
                distribution[student].append(all_tickets[idx])
                idx += 1

        # Проверка: idx должен быть равен tickets_amount
        return distribution


