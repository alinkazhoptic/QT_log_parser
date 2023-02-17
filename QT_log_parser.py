# Нечто для чтения лога Квантел и формирования массивов эволюции оптических параметров КРК

# Импорт полезной фигни
import re
import json
import csv
import easygui
import time
# import pandas as pd

# /// Входные данные \\\

# Здесь надо записать интересующую дату, как в логе:
# print('\n Введите интересующую дату, как в log-файле, например, "Dec 20" ')
# Date_of_interest = input()


# *** Путь до файла лога ***
print('1. Select log file \n')
file_path = easygui.fileopenbox(filetypes = ['*.log', '*.log.*'])

# Год регистрации лога - ввод снаружи
print('\n Введите год регистрации log-файла, например, 2021 ')
# year_in_log = input()
year_in_log = '2022'

# ***********************************************************

# Тут должны быть используемые функции
def FindTimestamp(str):
    search_result_timestamp = re.search(r'(?P<hours>\d\d):(?P<minutes>\d\d):(?P<seconds>\d\d)', str)
    h = int( search_result_timestamp.group('hours') )
    m = int( search_result_timestamp.group('minutes') )
    s = int( search_result_timestamp.group('seconds') )
    time_s = 60*60*h + 60*m + s
    timestamp = search_result_timestamp.group('hours') + ':' + search_result_timestamp.group(
        'minutes') + ':' + search_result_timestamp.group('seconds')
    return time_s, timestamp

def FindDatestamp(str, year_value):
    search_result_datestamp = re.search(r'(?P<month>\b\w{3}\b)\W+(?P<day>\d+)', str)
    month_value = search_result_datestamp.group('month')
    day_value = search_result_datestamp.group('day')
    datestamp = year_value + '-' + month_value + '-' + day_value
    return datestamp

def FindAliceID(st):
    if st.find('QK_GENERATION_LOG') >= 0:
        search_result_idstamp = re.search(r'(?P<qk>QK_GENERATION_LOG).(?P<id>\w{10}).', st)
    if st.find('Starting QKD protocol for point') >= 0:
        search_result_idstamp = re.search(r'(?P<qk>Starting QKD protocol for point)\s(?P<id>\w{10}).', st)

    print(search_result_idstamp.group('id'))  # Вывод ID Алис, с которыми делались ключи
    alice_id_value = search_result_idstamp.group('id')
    return alice_id_value




# ***********************************************************

# Reading log-file of Quantel
logfile_obj = open(file_path, 'rt') #'rt' - открытие для чтения (r) текстового (t) файла
loglines = logfile_obj.readlines()
logfile_obj.close()
print(len(loglines), 'lines successfully read')

# ***********************************************************

#Запись всех линий (строк) с оптическим логом в один массив qkdmetriclines
qkdmetriclines = []
# parse_phrase_sent = 'qkdom'
num_of_req_str_sent = 0  # счетчик строк, содержащих parse_phrase_1

# parse_phrase_received = 'QK_GENERATION_LOG'
num_of_req_str_received = 0  # счетчик строк, содержащих parse_phrase_2

ErrorLine = '{"Key Errors":1}'

delta_time_array = []
t_start = 0
timestamp_start = ''
t_end = 0
timestamp_end = ''

timestamp_array = []
datestamp_array = []

alice_id_array = []
ID_empty = '0x0'
AliceID = ID_empty
num_of_ids = 0

metric_line = ''

key_status = False

for line in loglines:
    if line.find('Starting QKD protocol for point') >= 0:
        AliceID = FindAliceID(line)

    if (line.find('Key generation started') >= 0):
        if ((t_start != 0) and (t_end != 0)):
            delta_time_array.append(t_end - t_start)
            timestamp_array.append(timestamp_end)
            qkdmetriclines.append(ErrorLine)
            alice_id_array.append(AliceID)
            t_start = 0
            timestamp_start = ''
            t_end = 0
            timestamp_end = ''
        # AliceID = ID_empty
        key_status = 0
        t_start, timestamp_start = FindTimestamp(line)
        # datestamp_array.append(FindDatestamp(line, year_in_log)) #дата записывается по каждому найденному старту
        print('start time - ', timestamp_start, ' = ', t_start, ' s')

    if ( (line.find('qkdom') >= 0) and (line.find('Metrics:') >= 0) ) :
        if ~key_status:
            key_status = True
            num_of_req_str_sent = num_of_req_str_sent + 1
            t_sent, timestamp_sent = FindTimestamp(line)
            t_end, timestamp_end = FindTimestamp(line)
            delta_time_array.append(t_end - t_start)
            timestamp_array.append(timestamp_sent)
            datestamp_array.append(FindDatestamp(line, year_in_log))  # дата записывается по каждой найденной отправке метрик
            alice_id_array.append(AliceID)
            # datestamp_array.append(FindDatestamp(line, year_in_log))
            print('end time - ', timestamp_end, ' = ', t_end, ' s')
            print("t_end = ", t_end)
            print("t_start = ", t_start)
            print('key gen time = ', t_end - t_start)

            qkdmetriclines.append(line)
            if (line.find('"Error":') >= 0):
                print('QK generation errors')
            # if (line.find('QBerr') >= 0):
            #     qkdmetriclines.append(line)
            # else:
            #     qkdmetriclines.append('{"No_QBER_data":1}')
            t_start = 0 # обнуление времен начала/окончания генерации - переход к новой генерации
            timestamp_start = ''
            t_end = 0
            timestamp_end = ''
            AliceID = ID_empty
        else:
            print('Double qkdom Metrics')

    if (line.find('Key generation ended') >= 0):
        if ~key_status:
            t_end, timestamp_end = FindTimestamp(line)
            print('end time - ', timestamp_end, ' = ', t_end, ' s')
            print('No key')

    if (line.find('QK_GENERATION_LOG') >= 0):
        num_of_req_str_received = num_of_req_str_received + 1
        AliceID = FindAliceID(line)
        num_of_ids = num_of_ids + 1
        print('QK_generation_log found!')
        if key_status: # если был ключ, то надо записать только ID
            alice_id_array[-1] = AliceID
        else:
            t_received, timestamp_received = FindTimestamp(line)
            delta_time_array.append(t_end - t_start)
            timestamp_array.append(timestamp_received)
            datestamp_array.append(
                FindDatestamp(line, year_in_log))  # дата записывается по каждому приему метрик
            alice_id_array.append(AliceID)
            qkdmetriclines.append(line)
            t_start = 0  # обнуление времен начала/окончания генерации - переход к новой генерации
            timestamp_start = ''
            t_end = 0
            timestamp_end = ''
            AliceID = ID_empty


