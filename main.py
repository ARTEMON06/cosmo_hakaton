# импорт всех необходимых библиотек, функций, классов

import requests  # библиотека для получения данных
import sys  # библиотека для запуска окна приложения
from PyQt5 import QtWidgets  # библиотека для создания окна приложения
from assets.main_GUI import Ui_MainWindow  # библиотека для запуска окна приложения
import sqlite3 as sql  # библиотека для работы с базой данных SQLite3
import translators as ts  # библиотека для перевода текста на русский

data = []

with sql.connect('data.db') as conn:
    """
    Создание или открытие базы данных, подключение к ней и создание/открытие таблицы с названием "output"
    """
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS output(name TEXT, height INT, diameter INT, mass INT, fuel TEXT,"
                "description TEXT, wikipedia TEXT);")
    conn.commit()


def request_API(api: str):
    """
    Функция для получения информации с github, преобразования её и записи в список
    :param api: API для получения информации
    :return: список (str) необходимых преобразованных данных
    """
    r = requests.get(api).json()
    for item in r:
        fuel_text = f"{item['engines']['propellant_1']}, {item['engines']['propellant_2']}"
        trans_text_fuel = ts.google(fuel_text, from_language='en', to_language='ru')
        trans_desc = ts.google(item['description'], from_language='en', to_language='ru')
        local_data = [item['name'], item['height']['meters'], item['diameter']['meters'],
                      item['mass']['kg'], trans_text_fuel, trans_desc, item['wikipedia']]
        data.append(local_data)
    return data


if __name__ == '__main__':
    with sql.connect('data.db') as conn:
        """
        Запись данных в БД
        """
        API = 'https://api.spacexdata.com/v4/rockets'
        data = request_API(API)
        cur = conn.cursor()
        cur.execute("DELETE FROM output")
        for mass_of_items in data:
            cur.execute("INSERT INTO output VALUES(?, ?, ?, ?, ?, ?, ?);", mass_of_items)

    # Вызов окна приложения
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, data)
    MainWindow.show()
    sys.exit(app.exec_())
