# RASPINUCLEO
0. sampling rate
1. seleziona strumenti
2. nuova misura

## sampling rate
numero di misura per secondo.
attuale = 10. Nuovo = 

## seleziona strumenti
scrivere gli indici degli strumenti da registrare separati da uno spazio
a tutti
0 str1
1 str2
...

## nuova misura
strumenti selezionati:
str1, str2, str5 ...
filename.csv creato
0 annulla
1 inizia registrazione
...
sampling...
...
filename.csv salvato



"""SCHEMA NUCLEO
1 volta user button: continua mandare la stringa con tutti i sensori nell'ordine in cui poi manderà i dati
LED BLINK, si ferma quando riceve la risposta '1' dalla funzione init_csv()

2 volta user button, LED FISSO: legge i sensori manda tutti i dati alla rasp
"""


# TODOS
+ print session log on menu cancel answer
+ save session variable to cinary file to load on startup ... last folder, last insrtruments..
+ archivio strumenti
+ 