# *** Проверка конца файла: ***
if t_start != 0: #генерация началась
    if t_end != 0: #обычный случай, генерация завершилась но ключа нет
        delta_time_array.append(t_end - t_start)
        timestamp_array.append(timestamp_end)
        qkdmetriclines.append(ErrorLine)
        alice_id_array.append(AliceID)
    else: #генерация не прекратилась
        delta_time_array.append(0)
        timestamp_array.append(timestamp_start)
        qkdmetriclines.append('{"QK generation is not ended":1}')
        alice_id_array.append(AliceID)

# *** Проверка длин массивов ***
print('\n Arrays length checking:')
print('Datestamp - ', len(datestamp_array))
print('Timestamp - ', len(timestamp_array))
print('Key gen time - ', len(delta_time_array))
print('Alice ID - ', len(alice_id_array))
print('QKD Metrics - ', len(qkdmetriclines))


if (num_of_req_str_sent != num_of_req_str_received): # проверка равенства числа полученных УК логов с количеством отправленных
    print('The number of sent logs is not equal to the number of received logs')
    print('n_sent = ', num_of_req_str_sent, ' n_recieved = ', num_of_req_str_received, '\n')

if (qkdmetriclines != []):
    print('Parsing completed successfully!')
    print(len(qkdmetriclines), 'series QKD metric lines founded')
    if (num_of_req_str_sent == 0) :
        print ('Warning: There is no "qkdom Metrics" in this log')
    if (num_of_req_str_received == 0) :
        print ('Warning: There is no "QK_GENERATION_LOG" in this log')


elif ( (num_of_req_str_sent == 0) & (num_of_req_str_received == 0) ):
    print('\nRecuired "qkdom Metrics" and "QK_GENERATION_LOG" does not exist in this log-file')
    # print('Close after 10 seconds')
    # time.sleep(10)
    # raise SystemExit()


# **************************************************
# *** Печать Alice ID
N_ids = len(alice_id_array)

if num_of_ids == 0 :
    print('Warning: There is no ID data in this log', '\n')
else:
    print('IDs of QSS Points:')
    for st in alice_id_array:
        print(st)  # Вывод ID Алис, с которыми делались ключи
    print('num of found IDs = ', num_of_ids)

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
json_all_keys = {'NumOfSeries'}
for x in range(N_QKD_series):
    json_single_str_data = json.loads(QKD_Metrics_array[x])  # Формирование словаря из строки json
    json_all_data.append(json_single_str_data)

    if json_all_data[x] == []:
        print('No data in str[', x, ']')
        # print('json to dict str[', x, ']', json_all_data[x])
    else:
        print('Date and time filling for line ', x)

    json_all_data[x]['NumOfSeries'] = x  # Добавление номера серии в словарь
    json_all_data[x]['Key gen time, s'] = delta_time_array[x]  # Добавление шкалы времени в словарь
    json_all_data[x]['Date'] = datestamp_array[x]  # Добавление даты
    json_all_data[x]['Timestamp'] = timestamp_array[x]  # Добавление абсолютного времени
    if (N_ids > 0):
        json_all_data[x]['Alice ID'] = alice_id_array[x]  # Добавление идентификатора QSS Point (Alice ID)


    json_all_keys.update(json_all_data[x].keys())
    # print('Keys (list of parameter):', json_all_keys)

N_keys = len(json_all_keys)
print('Number of parameters (JSON keys)', N_keys)

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

# ****************************

print('\n Press Enter for exit')
exit_var = input()
# ****************************************************************************

