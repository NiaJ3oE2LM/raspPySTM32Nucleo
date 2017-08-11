import serial.tools.list_ports
import serial, datetime, sys, types, os, time

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
mem_index = range(2)
strumenti = []

# sampling rate  menu
sampling_rate = menu_item(name='sampling rate',
                          info="numero di misure per secondo.")
# seleziona strumenti menu
seleziona_strumenti = menu_item(name='seleziona strumenti',
                                info="scrivere gli indici degli strumenti da registrare separati da uno spazio",
                                opts={'u': 'annulla', 'a': 'tutti'})
# nuova misura
nuova_misura = menu_item(name='nuova misura',
                         info='avvio nuova misura',
                         opts={'u': 'annulla', 's': 'inizia registrazione'})

esci = menu_item(name='esci', info='')

def sampling_rate_run(self):
    global sampling_rate_value
    # show info
    os.system('clear')
    print("\n{}\n{}".format(self.name.upper(), self.info))

    sampling_rate_value = int(input("attuale: {}.\tNuovo: ".format(sampling_rate_value)))

    return menu()


def seleziona_strumenti_run(self):
    global mem_index
    # show info
    os.system('clear')
    print("\n{}\n{}".format(self.name.upper(), self.info))

    res = []  # array STRING risposte accettabili

    # todo chiama la nucleo per ricevere le info sugli strumenti

    update_strumenti()
    for i in range(len(strumenti)):
        print("{} - {}".format(i, strumenti[i]))
        res.append(str(i))  # solo qui perchè quando scrivi mem_index non ti serve opts

    # print opts
    for opt in self.opts:
        print("{} - {}".format(opt, self.opts[opt]))


    # todo sistemare potenziali errori
    ans = input("+\tseleziona un'opzione: ")

    if ans == 'u':
        menu()
    elif ans == 'a':
        mem_index = range(len(strumenti))  # se inizializzi già come tutti, questo non serve
        print('selezionati tutti gli strumenti')
        return menu()
    elif ans != 'a':
        mem_index = []
        # usa la stringa come array di indici, converti in int
        for index in ans.split():
            if index in res:
                mem_index.append(int(index))

    selezionati_str = ', '.join([strumenti[i] for i in mem_index]) # cosa strana ma funziona
    print("strumenti selezionati: {}".format(selezionati_str))

    # wait 2 sec
    time.sleep(2)
    return menu()


def nuova_misura_run(self):
    # show info
    os.system('clear')
    print("\n{}\n{}".format(self.name.upper(), self.info))
    # print info strumenti
    strumenti_str = ', '.join([strumenti[i] for i in mem_index])
    print("strumenti selezionati: {}".format(strumenti_str))

    # crea il file csv
    filename = str(datetime.datetime.now()).split('.')[0].split()
    filename = '_'.join(filename[::-1])
    with open('data/{}.csv'.format(filename), mode='w') as file:
        print(strumenti_str, file=file)

    print("data/{}.csv creato correttamente".format(filename))

    # print opts
    for opt in self.opts:
        print("{} - {}".format(opt, self.opts[opt]))

    ans = scegli(self.opts)

    if ans == 'u':
        # rimuovi il file sbagliato
        os.system('rm data/{}.csv'.format(filename))
        return menu()
    else:
        print('inizio registrazione')
        # registra()


def esci_run(self):
    # todo print log della sessione
    return exit(0)

# BIND custom function to objects
sampling_rate.run = types.MethodType(sampling_rate_run, sampling_rate)
seleziona_strumenti.run = types.MethodType(seleziona_strumenti_run, seleziona_strumenti)
nuova_misura.run = types.MethodType(nuova_misura_run, nuova_misura)
esci.run = types.MethodType(esci_run, esci)

app = {
    '1': sampling_rate,
    '2': seleziona_strumenti,
    '3': nuova_misura,
    '4': esci
}


def menu():
    """visualizza un dizionario come menu
    Args:
        app : dizionario da visualizzare
    """

    # pulisci schermo e visualizza menu
    os.system('clear')
    print('\nraspinucleo'.upper())
    for opt in sorted(app):
        print('{} - {}'.format(opt, app[opt].name))

    # attendi risposta
    ans = scegli(app)

    # esegui funzione caratteristica
    return app[ans].run()


def init_csv(nucleo_serial, mem_all_vars = True, sampling_rate=5):
    """inizializza file csv, seleziona variabili da memorizzare e ritona filename e array di indici

    ogni file viene denominato con un timestamp e nella prima
    riga si indicano i nomi dei dati per colonna
    """

    # filename
    filename = str(datetime.datetime.now()).split('.')[0].split()
    filename = '_'.join(filename)

    """variabili da memorizzare:
     mem_index contiene TUTTI gli indici delle variabili
    da memorizzare nell'ordine in cui la nucleo le manderà
    """
    vars_name = read(nucleo_serial)
    mem_index = range(len(vars_name))
    if not mem_all_vars:
        # print vars and instructions, mach indexes
        print('available vars:{}'.format(vars_name))
        index_str = input("type 'a' to select all, type index number separated by splace to select individually")
        if index_str != 'a':
            mem_index = []
            # usa la stringa come array di indici, converti in int
            for index in index_str.split():
                mem_index.append(int(index))

    # crea il file
    with open('{}.csv'.format(filename), mode='a') as file:
        first_row =','.join(vars_name[mem_index])  # funziona come matlab?
        print(first_row, file=file)

    #  TODO info sensori errori e tipo
    # TODO  impostare sampling rate

    # la converma alla nucleo contiene il sampling rate per l'esperimento
    print(sampling_rate, file=nucleo_serial)

    return filename, mem_index


def update_strumenti():
    global strumenti
    strumenti = ['str1', 'str2', 'str3']
    mem_index = range(len(strumenti))
    return


def scegli(available):
    ans = ''
    while ans not in available:
        ans = input("+\tseleziona un'opzione: ")

    return ans


def read(nucleo_serial):
    """read serial and return string array
    
    :param nucleo_serial: serial object Nucleo
    :return: 
    """
    if nucleo_serial.isreadable():
        nucleo_serial.flushInput()
        data_list = str(ser.readline()).strip("b'").split()  # cancellare lettere di conversione da byte a str
        data_list.pop()                                      # l'ultimo elemnto è \n
        print(data_list)                                     # log
        return data_list
    else:
        print('serial is not readable! check connection!')
        return []


# """
# suppogo che ci sia solo la nucleo attaccata al raspberry quindi
# prendo la prima usb disponibile nella lista
# """
#
# nucleo_port = serial.tools.list_ports.comports()[0][0]
# ser = serial.Serial(port=nucleo_port, baudrate=115200)
#

if __name__ == '__main__':

    # while True:
    #     in_data = read(ser)  # non c'è bisogno do convertire in float o int
    #     in_data = in_data[vars_index]  # seleziona solo quelli da memorizzare
    #     with open('{}.csv'.format(file_name), mode='a') as data_file:
    #         print(','.join(in_data), file=data_file)
    #
    #     # imposta timerout per vedere quando la nuclo non manda più nulla
    update_strumenti()
    # os.system('export TERM=xterm')  # errore TERM variable
    menu()

"""SCHEMA NUCLEO
1 volta user button: continua mandare la stringa con tutti i sensori nell'ordine in cui poi manderà i dati
LED BLINK, si ferma quando riceve la risposta '1' dalla funzione init_csv()

2 volta user button, LED FISSO: legge i sensori manda tutti i dati alla rasp
"""
