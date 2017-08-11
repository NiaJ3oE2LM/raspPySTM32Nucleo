import serial.tools.list_ports, serial
import datetime, sys, types, os, time, threading, shelve
import dialog

"""interfaccia di comunicazione Raspberry NucleoSTM

Questo modulo permette la coomunicazione tra STMnucleo e Raspberry tramite porta usb
per comandare un'interfaccia sensori e raccogliere dati in file csv

il codice si divide in sue parti: prima la nucleo entra in modalità init
e continua inviare una stringa con il nome delle variabili. usare lo user button per 
avviare questa sessione. attendere la conferma di ricevuto dati dal rasp
rasp deve poi dare un parse delle variabili e chidere tramite terminale quali memorizzare 

nella seconda fase, la nucleo manda i dati via usb e rasp li appende al file csv fio al 
termine dell'esperimento.

todo, inviare info si sensori per avere i dati con la precisione strumenti
"""


class menu_item:

    def __init__(self, name, info, opts={}):
        self.name =  name
        self.info = info
        self.opts = opts

# todo fare una classe strumento

# GLOBAL VARIABLES
sampling_rate_value = 10
mem_index = []
strumenti = []
file_name, last_description, last_folder = "", '', ''


# sampling rate  menu
sampling_rate = menu_item(name='sampling rate',
                          info="numero di misure per secondo.")
# seleziona strumenti menu
seleziona_strumenti = menu_item(name='seleziona strumenti',
                                info="spostare a destra gli strumenti da utilizzare. viene mostrata la configurazione attuale",
                                opts={'u': 'annulla', 'a': 'tutti'})
# nuova misura
nuova_misura = menu_item(name='nuova misura',
                         info='modificare i campi opportuni, premere ok per iniziare la registrazione',
                         opts={'u': 'annulla', 's': 'inizia registrazione'})

esci = menu_item(name='esci', info='')


def sampling_rate_run(self):
    global sampling_rate_value
    code, ans_str = d.inputbox(title=self.name,
                               text=self.info+"\nattuale: {}.\tNuovo:".format(sampling_rate_value))
    if code == d.OK:
        sampling_rate_value = int(ans_str)

    return menu()


def seleziona_strumenti_run(self):
    global mem_index
    update_strumenti()

    # visuallizza configurazione corrente
    item_list = []
    for i in range(len(strumenti)):
        if i in mem_index:
            item_list.append((str(i), strumenti[i], True))
        else:
            item_list.append((str(i), strumenti[i], False))

    code, ans = d.buildlist(title=self.name,
                            text=self.info,
                            items=item_list)
    if code == d.OK:
        mem_index = list(int(ans[i]) for i in range(len(ans)))

    return menu()


def nuova_misura_run(self):
    global file_name, last_folder, last_description
    # DOC (label, yl, xl, item, yi, xi, field_length, input_length),(row and column numbers starting from 1).
    element_list= [('folder: data/', 1, 1, last_folder, 1, 2, 30, 70),
                   ('description', 2, 1, last_description, 2, 2, 30, 70)]
    code, ans_list = d.form(title=self.name,
                            text=self.info,
                            elements=element_list)
    if code == d.CANCEL:
        return menu()
    else:
        # controlla problemi di /
        folder, descr = ans_list[0].strip('/'), ans_list[1]
        # memorizza ultime preferenze
        last_folder , last_description = folder, descr

        # todo sistemare date time corretto
        filename = str(datetime.datetime.now()).split('.')[0].split()
        filename = '_'.join(filename[::-1])

        # controlla esistenza cartella
        if folder in os.listdir('data/'):
            folder = 'data/' + folder
        else:
            folder = 'data/' + folder
            os.mkdir(folder)

        # crea il file csv e stampa intestazione
        file_name = '{}/{}.csv'.format(folder, filename)
        with open(file_name, mode='w') as file:
            strumenti_str = ', '.join([strumenti[i] for i in mem_index])
            print(descr, file=file)
            print('sample rate:' + str(sampling_rate_value), file=file)
            print(strumenti_str, file=file)

        return record()

# BIND custom function to objects
sampling_rate.run = types.MethodType(sampling_rate_run, sampling_rate)
seleziona_strumenti.run = types.MethodType(seleziona_strumenti_run, seleziona_strumenti)
nuova_misura.run = types.MethodType(nuova_misura_run, nuova_misura)

app = {
    '1': sampling_rate,
    '2': seleziona_strumenti,
    '3': nuova_misura
}


def menu():
    choice_list = []
    for opt in sorted(app):
        choice_list.append((opt, app[opt].name))
    code, ans = d.menu(title='RASPINUCLEO',
                       text='interfaccia di comunicazione raspi nucleo',
                       choices=choice_list)
    if code == d.OK:
        return app[ans].run()
    else:
        logout()
        return exit(0)


def update_strumenti():
    global strumenti
    strumenti = ['str1', 'str2', 'str3']

    return


def record():
    # start recording
    ser.write('1'.encode('utf-8'))

    threading.Thread(target=tail).start()

    while True:
        in_data = read(ser)  # non c'è bisogno di convertire in float o int
        # se timeout viene ritornata una lista vuota, quindi esci
        if not in_data:
            break

        sel_data = (in_data[i] for i in mem_index)  # seleziona solo quelli da memorizzare
        with open(file_name, mode='a') as file:
            print(','.join(sel_data), file=file)


    d.infobox(title='WARNING',
              text='recording has stopped')
    time.sleep(2)
    return menu()


def tail():
    code = d.tailbox(title=file_name,
                     filepath=file_name)
    if code:
        # stop recording, la nucleo rileva l'interrupt in Rx, puoi scrivere qualsiasi cosa
        ser.write('1'.encode('utf-8'))
        return


def logout():

    with shelve.open('last_session', flag='w') as db:
        db['index'] = mem_index
        db['rate'] = sampling_rate_value
        db['folder'] = last_folder
        db['description'] = last_description


def load_last():
    global last_description, last_folder, mem_index, sampling_rate_value
    with shelve.open('last_session', flag='r') as db:
        mem_index = db['index']
        last_folder = db['folder']
        last_description = db['description']
        sampling_rate_value = db['rate']


def read(nucleo_serial):
    """read serial and return string array
    
    :param nucleo_serial: serial object Nucleo
    :return: 
    """
    if nucleo_serial.readable():
        nucleo_serial.flushInput()
        data_list = str(ser.readline()).strip("b'").split()  # cancellare lettere di conversione da byte a str
        if data_list:
            data_list.pop()                                      # l'ultimo elemnto è \n
        # print(data_list)                                     # log
        return data_list
    else:
        return []


"""
suppogo che ci sia solo la nucleo attaccata al raspberry quindi
prendo la prima usb disponibile nella lista
"""

nucleo_port = serial.tools.list_ports.comports()[0][0]
ser = serial.Serial(port=nucleo_port, baudrate=115200, timeout=1)

d = dialog.Dialog(autowidgetsize=True)
# carico database preferenze
load_last()

if __name__ == '__main__':

    update_strumenti()
    menu()
