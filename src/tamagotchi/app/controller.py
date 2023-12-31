from datetime import datetime as dt
from fractions import Fraction as frac
from json import dumps as jdumps, loads as jloads
from pathlib import Path
from src.tamagotchi.model import model
from data import data


class App:
    """
    Представляет метод для провеки файла с данными существа. И является хранителем существа восстановленного
    из файла.
    """
    def __init__(self):
        self.creature: model.Creature = LoadCreature.load()

    @staticmethod
    def is_live() -> bool:
        """Проверяет наличие файла с данными существа"""
        return LoadCreature.default_path.is_file()


class LoadCreature:
    """Представляет методы для сохранения существа в файл и загрузку существа из файла."""
    default_path: str | Path = data.creature_save
    game_days_to_real_hours: frac = frac(*data.days_hours)

    @classmethod
    def save(cls, creature: model.Creature) -> None:
        """Сщхраняет данные существа в файл."""
        data_save = {
            'timestamp': dt.now().timestamp(),
            'kind': creature.kind.name,
            'name': creature.name,
            'age': creature.age,
            'maturity': creature.mature.value,
            'params': creature.history[-1].__dict__
        }
        data_save = jdumps(data_save, ensure_ascii=False)
        cls.default_path.write_text(data_save, encoding='utf-8')

    @classmethod
    def load(cls) -> model.Creature:
        """Загружает существо из файла."""
        data_save = cls.default_path.read_text(encoding='utf-8')
        data_save = jloads(data_save)
        diff_hours = (dt.now().timestamp() - data_save['timestamp']) / 3600

        kind = None
        for elem in LoadKinds(*LoadKinds.generate()):
            if elem.name == data_save['kind']:
                kind = elem

        creature = model.Creature(kind, data_save['name'])
        creature.age = data_save['age']
        creature.mature = model.Maturity(data_save['maturity'])
        for k, v in data_save['params'].items():
            for elem in creature.params.keys():
                if elem.__name__ == k:
                    creature.params[elem].value = v
        return cls.__params_evolution(creature, diff_hours)

    # вариант с загрузкой питомца через model.State объект
    # @classmethod
    # def load(cls) -> model.Creature:
    #     data = cls.default_path.read_text(encoding='utf-8')
    #     data = jloads(data)
    #     kind = None
    #     for elem in LoadKinds(*LoadKinds.generate()):
    #         if elem.name == data['kind']:
    #             kind = elem
    #
    #     state = model.State(data['age'])
    #     for param, val in data['params'].items():
    #         if param != 'age':
    #             setattr(state, param, val)
    #
    #     state = cls.__params_evolution(state)
    #     creature = model.Creature(kind, data['name'])
    #     creature.age = state.age
    #     # доработать возможное изменение model.Maturity
    #     creature.mature = model.Maturity(data['maturity'])
    #     for k, v in state.__dict__.items():
    #         for elem in creature.params.keys():
    #             if elem.__name__ == k:
    #                 creature.params[elem].value = v
    #     return creature

    @classmethod
    def __params_evolution(cls, saved_creature: model.Creature, hours: float = 0) -> model.Creature:
        """Пересчитывает параметры существа в соответствии с мат.моделью имитации жизни при закрытом приложении (ТЗ п.3в)."""
        # один игровой день при закрытом приложении равен 2 часам реального времени
        game_day = hours * cls.game_days_to_real_hours
        flag = True
        while flag:
            list_bool: list = []
            for action in saved_creature.creature_action:
                # перевод таймера в часы
                timer_hours: float = round(action.timer / 60, 2)
                if timer_hours < game_day:
                    list_bool.append(True)
                    action.action()
                    game_day -= timer_hours
                    # saved_creature.age += timer_hours
                    saved_creature.add_creature_age(int(timer_hours))
                    if saved_creature.age > saved_creature.kind[saved_creature.mature].days:
                        # без проверки диапазона
                        saved_creature._grow_up()
                else:
                    list_bool.append(False)
            flag = any(list_bool)
        return saved_creature


class MainMenu:
    """Представляет класс с инициализацией игры (первый запуск)."""
    # метод не задействован
    @staticmethod
    def start():
        """Запускает GUI с фреймом главного меню."""

    @staticmethod
    def choose_kind(chosen_kind: model.Kind) -> model.Creature:
        # надо передать имя питомца
        """Создаёт питомца на основе выбранного пользователем вида."""
        return model.Creature(chosen_kind, data.default_name)


class LoadKinds(list):
    """Представляет список возможных видов существ."""
    def __init__(self, *kinds: model.Kind):
        super().__init__(kinds)

    @classmethod
    def read_file(cls):
        """Считывает виды существ из файла."""
        pass

    @staticmethod
    def generate() -> tuple:
        """Импортирует и возвращает кортеж с видами существ из файла."""
        from src.tamagotchi.utils import cat_kind, dog_kind
        return cat_kind, dog_kind
