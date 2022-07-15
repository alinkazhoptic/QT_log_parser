# Импорт полезной фигни
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import easygui
import time



# Secret key rate calculation
def SKR_calculation(indata):
    secret_key_length = indata['Secret key length after clear'].to_numpy()
    key_gen_time_array = indata["Key gen time, s"].to_numpy()
    N = len(secret_key_length)
    print('N = ', N)
    # print(type(key_gen_time_array))
    print('Key generation time [s]:', key_gen_time_array)
    print('Secret key length array [bit]:', secret_key_length)
    secret_key_rate = np.zeros(N)
    for q in range(N):
        secret_key_rate[q] = secret_key_length[q]/key_gen_time_array[q]

    print('SKR [bit/s] array:', secret_key_rate)
    return(secret_key_rate)


# *** Отрисовка графиков
def QKD_params_plotting(input_dataframe, time_array, SKR, alice_id):
    # Colors definitions
    c_red = [0.8, 0, 0]
    c_blue = [0, 0.3, 0.5]
    c_green = [0, 0.5, 0]

    # Line parameters
    line_width = 1
    grid_width = 0.5
    # Marker parameters
    marker_size = 10

    # Labels
    x_name = 'Time points'

    # Расчет средних значенийи СКО:
    mean_QBER = np.mean(input_dataframe['QBerr'])
    SKO_QBER = np.std(input_dataframe['QBerr'])
    mean_SKR = np.mean(SKR)
    SKO_SKR = np.std(SKR)
    text_for_graphs = ('QBER: \nmean = ' + str("%.2f" % mean_QBER) + ' %' + '\nstandard deviation = ' + str("%.2f" % SKO_QBER) + '\n\n' +
                           'Secret key rate: \nmean = ' + str("%.0f" % mean_SKR) + ' bit/s' + '\nstandard deviation = ' + str("%.2f" % SKO_SKR) + '\n')

    # Создание фигуры
    fig1 = plt.figure(figsize=[12, 8])

    plt.subplots_adjust(wspace=0.4, hspace=0.4)
    plt.rcParams['font.size'] = '8'
    plt.rcParams['font.family'] = 'Arial'

    fig1.suptitle('QKD output parameters for some Bob and Alice ID ' + str(alice_id), fontsize=10)

    ax_QBER = plt.subplot(321)
    # ax_QBER.set_title('Main parameters')
    ax_QBER.scatter(time_array, input_dataframe['QBerr'], marker='s', color=c_red, s=marker_size )
    ax_QBER.set(ylabel='QBER, %')
    ax_QBER.grid(True, linestyle=':', linewidth=grid_width)

    ax_KeyRate = plt.subplot(323, sharex=ax_QBER)
    ax_KeyRate.scatter(time_array, SKR, marker='^', color=c_blue, s=marker_size)
    ax_KeyRate.set(xlabel=x_name, ylabel='Secret key rate, bit/s')
    ax_KeyRate.grid(True, linestyle=':', linewidth=grid_width)

    ax_Text = plt.subplot(325)
    ax_Text.axis('off')
    ax_Text.text(0.1, 0.2, text_for_graphs, fontsize=10 )

    ax_Eff = plt.subplot(322)
    # ax_Eff.set_title('Technical parameters')
    ax_Eff.scatter(time_array, input_dataframe['APD0 Eff clicks'], marker='D', color=c_green, s=marker_size )
    ax_Eff.scatter(time_array, input_dataframe['APD1 Eff clicks'], marker='D', color=c_blue, s=marker_size )
    ax_Eff.set(ylabel='Efficiency, SPAD counts/pulse')
    ax_Eff.legend(['SPAD 0', 'SPAD 1'], loc='upper right')
    ax_Eff.grid(True, linestyle=':', linewidth=grid_width)

    ax_Flare = plt.subplot(324, sharex=ax_Eff)
    ax_Flare.scatter(time_array, input_dataframe['APD0 flare'], marker='o', color=c_green, s=marker_size )
    ax_Flare.scatter(time_array, input_dataframe['APD1 flare'], marker='o', color=c_blue, s=marker_size )
    ax_Flare.set(ylabel='Flare clicks, cnt/pulse')
    ax_Flare.legend(['SPAD 0', 'SPAD 1'], loc='upper right')
    ax_Flare.grid(True, linestyle=':', linewidth=grid_width)

    ax_Vis = plt.subplot(326, sharex=ax_Eff)
    ax_Vis.scatter(time_array, input_dataframe['APD0 visibility'], marker='s', color=c_green, s=marker_size)
    ax_Vis.scatter(time_array, input_dataframe['APD1 visibility'], marker='s', color=c_blue, s=marker_size )
    ax_Vis.set(xlabel=x_name, ylabel='Visibility, %')
    ax_Vis.legend(['SPAD 0', 'SPAD 1'], loc='upper right')
    ax_Vis.grid(True, linestyle=':', linewidth=grid_width)

    return fig1

def PDFsaving(filepath, filename, fig):
    pdf = PdfPages(filepath + filename + '.pdf')
    pdf.savefig(fig)
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
    # SecretKeyRate = [1]
    SecretKeyRate = SKR_calculation(data_id)
    N_points = len(SecretKeyRate)
    Abs_time_array = np.transpose( range(N_points) )
    fig_for_idx = QKD_params_plotting(data_id, Abs_time_array, SecretKeyRate, idx) # Строим графики для одной Алисы в одном окне
    if (save_req == 'Y') or (save_req == 'y'):
        out_filename = 'QKD with Alice ' + str(idx)
        PDFsaving(out_file_directory, out_filename, fig_for_idx) # Сохраняем графики в pdf
    else:
        print('Warning: graphs didn\'t save')

plt.show() # Отображаем графики

print('\n Press Enter for exit')
exit_var = input()

raise SystemExit()
