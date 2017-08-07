import serial.tools.list_ports
import serial, datetime, sys

"""
questo file contiene funzioni per leggere tutti i sensori 
attaccati alla nucleo in modo da poterli salvare in un file
.csv per elaborazione post esperimenti

chiamare con i marametri filename, *args, timeinfo=True, author='Schio Michele'
"""


def init_csv(filename, vars, timeinfo=True, author='Schio Michele'):
    """
    inizializza in file .csv con due righe: la prima contiene ora data e autore
    mentre la seconda indica la struttura dei valori memorizzati nel file
    :param filename: nome del file
    :param vars: nomi variabili nel file
    :param timeinfo: scelta info orario e data
    :param author: scelta utore
    :return:
    """
    with open('{}.csv'.format(filename), mode='a') as file:
        data_str = ','.join(vars)
        info_str = author + ' '
        if timeinfo:
            info_str += str(datetime.datetime.now())
        print(info_str, file=file)
        print(data_str, file=file)

    return


if __name__ == '__main__':
    """
    suppogo che ci sia solo la nucleo attaccata al raspberry quindi 
    prendo la prima usb disponibile nella lista
    """
    nucleo_port = serial.tools.list_ports.comports()[0][0]
    ser = serial.Serial(port=nucleo_port)
    ser.baudrate = 115200

    # init csv
    file_name =  'data/' + input('nome file csv:')  # sottocartella per gestione file
    variabili = input('nomi variabili da memorizzare\nseparate da spazi, usa _ nei nomi!').strip().split()
    init_csv(file_name, variabili)

    print('ready!')

    while True:
        ser.flushInput()
        in_data = str(ser.readline()).strip("b'").split()  # cancellare lettere di conversione da byte a str
        in_data.pop()                                      # l'ultimo elemnto è \n
        print(in_data)                                     # log
        with open('{}.csv'.format(file_name), mode='a') as data_file:
            print(','.join(in_data), file=data_file)
