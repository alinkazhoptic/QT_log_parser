# Импорт полезной фигни
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import easygui
import time



# Secret key rate calculation
def SKR_calculation(indata):
    parameters_array = indata.columns
    # print('list of parameters for current Alice: \n', parameters_array)
    key_gen_time_array = indata["Key gen time, s"].to_numpy()
    N = len(key_gen_time_array)
    print('N = ', N)
    # print(type(key_gen_time_array))
    print('Key generation time [s]:', key_gen_time_array)

    secret_key_rate = np.zeros(N)  # объявление массива скорости выработки секретного ключа

    if ('Secret key length after clear' in parameters_array): #если есть столбец с длиной секретного ключа
        secret_key_length = indata['Secret key length after clear'].to_numpy()
        print('Secret key length array [bit]:', secret_key_length)
    else:
        secret_key_length = np.zeros(N)
        print('No QK with this Alice')

    for q in range(N):
        secret_key_rate[q] = secret_key_length[q] / key_gen_time_array[q]

    print('SKR [bit/s] array:', secret_key_rate)
    return secret_key_rate


# *** Отрисовка графиков
def QKD_params_plotting(input_dataframe, time_array, SKR, QBER, alice_id):
    # Colors definitions
    c_red = [0.8, 0, 0]
    c_blue = [0, 0.3, 0.5]
    c_green = [0, 0.5, 0]

    # Line parameters
    line_width = 1
    grid_width = 0.5
    # Marker parameters
    marker_size = 10
    marker_size_on_line = 4

    # Labels
    x_name = 'Time points'

    # Расчет средних значенийи СКО:
    mean_QBER = np.mean(QBER)
    SKO_QBER = np.std(QBER)
    mean_SKR = np.mean(SKR)
    SKO_SKR = np.std(SKR)
    text_for_graphs = ('QBER: \nmean = ' + str("%.2f" % mean_QBER) + ' %' + '\nstandard deviation = ' + str("%.2f" % SKO_QBER) + '\n\n' +
                           'Secret key rate: \nmean = ' + str("%.0f" % mean_SKR) + ' bit/s' + '\nstandard deviation = ' + str("%.2f" % SKO_SKR) + '\n')

    N = len(time_array)

    # Создание фигуры
    fig1 = plt.figure(figsize=[12, 8])

    plt.subplots_adjust(wspace=0.4, hspace=0.4)
    plt.rcParams['font.size'] = '8'
    plt.rcParams['font.family'] = 'Arial'

    fig1.suptitle('QKD output parameters for some Bob and Alice ID ' + str(alice_id), fontsize=10)

    ax_QBER = plt.subplot(321)
    # ax_QBER.set_title('Main parameters')
    ax_QBER.scatter(time_array, QBER, marker='s', color=c_red, s=marker_size )
    ax_QBER.plot(time_array, 10 * np.ones(N), color=c_red, linestyle='--', linewidth=line_width)
    ax_QBER.set(ylabel='QBER, %')
    ax_QBER.grid(True, linestyle=':', linewidth=grid_width)
    ax_QBER.legend(['data','upper bound'], loc='upper right')

    ax_KeyRate = plt.subplot(323, sharex=ax_QBER)
    ax_KeyRate.scatter(time_array, SKR, marker='^', color=c_blue, s=marker_size)
    ax_KeyRate.set(xlabel=x_name, ylabel='Secret key rate, bit/s')
    ax_KeyRate.grid(True, linestyle=':', linewidth=grid_width)

    ax_Text = plt.subplot(325)
    ax_Text.axis('off')
    ax_Text.text(0.1, 0.2, text_for_graphs, fontsize=10 )

    ax_Eff = plt.subplot(322)
    # ax_Eff.set_title('Technical parameters')
    ax_Eff.plot(time_array, input_dataframe['APD0 Eff clicks'], marker='D', color=c_green, linewidth=line_width, markersize=marker_size_on_line) #, s=marker_size )
    ax_Eff.plot(time_array, input_dataframe['APD1 Eff clicks'], marker='D', color=c_blue, linewidth=line_width, markersize=marker_size_on_line) #, s=marker_size )
    ax_Eff.plot(time_array, 0.00001 * np.ones(N), color=c_red, linestyle='--', linewidth=line_width)
    ax_Eff.set(ylabel='Efficiency, SPAD counts/pulse')
    ax_Eff.legend(['SPAD 0', 'SPAD 1', 'Critical lower bound'], loc='upper right')
    ax_Eff.grid(True, linestyle=':', linewidth=grid_width)

    ax_Flare = plt.subplot(324, sharex=ax_Eff)
    ax_Flare.plot(time_array, input_dataframe['APD0 flare'], marker='o', color=c_green, linewidth=line_width, markersize=marker_size_on_line) #, s=marker_size )
    ax_Flare.plot(time_array, input_dataframe['APD1 flare'], marker='o', color=c_blue, linewidth=line_width, markersize=marker_size_on_line) #, s=marker_size )
    ax_Flare.plot(time_array, 0.00001*np.ones(N), color=c_red, linestyle='--', linewidth=line_width)
    ax_Flare.set(ylabel='Flare clicks, cnt/pulse')
    ax_Flare.legend(['SPAD 0', 'SPAD 1', 'Critical upper bound'], loc='upper right')
    ax_Flare.grid(True, linestyle=':', linewidth=grid_width)


    ax_Vis = plt.subplot(326, sharex=ax_Eff)
    ax_Vis.plot(time_array, input_dataframe['APD0 visibility'], marker='s', color=c_green, linewidth=line_width, markersize=marker_size_on_line)#, s=marker_size)
    ax_Vis.plot(time_array, input_dataframe['APD1 visibility'], marker='s', color=c_blue, linewidth=line_width, markersize=marker_size_on_line) #, s=marker_size )
    ax_Vis.plot(time_array, 80*np.ones(N), color=c_red, linestyle='--', linewidth=line_width)
    ax_Vis.set(xlabel=x_name, ylabel='Visibility, %')
    ax_Vis.legend(['SPAD 0', 'SPAD 1', 'Critical lower bound'], loc='upper right')
    ax_Vis.grid(True, linestyle=':', linewidth=grid_width)

    return fig1

