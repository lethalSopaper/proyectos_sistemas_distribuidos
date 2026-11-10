#Ugartechea Gonzalez Luis Antonio -- 320223822
# Algoritmo de Relojes Vectoriales - 5 Procesos (Actividad 3)
from multiprocessing import Process, Pipe
from os import getpid
import time

def local_time(vector):
    return f' (VECTOR_TIME={vector})'

# Incrementa el reloj local y toma el máximo de los demás
def calc_recv_timestamp(recv_vector, local_vector, p_index):
    local_vector[p_index] += 1
    for i in range(len(local_vector)):
        local_vector[i] = max(local_vector[i], recv_vector[i])
    return local_vector

def event(pid, vector, p_index, event_name="", p_name=""):
    vector[p_index] += 1
    print(f'[{p_name}] Evento {event_name} en {pid} !' + local_time(vector))
    return vector
    
def send_message(pipe, pid, vector, p_index, event_name="", p_name=""):
    vector[p_index] += 1
    # Enviamos una copia del vector para evitar referencias de memoria cruzadas
    pipe.send(('Mensaje', vector.copy()))
    print(f'[{p_name}] Evento {event_name} (Mensaje enviado) desde proceso {pid}' + local_time(vector))
    return vector

def recv_message(pipe, pid, vector, p_index, event_name="", p_name=""): 
    message, recv_vector = pipe.recv()
    vector = calc_recv_timestamp(recv_vector, vector, p_index)
    print(f'[{p_name}] Evento {event_name} (Mensaje recibido) en proceso {pid}' + local_time(vector))
    return vector
	
def process_one(pipe_send_p2, pipe_recv_p3):
    pid = getpid()
    vector = [0, 0, 0, 0, 0] # [P1, P2, P3, P4, P5]
    p_index = 0
    p = "P1"
    
    vector = event(pid, vector, p_index, 'e1_1', p)
    time.sleep(0.1)
    
    # Envia M1 a P2
    vector = send_message(pipe_send_p2, pid, vector, p_index, 'e1_2', p)
    time.sleep(0.3)
    
    vector = event(pid, vector, p_index, 'e1_3', p)
    
    # Recibe M4 de P3
    vector = recv_message(pipe_recv_p3, pid, vector, p_index, 'e1_4', p)


def process_two(pipe_recv_p1, pipe_send_p4):
    pid = getpid()
    vector = [0, 0, 0, 0, 0]
    p_index = 1
    p = "P2"
    
    vector = event(pid, vector, p_index, 'e2_1', p)
    
    # Recibe M1 de P1
    vector = recv_message(pipe_recv_p1, pid, vector, p_index, 'e2_2', p)
    time.sleep(0.1)
    
    vector = event(pid, vector, p_index, 'e2_3', p)
    time.sleep(0.1)
    
    # Envia M2 a P4
    vector = send_message(pipe_send_p4, pid, vector, p_index, 'e2_4', p)
    time.sleep(0.1)
    
    vector = event(pid, vector, p_index, 'e2_5', p)


def process_three(pipe_recv_p5, pipe_send_p1):
    pid = getpid()
    vector = [0, 0, 0, 0, 0]
    p_index = 2
    p = "P3"
    
    # Recibe M3 de P5
    vector = recv_message(pipe_recv_p5, pid, vector, p_index, 'e3_1', p)
    time.sleep(0.1)
    
    vector = event(pid, vector, p_index, 'e3_2', p)
    time.sleep(0.1)
    
    # Envia M4 a P1
    vector = send_message(pipe_send_p1, pid, vector, p_index, 'e3_3', p)
    time.sleep(0.1)
    
    vector = event(pid, vector, p_index, 'e3_4', p)


def process_four(pipe_recv_p2, pipe_send_p5):
    pid = getpid()
    vector = [0, 0, 0, 0, 0]
    p_index = 3
    p = "P4"
    
    vector = event(pid, vector, p_index, 'e4_1', p)
    
    # Recibe M2 de P2
    vector = recv_message(pipe_recv_p2, pid, vector, p_index, 'e4_2', p)
    time.sleep(0.1)
    
    vector = event(pid, vector, p_index, 'e4_3', p)
    time.sleep(0.1)
    
    # Envia M5 a P5
    vector = send_message(pipe_send_p5, pid, vector, p_index, 'e4_4', p)
    time.sleep(0.1)
    
    vector = event(pid, vector, p_index, 'e4_5', p)


def process_five(pipe_send_p3, pipe_recv_p4):
    pid = getpid()
    vector = [0, 0, 0, 0, 0]
    p_index = 4
    p = "P5"
    
    time.sleep(0.1)
    # Envia M3 a P3
    vector = send_message(pipe_send_p3, pid, vector, p_index, 'e5_1', p)
    time.sleep(0.1)
    
    vector = event(pid, vector, p_index, 'e5_2', p)
    time.sleep(0.1)
    
    vector = event(pid, vector, p_index, 'e5_3', p)
    
    # Recibe M5 de P4
    vector = recv_message(pipe_recv_p4, pid, vector, p_index, 'e5_4', p)


if __name__ == '__main__':
    print("==================================================")
    print(" SIMULACIÓN DE RELOJES VECTORIALES (5 PROCESOS)")
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
