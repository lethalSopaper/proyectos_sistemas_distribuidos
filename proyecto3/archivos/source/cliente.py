import grpc
import archivos_pb2
import archivos_pb2_grpc

def mostrar_menu():
    print("\n" + "="*35)
    print("SISTEMA DE ARCHIVOS REMOTOS")
    print("="*35)
    print("1. Crear nuevo archivo")
    print("2. Leer un archivo")
    print("3. Agregar contenido a un archivo")
    print("4. Listar archivos disponibles")
    print("5. Eliminar un archivo")
    print("6. Salir")
    print("="*35)
    return input("Elige una opción (1-6): ")

def iniciar_cliente():
    # Dirección por defecto. Si pruebas en varias computadoras, cambia 'localhost' por la IP del servidor.
    direccion_servidor = 'localhost:50051'
    print(f"Conectando al servidor en {direccion_servidor}...")
    try:
        # Se abre el canal de comunicación con el servidor
        with grpc.insecure_channel(direccion_servidor) as canal:
            stub = archivos_pb2_grpc.ServicioArchivosStub(canal)
            while True:
                opcion = mostrar_menu()
                if opcion == '1':
                    nombre = input("Ingresa el nombre del archivo (ej. notas.txt): ")
                    contenido = input("Escribe el contenido inicial: ")
                    solicitud = archivos_pb2.CrearRequest(nombre_archivo=nombre, contenido=contenido)
                    respuesta = stub.CrearArchivo(solicitud)
                    print(f"\n[Servidor] -> {respuesta.mensaje}")
                elif opcion == '2':
                    nombre = input("Ingresa el nombre del archivo a leer: ")
                    solicitud = archivos_pb2.LeerRequest(nombre_archivo=nombre)
                    respuesta = stub.LeerArchivo(solicitud)
                    print(f"\n[Servidor] -> {respuesta.mensaje}")
                    if respuesta.exito:
                        print("-" * 40)
                        print(respuesta.contenido)
                        print("-" * 40)
                elif opcion == '3':
                    nombre = input("Ingresa el nombre del archivo a modificar: ")
                    contenido = input("Escribe el texto a agregar al final: ")
                    # Añadimos un salto de línea para que no se pegue con el texto anterior
                    contenido_con_salto = "\n" + contenido
                    solicitud = archivos_pb2.AgregarRequest(nombre_archivo=nombre, contenido=contenido_con_salto)
                    respuesta = stub.AgregarContenido(solicitud)
                    print(f"\n[Servidor] -> {respuesta.mensaje}")
                elif opcion == '4':
                    solicitud = archivos_pb2.ListarRequest()
                    respuesta = stub.ListarArchivos(solicitud)
                    print(f"\n[Servidor] -> {respuesta.mensaje}")
                    if respuesta.exito:
                        print("\nArchivos en el directorio remoto:")
                        if respuesta.archivos:
                            for arc in respuesta.archivos:
                                print(f" 📄 {arc}")
                        else:
                            print(" (El directorio está vacío)")
                elif opcion == '5':
                    nombre = input("Ingresa el nombre del archivo a eliminar: ")
                    solicitud = archivos_pb2.EliminarRequest(nombre_archivo=nombre)
                    respuesta = stub.EliminarArchivo(solicitud)
                    print(f"\n[Servidor] -> {respuesta.mensaje}")
                elif opcion == '6':
                    print("\nCerrando conexión. ¡Hasta luego!")
                    break
                else:
                    print("\n Opción no válida. Intenta de nuevo.")

    except grpc.RpcError as e:
        # Esto cumple con la prueba de "Servidor no disponible"
        print(f"\n Error de comunicación: No se pudo conectar al servidor.")
        print("Asegúrate de que 'servidor.py' esté en ejecución.")

if __name__ == '__main__':
    iniciar_cliente()