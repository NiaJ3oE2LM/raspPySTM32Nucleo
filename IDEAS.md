# futuro
implememtare freeRtos con time scheduling per creare un customm DAQ. nel frattempo utilizza un basso samplerate senz ausare FreeRTOS

# TODOS
- leggere paper openlabs


## utility --> rapiNucleo
+ zero sensor
+ live sensor reading
+ initialize sensors from terminal and setu nucleo

## sensori 
+ amperometro
+ encoder
+ prossimità mbed
+ voltmetro
+ temperatura
+ microfono
+ 

## DAQ
+ come fare a misurare tot digital pin nello STESSO ISTANTE	
+ è davverp necessario usare la nucleo?
SI perchè i pin del rasp sono tutti digitali
+ implementare sistema BAUD_RATE timers via USB, accontentati di un basso sample rate 
+ non usare free RTOS prima di essere arrivato al limite con la libreria timer 

# calculations
+ usando 5 sensori e considerato che Analog.read ritorna un uint16_t (16 bit). aprendo una Serial baud = 921600 bits/s, puoi ottenere --> baud/(5*16) = 11520 samples/s

per implementare questa soluzione, dovresti leggere continuamente la seriale, memeorizzare la lunghezza del segnale di ciascun strumenti oltre aLL'ORDINE in cui arrivano e tenere sincronizzata la comunicazione.

# results
- ottenuto sampling rate 5kHz senza rtos

