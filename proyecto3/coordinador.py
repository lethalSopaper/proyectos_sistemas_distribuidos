import sys
import grpc
import time
from concurrent import futures
import difusion_pb2
import difusion_pb2_grpc

# --- CONFIGURACIÓN DINÁMICA DE RECEPTORES ---
RECEPTORES = []

# Obtenemos los argumentos escritos en la terminal (omitiendo el nombre del script)
direcciones_ingresadas = sys.argv[1:]

if len(direcciones_ingresadas) > 0:
    # Si el usuario proporcionó IPs al ejecutar, las asignamos dinámicamente
    for i, direccion in enumerate(direcciones_ingresadas, start=1):
        RECEPTORES.append({"id": f"P{i}", "direccion": direccion})
else:
    # Fallback: Si se ejecuta sin argumentos, usamos localhost para pruebas rápidas
    print("⚠️ Aviso: No se detectaron IPs externas. Usando localhost por defecto...\n")
    RECEPTORES = [
        {"id": "P1", "direccion": "localhost:50051"},
        {"id": "P2", "direccion": "localhost:50052"},
        {"id": "P3", "direccion": "localhost:50053"},
        {"id": "P4", "direccion": "localhost:50054"},
        {"id": "P5", "direccion": "localhost:50055"},
    ]
# --------------------------------------------

# ... (el resto de tus funciones contactar_receptor, imprimir_resumen, etc. se quedan exactamente igual)

def contactar_receptor(receptor, mensaje):
    """Intenta enviar el mensaje a un receptor específico manejando errores de conexión."""
    try:
        with grpc.insecure_channel(receptor["direccion"]) as canal:
            cliente = difusion_pb2_grpc.ServicioDifusionStub(canal)
            # El timeout de 2 segundos evita que el programa se detenga si un nodo cae
            respuesta = cliente.RecibirMensaje(mensaje, timeout=2.0)
            return {"id": receptor["id"], "exito": True, "datos": respuesta}
    except grpc.RpcError as e:
        return {"id": receptor["id"], "exito": False, "error": e.code().name}

def imprimir_resumen(resultados, tiempo_ejecucion, tipo_difusion):
    """Muestra el resumen de respuestas e identifica a los procesos caídos."""
    exitosos = [r for r in resultados if r["exito"]]
    fallidos = [r for r in resultados if not r["exito"]]
    print(f"\n--- Resumen de Difusión {tipo_difusion} ---")
    print(f"Tiempo total: {tiempo_ejecucion:.4f} segundos")
    print(f"Confirmaciones: {len(exitosos)} de {len(RECEPTORES)}")
    for exito in exitosos:
        print(f" [OK] {exito['id']}: {exito['datos'].detalle}")
    if fallidos:
        print("\nProcesos que NO respondieron:")
        for fallo in fallidos:
            print(f" [FALLO] {fallo['id']}: Error de comunicación ({fallo['error']})")
    print("-" * 40)

def ejecutar_difusion_secuencial(emisor, texto):
    print(f"\nIniciando difusión SECUENCIAL del mensaje: '{texto}'")
    mensaje = difusion_pb2.Mensaje(emisor_id=emisor, contenido=texto)
    resultados = []
    inicio = time.time()
    for receptor in RECEPTORES:
        resultados.append(contactar_receptor(receptor, mensaje))
    fin = time.time()
    imprimir_resumen(resultados, fin - inicio, "SECUENCIAL")

def ejecutar_difusion_concurrente(emisor, texto):
    print(f"\nIniciando difusión CONCURRENTE del mensaje: '{texto}'")
    mensaje = difusion_pb2.Mensaje(emisor_id=emisor, contenido=texto)
    resultados = []
    inicio = time.time()
    # Usamos ThreadPoolExecutor para lanzar múltiples llamadas RPC en paralelo
    with futures.ThreadPoolExecutor(max_workers=len(RECEPTORES)) as executor:
        tickets = [executor.submit(contactar_receptor, rec, mensaje) for rec in RECEPTORES]
        for ticket in futures.as_completed(tickets):
            resultados.append(ticket.result())
    fin = time.time()
    # Ordenar resultados por ID para que la salida sea legible
    resultados.sort(key=lambda x: x["id"])
    imprimir_resumen(resultados, fin - inicio, "CONCURRENTE")

if __name__ == "__main__":
    print("=== SISTEMA DE DIFUSIÓN gRPC ===")
    while True:
        print("Que tipo de mensaje deseas difundir primero? (Secuencial[0], Concurrente[1]) o 'salir' para terminar:")
        tipo_difusion = input("Tu elección: ")
        if tipo_difusion == "salir":
            break
        # Prueba 1: Difusión secuencial con mensaje del usuario
        if tipo_difusion == "0":
            texto_secuencial = input("\nEscribe el mensaje a difundir (Secuencial): ")
            ejecutar_difusion_secuencial("Coordinador", texto_secuencial)
            time.sleep(1) # Pequeña pausa visual
        # Prueba 2: Difusión concurrente con un mensaje distinto del usuario
        elif tipo_difusion == "1":
            texto_concurrente = input("\nEscribe el mensaje a difundir (Concurrente): ")
            ejecutar_difusion_concurrente("Coordinador", texto_concurrente)