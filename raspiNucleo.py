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

    def __init__(self, name, info):
        self.name = name
        self.info = info


# todo fare una classe strumento

# GLOBAL VARIABLES
sampling_Hz = 1000  # period_us microseconds nucleo timer
mem_index = []
available_instruments = []
instruments_db = []
file_name, last_description, last_folder = "", '', ''

"""STRUTTURA MENU INIZIALE """
# sampling rate  menu
sampling_rate = menu_item(name='sampling rate',
                          info="frequenza di campionamento in Hz")
# seleziona strumenti menu
seleziona_strumenti = menu_item(name='seleziona strumenti',
                                info="spostare a destra gli strumenti da utilizzare. viene mostrata la configurazione attuale")
# imposta strumenti menu
imposta_strumenti = menu_item(name='imposta strumenti',
                              info="impostare pin e tipo di strumento")

# nuova misura
nuova_misura = menu_item(name='nuova misura',
                         info='premere ok per iniziare la registrazione')

app = {
    '1': sampling_rate,
    '#': imposta_strumenti,
    '2': seleziona_strumenti,
    '3': nuova_misura
}


def sampling_rate_run(self):
    """
    funzione bind oggetto sampling_rate. chiede di reimpostare il parametro sampling rate

    :param self:
    :return:
    """
    # todo aggiornare il parametro via serial sulla nucleo
    global sampling_Hz
    code, ans_str = d.inputbox(title=self.name,
                               text=self.info+"\nattuale: {}.\tNuovo:".format(sampling_Hz))
    if code == d.OK and ans_str:
        sampling_Hz = int(ans_str)
        update_sampling_rate()


def seleziona_strumenti_run(self):
    """
    bind oggetto seleziona_strumenti. imposta la variabile mem_index con gli  indici
    degli strumenti da memorizzare secondo l'ordine in cui comunica la nucleo
    :param self:
    :return:
    """

    # todo sistemare upgrade_struenti
    global mem_index
    update_strumenti()

    # visuallizza configurazione corrente
    item_list = []
    for i in range(len(available_instruments)):
        if i in mem_index:
            item_list.append((str(i), instruments_db[int(available_instruments[0])][0], True))
        else:
            item_list.append((str(i), instruments_db[int(available_instruments[i])][0], False))

    code, ans = d.buildlist(title=self.name,
                            text=self.info,
                            items=item_list)
    if code == d.OK:
        mem_index = list(int(ans[i]) for i in range(len(ans)))


def nuova_misura_run(self):
    """
    bind oggetto nuova_misura. crea il nuovo file csv specificando la cartella e la descrizione
    :param self:
    :return:
    """
    global file_name, last_folder, last_description
    # DOC (label, yl, xl, item, yi, xi, field_length, input_length),(row and column numbers starting from 1).
    col = max([len('folder: data/'),len('description')])+1
    element_list= [('folder: data/', 1, 1, last_folder, 1, col, 20, 100),
                   ('description:', 2, 1, last_description, 2, col, 20, 100)]
    # info strumenti
    strumenti_str = ', '.join(available_instruments[i] for i in mem_index)

    code, ans_list = d.form(title=self.name,
                            text=(self.info + '\nSampling_rate:' + str(sampling_Hz) + '\nStrumenti:' + strumenti_str),
                            elements=element_list)
    if code == d.CANCEL:
        return menu()
    else:
        # controlla problemi di /
        folder, descr = ans_list[0].strip('/'), ans_list[1]
        # memorizza ultime preferenze
        last_folder, last_description = folder, descr

        # corretto cos', il rasp ha una timezone diversa
        filename = str(datetime.datetime.now()).split('.')[0].split()
        filename = '_'.join(filename[::-1])

        # controlla esistenza cartella
        if not folder:
            folder = 'data'  # senza / [1]
        elif folder in os.listdir('data/'):
            folder = 'data/' + folder
        else:
            folder = 'data/' + folder
            os.mkdir(folder)

        # crea il file csv e stampa intestazione [1]x
        file_name = '{}/{}.csv'.format(folder, filename)
        with open(file_name, mode='w') as file:
            print(descr, file=file)
            print('sample rate:' + str(sampling_Hz), file=file)
            print(strumenti_str, file=file)

        return record()

