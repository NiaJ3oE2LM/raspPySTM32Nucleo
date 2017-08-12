#include "mbed.h"

Timeout del;
Timeout del2;
Timeout del3;
DigitalIn ain0(PA_8);
DigitalIn ain1(PB_10);

InterruptIn button(USER_BUTTON); 
Serial pc(SERIAL_TX, SERIAL_RX);
DigitalOut led(LED1);

bool isrunning = false;
int sampling_rate = 10;
float attach_delay = .1;

const int line_length = 10;

char rx_line[line_length];

void read_str();
void irq();
void log_data();
void select_mode();
void print_info();
void blink();

int main(){ 
    pc.baud(115200);
    pc.attach(&read_str, Serial::RxIrq);
    button.fall(&irq);
    // del3.attach(&print_info, 1);
    while(1){}   
}

    
void irq(){
// avvia o arresta la funzione log
    if(isrunning){
        led=0;
        isrunning = false;
        del2.detach();
        }
    else{
        led=1;
        isrunning = true;
        del2.attach(&log_data, 1.0/sampling_rate);
        }
    return;
    }
    
void blink(){
    led = 1; wait(.5); led = 0;
    return;
    }
    

void print_info(){
// print valori da monitorare
    pc.printf("\ns_rate: %d   isrunning: %d   [%s , %s]", sampling_rate, isrunning, rx_line[0], rx_line[1]);
    del3.attach(print_info, 1);
    }
    
void log_data(){
// stampa in seriale i valori dei sensori
    pc.printf("%d %d \n", ain0.read(), ain1.read());  // " \n" richiesto spazio e \n in ioBase.readline() python
    del2.detach();
    del2.attach(&log_data, 1.0/sampling_rate);
    return;
    }


void read_str(){
    __disable_irq();
    pc.gets(rx_line, line_length);
    del.detach();
    del.attach(&select_mode, attach_delay);
    __enable_irq();
    return;
    }


void select_mode(){
// interpreta la modalità richiesta tramite seriale dal rasp
// 'r' record, 'i' update_strumenti, 'numero int' sample_rate
    if(rx_line[0] == 'r'){
        del2.detach();
        del2.attach(&irq, attach_delay);
        }
    else if (rx_line[0] == 'i'){
        // TODO aggiornare con classe strumento
        pc.printf("light_sensor1 light_sensor2 \n");
        blink();
        }
    else{
        sscanf(rx_line, "%d", &sampling_rate);
        blink();
        }
    // pulisci rx_line
    for (int i = 0; i < line_length; i++){
        rx_line[i]= 0;
        }
    return;
}