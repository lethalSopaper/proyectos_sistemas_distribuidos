import grpc
import sys
from concurrent import futures
import difusion_pb2
import difusion_pb2_grpc

class ServicioDifusion(difusion_pb2_grpc.ServicioDifusionServicer):
    def __init__(self, receptor_id):
        self.receptor_id = receptor_id

    # Procedimiento remoto que se ejecuta cuando el coordinador llama
    def RecibirMensaje(self, request, context):
        print(f"\n[{self.receptor_id}] Mensaje entrante de {request.emisor_id}:")
        print(f" -> Contenido: {request.contenido}")
        # Devuelve la confirmación requerida
        return difusion_pb2.Confirmacion(
            receptor_id=self.receptor_id,
            recibido=True,
            detalle=f"El nodo {self.receptor_id} procesó el mensaje exitosamente."
        )

def iniciar_receptor(receptor_id, puerto):
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    servicio = ServicioDifusion(receptor_id)
    difusion_pb2_grpc.add_ServicioDifusionServicer_to_server(servicio, servidor)
    servidor.add_insecure_port(f"[::]:{puerto}")
    servidor.start()
    print(f"Receptor {receptor_id} activo y escuchando en el puerto {puerto}...")
    servidor.wait_for_termination()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python receptor.py <ID_NODO> <PUERTO>")
        sys.exit(1)
    id_nodo = sys.argv[1]
    puerto_nodo = sys.argv[2]
    iniciar_receptor(id_nodo, puerto_nodo)