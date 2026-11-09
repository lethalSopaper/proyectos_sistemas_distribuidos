#Ugartechea Gonzalez Luis Antonio -- 320223822
from multiprocessing import Process, Pipe
from os import getpid
import time

def local_time(counter):
    return ' (LAMPORT_TIME={})'.format(counter)

def calc_recv_timestamp(recv_time_stamp, counter):
    return max(recv_time_stamp, counter) + 1

def event(pid, counter, event_name="", p_name=""):
    counter += 1
    print(f'[{p_name}] Evento {event_name} en {pid} !' + local_time(counter))
    return counter
    
def send_message(pipe, pid, counter, event_name="", p_name=""):
    counter += 1
    pipe.send(('Mensaje', counter))
    print(f'[{p_name}] Evento {event_name} (Mensaje enviado) desde proceso {pid}' + local_time(counter))
    return counter

def recv_message(pipe, pid, counter, event_name="", p_name=""): 
    message, timestamp = pipe.recv()
    counter = calc_recv_timestamp(timestamp, counter)
    print(f'[{p_name}] Evento {event_name} (Mensaje recibido) en proceso {pid}' + local_time(counter))
    return counter
	
def process_one(pipe_send_p2, pipe_recv_p3):
    pid = getpid()
    counter = 0
    p = "P1"
    
    counter = event(pid, counter, 'e1_1', p)
    time.sleep(0.1) # Pequeños retardos para asegurar el orden en la consola
    
    # Envia M1 a P2
    counter = send_message(pipe_send_p2, pid, counter, 'e1_2', p)
    time.sleep(0.3)
    
    counter = event(pid, counter, 'e1_3', p)
    
    # Recibe M4 de P3
    counter = recv_message(pipe_recv_p3, pid, counter, 'e1_4', p)


def process_two(pipe_recv_p1, pipe_send_p4):
    pid = getpid()
    counter = 0
    p = "P2"
    
    counter = event(pid, counter, 'e2_1', p)
    
    # Recibe M1 de P1
    counter = recv_message(pipe_recv_p1, pid, counter, 'e2_2', p)
    time.sleep(0.1)
    
    counter = event(pid, counter, 'e2_3', p)
    time.sleep(0.1)
    
    # Envia M2 a P4
    counter = send_message(pipe_send_p4, pid, counter, 'e2_4', p)
    time.sleep(0.1)
    
    counter = event(pid, counter, 'e2_5', p)


def process_three(pipe_recv_p5, pipe_send_p1):
    pid = getpid()
    counter = 0
    p = "P3"
    
    # Recibe M3 de P5
    counter = recv_message(pipe_recv_p5, pid, counter, 'e3_1', p)
    time.sleep(0.1)
    
    counter = event(pid, counter, 'e3_2', p)
    time.sleep(0.1)
    
    # Envia M4 a P1
    counter = send_message(pipe_send_p1, pid, counter, 'e3_3', p)
    time.sleep(0.1)
    
    counter = event(pid, counter, 'e3_4', p)


def process_four(pipe_recv_p2, pipe_send_p5):
    pid = getpid()
    counter = 0
    p = "P4"
    
    counter = event(pid, counter, 'e4_1', p)
    
    # Recibe M2 de P2
    counter = recv_message(pipe_recv_p2, pid, counter, 'e4_2', p)
    time.sleep(0.1)
    
    counter = event(pid, counter, 'e4_3', p)
    time.sleep(0.1)
    
    # Envia M5 a P5
    counter = send_message(pipe_send_p5, pid, counter, 'e4_4', p)
    time.sleep(0.1)
    
    counter = event(pid, counter, 'e4_5', p)


def process_five(pipe_send_p3, pipe_recv_p4):
    pid = getpid()
    counter = 0
    p = "P5"
    
    time.sleep(0.1)
    # Envia M3 a P3
    counter = send_message(pipe_send_p3, pid, counter, 'e5_1', p)
    time.sleep(0.1)
    
    counter = event(pid, counter, 'e5_2', p)
    time.sleep(0.1)
    
    counter = event(pid, counter, 'e5_3', p)
    
    # Recibe M5 de P4
    counter = recv_message(pipe_recv_p4, pid, counter, 'e5_4', p)


if __name__ == '__main__':
    print("==================================================")
    print(" SIMULACIÓN DE RELOJES LÓGICOS DE LAMPORT (5 PROCESOS)")
    print("==================================================\n")

    # Creación de tuberías (pipes) unidireccionales entre los procesos según el diagrama
    # P1 -> P2 (M1)
    pipe_recv_p2, pipe_send_p1 = Pipe(duplex=False) 
    
    # P2 -> P4 (M2)
    pipe_recv_p4, pipe_send_p2 = Pipe(duplex=False)
    
    # P5 -> P3 (M3)
    pipe_recv_p3, pipe_send_p5 = Pipe(duplex=False)
    
    # P3 -> P1 (M4)
    pipe_recv_p1, pipe_send_p3 = Pipe(duplex=False)
    
    # P4 -> P5 (M5)
    pipe_recv_p5, pipe_send_p4 = Pipe(duplex=False)


    p1 = Process(target=process_one, args=(pipe_send_p1, pipe_recv_p1))
    p2 = Process(target=process_two, args=(pipe_recv_p2, pipe_send_p2))
    p3 = Process(target=process_three, args=(pipe_recv_p3, pipe_send_p3))
    p4 = Process(target=process_four, args=(pipe_recv_p4, pipe_send_p4))
    p5 = Process(target=process_five, args=(pipe_send_p5, pipe_recv_p5))

    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
    
    print("\nSimulación finalizada con éxito.")
