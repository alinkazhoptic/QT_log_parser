# Нечто для чтения лога Квантел и формирования массивов эволюции оптических параметров КРК

# Импорт полезной фигни
import re
import json
import csv
import easygui
import time

# /// Входные данные \\\

# Здесь надо записать интересующую дату, как в логе:
# print('\n Введите интересующую дату, как в log-файле, например, "Dec 20" ')
# Date_of_interest = input()


# *** Путь до файла лога ***
print('1. Select log file \n')
file_path = easygui.fileopenbox(filetypes = ['*.log', '*.log.*'])

# Год регистрации лога - ввод снаружи
print('\n Введите год регистрации log-файла, например, 2021 ')
year_value = input()

# ***********************************************************

# Тут должны быть используемые функции

# ***********************************************************

# Reading log-file of Quantel
logfile_obj = open(file_path, 'rt') #'rt' - открытие для чтения (r) текстового (t) файла
loglines = logfile_obj.readlines()
logfile_obj.close()
print(len(loglines), 'lines successfully read')

# ***********************************************************

#Запись всех линий (строк) с оптическим логом в один массив qkdmetriclines
qkdmetriclines = []
parse_phrase_sent = "qkdom"
num_of_req_str_sent = 0  # счетчик строк, содержащих parse_phrase_1

parse_phrase_received = "QK_GENERATION_LOG"
num_of_req_str_received = 0  # счетчик строк, содержащих parse_phrase_2

for line in loglines:
    if (line.find(parse_phrase_received) >= 0) :
        num_of_req_str_received = num_of_req_str_received + 1
        if line.find('"QBerr"') > 0:
            qkdmetriclines.append(line)
            # print(line) # просто вывод всех полезных строк лог-файла
        else:
             print('There is no QBER data for this series')

for line in loglines:
    if ( (line.find(parse_phrase_sent) >= 0) and (line.find('Metrics:') >= 0) ):
        num_of_req_str_sent = num_of_req_str_sent + 1
        if line.find('"QBerr"') > 0:
            if num_of_req_str_received == 0:
                qkdmetriclines.append(line)
        else:
            print('There is no QBER data for this series')

if (num_of_req_str_sent != num_of_req_str_received): # проверка равенства числа полученных УК логов с количеством отправленных
    print('The number of sent logs is not equal to the number of received logs')

if (qkdmetriclines != []):
    print('Parsing completed successfully!')
    if (num_of_req_str_sent == 0) :
        print ('Warning: There is no "' + parse_phrase_sent + '" in this log')
    if (num_of_req_str_received == 0) :
        print ('Warning: There is no "' + parse_phrase_received + '" in this log')
    # print(len(qkdmetriclines), 'series lines')

elif ( (num_of_req_str_sent == 0) & (num_of_req_str_received == 0) ):
    print('\nRecuired "' + parse_phrase_received + '" or "' + parse_phrase_received + '" does not exist in this log-file')
    print('Close after 10 seconds')
    time.sleep(10)
    raise SystemExit()


\
# *** Выделение временной метки из массива линий qkdmetriclines ***
time_array = []
date_array = []
timestamp_array = []

# k = 0
for st in qkdmetriclines:
    search_result_datestamp = re.search(r'(?P<month>\b\w{3}\b)\W+(?P<day>\d+)', st)
    search_result_timestamp = re.search(r'(?P<hours>\d\d):(?P<minutes>\d\d):(?P<seconds>\d\d)', st)
    # print(search_result_timestamp)
    month_value = search_result_datestamp.group('month')
    day_value = int( search_result_datestamp.group('day') )
    h_value = int( search_result_timestamp.group('hours') )
    m_value = int( search_result_timestamp.group('minutes') )
    s_value = int( search_result_timestamp.group('seconds') )

    seconds_total = s_value + 60 * m_value + 60 * 60 * h_value + 24 * 60 * 60 * day_value
    # print('Date: month - ', month_value, 'day - ', day_value )
    # print('Total time is', seconds_total, 'seconds')

    date_array.append( str(year_value) + '-' + str(month_value) + '-' + str(day_value) )
    timestamp_array.append( search_result_timestamp.group('hours') + ':' + search_result_timestamp.group('minutes') + ':' + search_result_timestamp.group('seconds') )
    time_array.append(seconds_total)
    # print('time [', k, ']:', time_array[k], 's')
    # k = k + 1

# Смещение массива времени для счета относительно запуска системы
time_start = time_array[0]
for i in range(len(time_array)):
    time_array[i] = time_array[i] - time_start
    # print('Relative time after start [', i, ']:', time_array[i], 's')
# print('\nlength of time array = ', len(time_array), '\n')

# **************************************************
# *** Выделение Alice ID

