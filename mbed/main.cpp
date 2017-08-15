#include "mbed.h"

Timeout del;
Timeout del2;
Timeout del3;
Timer t;
AnalogIn ain0(PC_0);
AnalogIn ain1(PC_1);

InterruptIn button(USER_BUTTON); 
Serial pc(USBTX, USBRX);  // usa serial usb per comunicare con il pc
DigitalOut led(LED1);

bool isrunning = false;
float attach_delay = .1;

const int line_length = 10;
int period_us = 1000;  // default 1kHz

char rx_line[line_length];

void read_str();
void irq();
void irq_start();
//void log_data();
void select_mode();
void print_info();
void blink();

int main(){ 
    pc.baud(921600);
    pc.attach(&read_str, Serial::RxIrq);
    button.fall(&irq_start);
    // del3.attach(&print_info, 1);
    while(1){}   
}

/*   
void irq(){
// meno operazioni possibili
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
*/
void irq_start(){
    if (isrunning){
        isrunning = false;
        del2.detach();
        }
    else{
        isrunning = true;
        t.start();
        del2.detach();
        del2.attach(&irq, attach_delay); // serve solo a farla partire
        }
    blink();
    return;
    }    
    
    
void irq(){
    t.reset();
    pc.printf("%u %u \n", ain0.read_u16(), ain1.read_u16());
    if (t.read_us() < period_us){
        del2.detach();
        del2.attach(&irq, (period_us-t.read_us())/1000000.0);
        }
    else{
        del2.detach();
        isrunning = false;
        led = 1;
        }
    return;
    }
    
    
void blink(){
    led = 1; wait(.5); led = 0;
    return;
    }
    

void print_info(){
// print valori da monitorare
    pc.printf("\nperiod_us: %d   isrunning: %d   [%s , %s]", period_us, isrunning, rx_line[0], rx_line[1]);
    del3.attach(print_info, 1);
    }
    
/*    
void log_data(){
// stampa in seriale i valori dei sensori
    pc.printf("%d %d \n", ain0.read(), ain1.read());  // " \n" richiesto spazio e \n in ioBase.readline() python
    del2.detach();
    del2.attach(&log_data, 1.0/sampling_rate);
    return;
    }
*/

void read_str(){
    __disable_irq();
    pc.gets(rx_line, line_length);
    // pc.printf("%s", rx_line);
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
        del2.attach(&irq_start, attach_delay);
        }
    else if (rx_line[0] == 'i'){
        // inviare i numeri riga corrispondenti al file instruments.csv
        pc.printf("1 1 \n");
        blink();
        }
    else{
        sscanf(rx_line, "%d", &period_us);
        // pc.printf("period_us: %d \n", period_us);
        blink();
        }
    // pulisci rx_line
    for (int i = 0; i < line_length; i++){
        rx_line[i]= 0;
        }
    return;
}