# BIND custom function to objects
sampling_rate.run = types.MethodType(sampling_rate_run, sampling_rate)
seleziona_strumenti.run = types.MethodType(seleziona_strumenti_run, seleziona_strumenti)
nuova_misura.run = types.MethodType(nuova_misura_run, nuova_misura)


def menu():
    """
    visualizza il menu principale
    :return:
    """
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


def update_strumenti():
    """
    aggiorn ala lista degli strumenti dispobili
    :return:
    """
    global available_instruments
    # start instrument mode with 'i'
    write('i')
    available_instruments = read()


def update_sampling_rate():
    """Comunica alla Nucleo il nuovo PERIODO di campionamento in

    nuovo periodo = 1000000[us]/f[Hz]
    """
    str_LF = str(1000000 // sampling_Hz)
    write(str_LF)
    pass


def toggle_record():
    """send 'r' to nucleo and nucleo should stop sending data if
    sendong, shoud start if not sending
    """
    write('r')
    pass


def record():
    """avvia la registrazione sulla nucleo esalva i valori sul file csv
    :return:
    """
    toggle_record()
    threading.Thread(target=tail).start()
    with open(file_name, mode='a') as file:
        in_str = read()
        while in_str:  # in_str list vuota se non c'è nulla
            # todo la nucleo deve spedire in seriale solo quello chel'utente vuole! altrimenti perdi velocità
            # todo togliere mem_index dall'algoritmo
            in_str = read()
            print(in_str, file=file)
            in_str = ser.readline()

    d.infobox(title='WARNING',
              text='recording has stopped')
    time.sleep(1)


def tail():
    """
    visualizza il contenuto del file csv mentre viene popolato
    :return:
    """
    code = d.msgbox(text='scrivendo i dati su: {}\nPremere ok per terminare '.format(file_name))
    if code:
        toggle_record()


def logout():
    """
    memorizza le variabili utente per il prossimo avvio
    :return:
    """

    with shelve.open('last_session', flag='w') as db:
        db['index'] = mem_index
        db['rate'] = sampling_Hz
        db['folder'] = last_folder
        db['description'] = last_description

    os.system('clear')
    return exit(0)


def start_load():
    """carica le variabili utente dal database e gli strumenti dal file instruments.csv

    :return:
    """
    global last_description, last_folder, mem_index, sampling_Hz
    with shelve.open('last_session', flag='r') as db:
        mem_index = db['index']
        last_folder = db['folder']
        last_description = db['description']
        sampling_Hz = db['rate']

    update_sampling_rate()  # chiamare dopo aver caricato il valore

    update_strumenti()  # permette di eseguire subito una nuova misura
    print(available_instruments)
    with open('instruments.csv', mode='r') as file:
        for line in file:
            instruments_db.append(line.split(','))

    pass


def write(string):
    """aggiunge LF a string e converte in binario, quindi scrive in ser"""
    if ser.writable():
        # TODO capire perchè succede questa cazzata!
        string = string[:1] + ' ' + string[1:] + '\n'

        ser.flushOutput()
        ser.write(bytearray(string, 'utf-8'))
        # print('sent: ', string.encode('utf-8'))
    else:
        print('ser not writable')

    pass


def read():
    """read serial and return string array
    
    :param ser: serial object Nucleo
    :return: empty array in serial is not readable
    """
    ser.reset_input_buffer()
    data_list = str(ser.readline()).strip("b' \\n").split()  # cancellare lettere di conversione da byte a str
    return data_list


""" AVVIO SERIALE NUCLEO
suppogo che ci sia solo la nucleo attaccata al raspberry quindi
prendo la prima usb disponibile nella lista
"""
try:
    nucleo_port = serial.tools.list_ports.comports()[0][0]
except:
    print("nucleo è connessa?")
    exit(0)

ser = serial.Serial(port=nucleo_port, baudrate=921600, timeout=2, write_timeout=2)
d = dialog.Dialog(autowidgetsize=True)

if __name__ == '__main__':
    start_load()
    print()
    while True:
        menu()
