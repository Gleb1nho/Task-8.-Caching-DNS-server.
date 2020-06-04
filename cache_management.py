import pickle
from interface import LineDrawer, Colors
import datetime


class Packet:
    def __init__(self, resource_record, create_time):
        self.resource_record = resource_record
        self.create_time = create_time


class CacheManagementUnit:
    colors = Colors()
    line = f'{colors.BOLD}{LineDrawer().draw_horisontal_line()}{colors.ENDC}'

    def __init__(self):
        self.database = self.load_cache()

    def load_cache(self):
        try:
            with open('dns.cache', 'rb') as f:
                database = pickle.load(f)
            print(f'{self.colors.OKGREEN}Кэш загружен{self.colors.ENDC}')
        except Exception as e:
            print(f'{self.colors.FAIL}Возникла ошибка при загрузке кэш-файла dns.cache: {e}{self.colors.ENDC}')
            return
        return database

    def save_cache(self, database):
        try:
            with open('dns.cache', 'wb') as f:
                pickle.dump(database, f)
            print(f'{self.line}\n{self.colors.OKGREEN}Закэшировано{self.colors.ENDC}\n{self.line}')
        except Exception as e:
            print(f'{self.line}\n{self.colors.FAIL}Возникла ошибка при сохранении:{e}{self.colors.ENDC}\n{self.line}')

    def delete_old_records(self):
        delta = 0
        for key, value in self.database.items():
            last_length = len(value)
            self.database[key] = set(packet for packet in value if not datetime.datetime.now() - packet.create_time > datetime.timedelta(seconds=packet.resource_record.ttl))
            delta += last_length - len(self.database[key])
        if delta > 0:
            print(f'В {datetime.datetime.now()} удалено(а) {self.colors.BOLD}{delta}{self.colors.ENDC} старых(ая) ресурсных(ая) записей(ь)')