def PDFsaving(filepath, filename, fig1, fig2):
    pdf = PdfPages(filepath + filename + '.pdf')
    pdf.savefig(fig1)
    pdf.savefig(fig2)

    pdf.close()
    return(0)


# Зарузка данных

# *** Путь до файла лога ***
print('1. Select optical log file \n')
filepath = easygui.fileopenbox(filetypes = ['*.csv', '*.csv.*'])

# Запрос сохранения и путя сохранения
print('For graphs saving input Y, to continue without saving press enter')
save_req = input()
if (save_req == 'Y') or (save_req == 'y'):
    print('2. Select a directory to save graphs')
    out_file_directory = easygui.diropenbox() + '\\' # Путь до места сохранения '\\' добавлено для последующего присоединения имени файла

# *** Чтение csv файла:
input_data = pd.read_csv(filepath, delimiter=';')
print('Input table:\n', input_data)


# *** Группировка по ID Алис ***
if 'Alice ID' in input_data.keys():
    grouped_input_data = input_data.groupby('Alice ID')
    alice_id_list = list(grouped_input_data.groups.keys())
    print(alice_id_list)

# Цикл по ID Алис для построения графиков и их сохранения
for idx in alice_id_list:
    print('Alice ID: ', idx)
    data_id = grouped_input_data.get_group(idx)
    parameters_array = data_id.columns
    print('List of parameters for Alice', str(idx), ': \n', parameters_array)

    SecretKeyRate = SKR_calculation(data_id)
    N_points = len(SecretKeyRate)

    if 'QBerr' in parameters_array:
        QBER_array = data_id["QBerr"].to_numpy()
    else:
        QBER_array = np.zeros(N_points)

    # Ошибки выработки: вывод на отдельный figure
    err_status = 0
    if 'Error' in parameters_array:
        err_status = 1
        Errors_text = data_id["Error"].to_numpy()
        print('Alice ID', idx, ' errors:\n', Errors_text)
    else:
        Errors_text = ['no errors']

    fig_errors = plt.figure(figsize=[12, 8])
    plt.title('Errors list of QKD with Alice ID ' + str(idx) + ':')
    ax_err = plt.subplot(111)
    x0 = 0.1
    y0 = 0.8
    for z in range(len(Errors_text)):
        y = y0 - z*0.025
        err_str_out = str(z) + '. ' + str(Errors_text[z])+'\n'
        ax_err.text(x0, y, err_str_out, fontsize=8)
    ax_err.axis('off')
    # ax_err.text(0.1, 0.8, str(Errors_text), fontsize=8)

    Abs_time_array = np.transpose( range(N_points) )
    fig_graph = QKD_params_plotting(data_id, Abs_time_array, SecretKeyRate, QBER_array, idx) # Строим графики для одной Алисы в одном окне
    if (save_req == 'Y') or (save_req == 'y'):
        out_filename = 'QKD with Alice ' + idx
        PDFsaving(out_file_directory, out_filename, fig_graph, fig_errors) # Сохраняем графики в pdf
        if err_status == 0:
            plt.close(fig_errors)
    else:
        print('Warning: graphs didn\'t save')

plt.show() # Отображаем графики

print('\n Press Enter for exit')
exit_var = input()

raise SystemExit()