alice_id_array = []
print('IDs of QSS Points:')
if num_of_req_str_received > 0:
    for st in qkdmetriclines:
        search_result_idstamp = re.search(r'(?P<qk>QK_GENERATION_LOG).(?P<id>\w{10}).', st)
        print(search_result_idstamp.group('id'))       #Вывод ID Алис, с которыми делались ключи
        alice_id_value = search_result_idstamp.group('id')
        alice_id_array.append(alice_id_value)
num_of_ids = len(alice_id_array)
if num_of_ids == 0 :
    print('Warning: There is no ID data in this log', '\n')
# print ('num of found IDs = ' + str(num_of_ids) )


# **************************************************************************
# *** Выделение лога формата json из каждой строки ***
QKD_Metrics_array = []
q = 0
for q_line in qkdmetriclines:
    json_only = re.search(r'(?P<json_str>\{.*\})', q_line) # поиск лога json в строке и запись его в группу 'json_str'
    if json_only:
        # print(json_only)
        QKD_Metrics_array.append(json_only.group('json_str'))
        print('QKD Metrics [', q, '] : ', QKD_Metrics_array[q])
        q = q + 1
    else:
        print('No data found for QKD Metrics')
        QKD_Metrics_array.append('{}')
        print('QKD Metrics [', q, '] : ', QKD_Metrics_array[q])
        q = q + 1

N_QKD_series = len(QKD_Metrics_array) # число попыток выработки КК
print('\nNumber of series', N_QKD_series, '\n')

# ***************************************************************************
# Формирование словаря из каждой строки json => получаем список словарей json_all_data

json_all_data = []
for x in range(N_QKD_series):
    json_single_str_data = json.loads(QKD_Metrics_array[x])  # Формирование словаря из строки json
    json_all_data.append(json_single_str_data)

    if json_all_data[x]:
        json_all_data[x]['NumOfSeries'] = x  # Добавление номера серии в словарь
        json_all_data[x]['Time after start, s'] = time_array[x]  # Добавление шкалы времени в словарь
        json_all_data[x]['Date'] = date_array[x] # Добавление даты
        json_all_data[x]['Timestamp'] = timestamp_array[x] # Добавление абсолютного времени
        if (num_of_ids > 0):
            json_all_data[x]['Alice ID'] = alice_id_array[x]  # Добавление идентификатора QSS Point (Alice ID)

        # print('json to dict str[', x, ']', json_all_data[x])
        json_all_keys = list( json_all_data[x].keys() )   # список ключей в текущем словаре
        # print('Keys (list of parameter):', json_all_keys)
    else:
        json_all_data[x]['Time after start, s'] = time_array[x]  # Добавление шкалы времени в словарь
        json_all_data[x]['NumOfSeries'] = x  # Добавление номера серии в словарь
        json_all_data[x]['Date'] = date_array[x]  # Добавление даты
        json_all_data[x]['Timestamp'] = timestamp_array[x]  # Добавление абсолютного времени
        if (num_of_ids > 0):
            json_all_data[x]['Alice ID'] = alice_id_array[x]  # Добавление идентификатора QSS Point (Alice ID)

        print('No data in str[', x, ']')

N_keys = len(json_all_keys)
print('Number of keys', N_keys)

# *************************************************************************************
# ЗАПИСЬ в файл общее:
print('\nInput file path for optical log')
out_file_directory = easygui.diropenbox()
# out_file_path = input()


# ***   Запись в TXT файл с разделителем ";" ***

# Открыть текстовый файл для записи\
out_txt_filename = 'optical_log.txt'
out_txt_file = open(out_file_directory + '\\' + out_txt_filename, 'w')
par_separator = ';'

# Записать шапку (названия параметров)
for key in json_all_keys:
    out_txt_file.write(key + par_separator)
    # print(key, '\n')

out_txt_file.write('\n') # переход на новую строку по завершении шапки

# Запись значений параметров по ключам
for z in range(N_QKD_series):
    for key_name in json_all_keys:
        param_value = json_all_data[z].get(key_name,'0') # получаем данные по ключу и если пусто, записываем 0
        out_txt_file.write(str(param_value) + par_separator)
    out_txt_file.write('\n')  # переход на новую строку

print('\n Successfully writing TXT')

out_txt_file.close()


# *** Запись лога в CSV файл ***
out_csv_filename = "optical_log.csv"

try:
    with open(out_file_directory + '\\' + out_csv_filename, 'w') as out_csv_file:
        writer = csv.DictWriter(out_csv_file, fieldnames=json_all_keys, delimiter = ';')
        writer.writeheader()
        for data in json_all_data:
            writer.writerow(data)
except IOError:
    print("I/O error")

print('\n Successfully writing CSV')

print('\n Для выхода нажми Enter')
exit_var = input()
# ****************************************************************************

