import grpc
import os
from concurrent import futures
import archivos_pb2
import archivos_pb2_grpc

# Directorio de trabajo exclusivo para el servidor
DIRECTORIO_ALMACEN = "almacen_remoto"

class ServicioArchivos(archivos_pb2_grpc.ServicioArchivosServicer):
    def __init__(self):
        # Crear la carpeta de almacenamiento si no existe al arrancar
        if not os.path.exists(DIRECTORIO_ALMACEN):
            os.makedirs(DIRECTORIO_ALMACEN)
            print(f"Carpeta '{DIRECTORIO_ALMACEN}' creada.")

    def _validar_seguridad(self, nombre_archivo):
        """
        Valida que el nombre del archivo sea seguro y evita ataques de Path Traversal.
        Retorna la ruta completa y segura si es válido, de lo contrario retorna None.
        """
        # Prevenir que envíen rutas como "../etc/passwd" o "carpeta/archivo.txt"
        if ".." in nombre_archivo or "/" in nombre_archivo or "\\" in nombre_archivo:
            return None
        # Construir la ruta absoluta segura
        return os.path.join(DIRECTORIO_ALMACEN, nombre_archivo)

    def CrearArchivo(self, request, context):
        ruta_segura = self._validar_seguridad(request.nombre_archivo)
        if not ruta_segura:
            return archivos_pb2.CrearResponse(
                exito=False,
                mensaje="Error de seguridad: Nombre de archivo inválido o intento de acceso no autorizado."
            )
        if os.path.exists(ruta_segura):
            return archivos_pb2.CrearResponse(
                exito=False,
                mensaje=f"Error: El archivo '{request.nombre_archivo}' ya existe."
            )
        try:
            with open(ruta_segura, 'w', encoding='utf-8') as f:
                f.write(request.contenido)
            return archivos_pb2.CrearResponse(
                exito=True,
                mensaje=f"Archivo '{request.nombre_archivo}' creado exitosamente."
            )
        except Exception as e:
            return archivos_pb2.CrearResponse(exito=False, mensaje=str(e))

    def LeerArchivo(self, request, context):
        ruta_segura = self._validar_seguridad(request.nombre_archivo)
        if not ruta_segura:
            return archivos_pb2.LeerResponse(
                exito=False,
                mensaje="Error de seguridad: Nombre de archivo inválido.",
                contenido=""
            )
        if not os.path.exists(ruta_segura):
            return archivos_pb2.LeerResponse(
                exito=False,
                mensaje=f"Error: El archivo '{request.nombre_archivo}' no existe.",
                contenido=""
            )
        try:
            with open(ruta_segura, 'r', encoding='utf-8') as f:
                contenido = f.read()
            return archivos_pb2.LeerResponse(
                exito=True,
                mensaje="Lectura exitosa.",
                contenido=contenido
            )
        except Exception as e:
            return archivos_pb2.LeerResponse(exito=False, mensaje=str(e), contenido="")

    def AgregarContenido(self, request, context):
        ruta_segura = self._validar_seguridad(request.nombre_archivo)
        if not ruta_segura:
            return archivos_pb2.AgregarResponse(
                exito=False,
                mensaje="Error de seguridad: Nombre de archivo inválido."
            )
        if not os.path.exists(ruta_segura):
            return archivos_pb2.AgregarResponse(
                exito=False,
                mensaje=f"Error: El archivo '{request.nombre_archivo}' no existe. No se puede agregar contenido."
            )
        try:
            # Modo 'a' (append) para agregar al final sin sobrescribir
            with open(ruta_segura, 'a', encoding='utf-8') as f:
                f.write(request.contenido)
            return archivos_pb2.AgregarResponse(
                exito=True,
                mensaje=f"Contenido agregado exitosamente a '{request.nombre_archivo}'."
            )
        except Exception as e:
            return archivos_pb2.AgregarResponse(exito=False, mensaje=str(e))

    def ListarArchivos(self, request, context):
        try:
            # os.listdir devuelve una lista de los nombres de los archivos en la carpeta
            archivos = os.listdir(DIRECTORIO_ALMACEN)
            return archivos_pb2.ListarResponse(
                exito=True,
                mensaje="Listado generado exitosamente.",
                archivos=archivos
            )
        except Exception as e:
            return archivos_pb2.ListarResponse(exito=False, mensaje=str(e), archivos=[])

    def EliminarArchivo(self, request, context):
        ruta_segura = self._validar_seguridad(request.nombre_archivo)
        if not ruta_segura:
            return archivos_pb2.EliminarResponse(
                exito=False,
                mensaje="Error de seguridad: Nombre de archivo inválido."
            )
        if not os.path.exists(ruta_segura):
            return archivos_pb2.EliminarResponse(
                exito=False,
                mensaje=f"Error: El archivo '{request.nombre_archivo}' no existe."
            )
        try:
            os.remove(ruta_segura)
            return archivos_pb2.EliminarResponse(
                exito=True,
                mensaje=f"Archivo '{request.nombre_archivo}' eliminado exitosamente."
            )
        except Exception as e:
            return archivos_pb2.EliminarResponse(exito=False, mensaje=str(e))

def iniciar_servidor(puerto=50051):
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicio = ServicioArchivos()
    archivos_pb2_grpc.add_ServicioArchivosServicer_to_server(servicio, servidor)
    servidor.add_insecure_port(f"[::]:{puerto}")
    servidor.start()
    print(f"Servidor de archivos activo.")
    print(f"Directorio de trabajo: ./{DIRECTORIO_ALMACEN}")
    print(f"Escuchando en el puerto {puerto}...")
    servidor.wait_for_termination()

if __name__ == '__main__':
    iniciar_servidor()
