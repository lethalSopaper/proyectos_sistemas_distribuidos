# Configuración del Entorno Virtual e Instalación de Dependencias

Para garantizar que el proyecto se ejecute de manera aislada y sin conflictos con otras bibliotecas del sistema, utilizaremos un entorno virtual de Python. A continuación, se detallan los pasos para prepararlo.

## 1. Creación del entorno virtual

Abre una terminal, navega hasta la carpeta raíz de tu proyecto y ejecuta el siguiente comando para crear un entorno virtual llamado `.venv`:

```
python3 -m venv .venv

```

## 2. Activación del entorno virtual

Antes de instalar dependencias o ejecutar el código, debes activar el entorno virtual. El comando varía dependiendo de tu sistema operativo:

**En Linux (ej. Fedora, Ubuntu) o macOS:**

```
source .venv/bin/activate

```

**En Windows (Símbolo del sistema / PowerShell):**

```
.venv\Scripts\activate

```

*Nota: Sabrás que el entorno está activo porque el prompt de tu terminal mostrará el nombre del entorno, por ejemplo: `(.venv) [usuario@host proyecto]$`.*

## 3. Instalación de dependencias

El proyecto requiere las bibliotecas oficiales de gRPC para Python. Con el entorno virtual activo, actualiza `pip` (recomendado) e instala los paquetes necesarios:

```
python3 -m pip install --upgrade pip
python3 -m pip install grpcio grpcio-tools

```

* `grpcio`: Contiene el núcleo de la biblioteca gRPC para que el cliente y servidor puedan comunicarse.

* `grpcio-tools`: Proporciona el compilador (protoc) necesario para traducir el archivo `.proto` a código Python.

## 4. Verificación de la instalación

Para asegurarte de que gRPC se instaló correctamente, puedes ejecutar el siguiente comando. Si no muestra errores y devuelve la versión, el entorno está listo:

```
python3 -c "import grpc; print(f'gRPC versión: {grpc.__version__}')"

```

## 5. Compilación del archivo Protocol Buffers (.proto)

Una vez instaladas las dependencias, el siguiente paso indispensable antes de ejecutar el código es generar las clases de Python a partir de nuestro archivo de definición de servicios.

Ejecuta el siguiente comando en la raíz del proyecto (donde se encuentra `difusion.proto`):

```
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. difusion.proto

```

Este comando generará automáticamente dos archivos necesarios para el funcionamiento del sistema:

* `difusion_pb2.py` (Clases de los mensajes)

* `difusion_pb2_grpc.py` (Clases del servicio cliente/servidor)

## 6. Ejecución del Sistema

El sistema utiliza un modelo de comunicación donde los **receptores actúan como servidores** esperando peticiones, y el **coordinador actúa como cliente** enviando los mensajes. Es indispensable iniciar los receptores antes que el coordinador.

### 6.1 Ejecución en Local (Localhost)

Esta modalidad es ideal para realizar pruebas rápidas en una sola computadora.

**Paso 1: Iniciar los procesos receptores**
Abre 5 terminales distintas (activa el entorno virtual en cada una) y ejecuta el script proporcionando un **ID** y un **Puerto**:

* **Terminal 1:** `python3 receptor.py P1 50051`

* **Terminal 2:** `python3 receptor.py P2 50052`

* **Terminal 3:** `python3 receptor.py P3 50053`

* **Terminal 4:** `python3 receptor.py P4 50054`

* **Terminal 5:** `python3 receptor.py P5 50055`

**Paso 2: Iniciar el coordinador**
En una sexta terminal, ejecuta el script del coordinador **sin argumentos**. Al no recibir direcciones IP externas desde la línea de comandos, el sistema utilizará la configuración por defecto conectándose a `localhost` en los puertos 50051 a 50055.

```
python3 coordinador.py

```

### 6.2 Ejecución Distribuida (Varias computadoras en red)

Para ejecutar el sistema en un entorno real distribuido, las computadoras deben estar conectadas a la misma red local (LAN o VPN).

**Paso 1: Configurar e iniciar los receptores en las máquinas remotas**

1. En cada computadora receptora, asegúrate de tener el proyecto descargado, el entorno virtual activo y las dependencias instaladas.

2. Averigua la dirección IP local de cada máquina receptora (en distribuciones como Fedora, puedes utilizar el comando `ip a`).

3. Inicia el script del receptor indicando su ID y un puerto disponible. Por ejemplo, en la primera máquina:

   ```
   python3 receptor.py P1 50051
   
   ```

   *(Nota: Si las máquinas tienen un firewall activo como `firewalld` en Fedora, asegúrate de habilitar el tráfico para el puerto especificado. Ej: `sudo firewall-cmd --add-port=50051/tcp`).*

**Paso 2: Iniciar el coordinador dinámico**
En la computadora desde la que emitirás los mensajes (coordinador), ejecuta el script pero **añade las direcciones IP y puertos reales de los receptores** separados por espacios. El coordinador configurará dinámicamente la difusión hacia estas direcciones.

Ejemplo:

```
python3 coordinador.py 192.168.1.100:50051 192.168.1.101:50052 10.0.0.5:50051

```

## 7. Desactivar el entorno virtual

Una vez que termines de trabajar en el proyecto y cierres los procesos (usando `Ctrl+C` en las terminales), puedes salir del entorno virtual simplemente ejecutando:

```
deactivate

```