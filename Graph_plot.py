# Импорт полезной фигни
import pandas as pd

# Зарузка данных

filepath = "Y:/!РАБОТА/ИнфоТеКС/Квантел/logs example/optical/1/optical_log.csv"
input_data = pd.read_csv(filepath, delimiter=';')
print(input_data)

# print(input_data)

# *** Отрисовка графиков
