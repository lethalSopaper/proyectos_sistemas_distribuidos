# Sistema Distribuido con gRPC, Relojes Vectoriales y Docker

Implementación de un sistema distribuido compuesto por **5 procesos independientes (`P1` a `P5`)** ejecutados en contenedores Docker aislados, comunicándose mediante **gRPC (Protocol Buffers)** y manteniendo el orden causal de eventos mediante **relojes vectoriales** y bitácoras persistentes.

---

## 1. Arquitectura y Estructura del Proyecto

Cada contenedor ejecuta simultáneamente un servidor gRPC persistente (con control de concurrencia mediante `threading.Lock` para proteger el reloj vectorial en memoria) y expone una interfaz CLI invocada mediante `docker exec` para detonar eventos internos, envíos punto a punto y difusiones (*broadcast*).

```text
proyecto-distribuido/
├── proto/
│   └── cluster.proto       # Definición de servicios y mensajes gRPC
├── src/
│   ├── server.py           # Servidor gRPC, lógica de relojes vectoriales y bitácoras
│   └── client.py              # Cliente CLI para disparar eventos vía docker exec
├── logs/                   # Bitácoras persistentes (p1.log ... p5.log)
├── Dockerfile              # Construcción de imagen y compilación de .proto
├── compose.yaml            # Orquestación de los 5 contenedores y red bridge
├── requirements.txt        # Dependencias Python (grpcio, grpcio-tools)
└── README.md               # Guía de ejecución y pruebas
```

### Reglas de Actualización de Relojes Vectoriales
Cada proceso $P_i$ ($i \in \{1..5\}$) inicia con el vector $[0, 0, 0, 0, 0]$:
1. **Evento interno (`[INTERNAL]`):** $V_i[i] \leftarrow V_i[i] + 1$
2. **Envío de mensaje (`[SEND]`):** $V_i[i] \leftarrow V_i[i] + 1$, y se adjunta $V_i$ al mensaje.
3. **Recepción de mensaje (`[RECEIVE]`):**
   $$V_i[k] \leftarrow \max(V_i[k], V_{\text{recibido}}[k]) \quad \forall k \in \{1..5\}$$
   $$V_i[i] \leftarrow V_i[i] + 1$$
4. **Difusión (`[BROADCAST]`):** Ejecuta el envío secuencial hacia los otros cuatro nodos incrementando su componente local en cada emisión registrada.

---

## 2. Requisitos Previos

* **Docker Engine** (v20.10+) y **Docker Compose** (v2.0+) instalados y en ejecución.
* Puerto interno `50051` disponible dentro de la red virtual de Docker (`dist_net`).

---

## 3. Construcción e Inicio del Clúster

1. **Limpiar bitácoras anteriores (opcional, recomendado antes de una corrida limpia):**
   ```bash
   mkdir -p logs && rm -f logs/*.log
   ```

2. **Construir las imágenes y levantar los 5 contenedores en segundo plano:**
   ```bash
   docker compose up --build -d
   ```

3. **Verificar que los 5 procesos (`p1` a `p5`) estén activos:**
   ```bash
   docker compose ps
   ```
   *Resultado esperado:* Los 5 servicios (`p1`, `p2`, `p3`, `p4`, `p5`) deben aparecer en estado `Up`.

4. **Verificar que los servidores gRPC estén escuchando (opcional):**
   ```bash
   docker compose logs
   ```

---

## 4. Ejecución de Pruebas mediante `docker exec`

A continuación se presenta una secuencia completa de pruebas que ejercita **todos los servicios requeridos** (tareas internas, mensajes punto a punto, difusión global y concurrencia) involucrando a los **5 procesos**.

### Fase 1: Inicialización y flujo causal principal (`P1` $\rightarrow$ `P3` $\rightarrow$ `P4`)
```bash
# 1. P1 ejecuta un evento interno -> P1: [1,0,0,0,0]
docker exec p1 python src/client.py local "iniciar_transaccion"

# 2. P1 envía solicitud a P3 -> P1: [2,0,0,0,0] | P3: [2,0,1,0,0]
docker exec p1 python src/client.py send P3 "solicitud_validacion"

# 3. P3 ejecuta una tarea local -> P3: [2,0,2,0,0]
docker exec p3 python src/client.py local "procesar_validacion"

# 4. P3 envía el resultado a P4 -> P3: [2,0,3,0,0] | P4: [2,0,3,1,0]
docker exec p3 python src/client.py send P4 "resultado_aprobado"
```

### Fase 2: Eventos concurrentes en `P2` y `P5`
```bash
# 5. P2 ejecuta tarea local de forma concurrente -> P2: [0,1,0,0,0]
docker exec p2 python src/client.py local "auditoria_previa"

# 6. P2 envía reporte a P5 -> P2: [0,2,0,0,0] | P5: [0,2,0,0,1]
docker exec p2 python src/client.py send P5 "reporte_auditoria"

# 7. P5 ejecuta tarea local -> P5: [0,2,0,0,2]
docker exec p5 python src/client.py local "registrar_auditoria"
```

### Fase 3: Difusión global (*Broadcast*) desde `P4`
```bash
# 8. P4 difunde confirmación global a P1, P2, P3 y P5
docker exec p4 python src/client.py broadcast "commit_global"
```
*Efecto en relojes tras el broadcast de `P4` (que parte de `[2,0,3,1,0]` y emite 4 envíos incrementando su posición `P4` a `2`, `3`, `4` y `5`):*
* `P1` recibe `[2,0,3,2,0]` $\rightarrow$ actualiza a **`[3,0,3,2,0]`**
* `P2` recibe `[2,0,3,3,0]` $\rightarrow$ actualiza a **`[2,3,3,3,0]`**
* `P3` recibe `[2,0,3,4,0]` $\rightarrow$ actualiza a **`[2,0,4,4,0]`**
* `P5` recibe `[2,0,3,5,0]` $\rightarrow$ actualiza a **`[2,2,3,5,3]`**

### Fase 4: Cierre y verificación final entre nodos
```bash
# 9. P5 confirma cierre hacia P1 -> P5: [2,2,3,5,4] | P1: [4,2,3,5,4]
docker exec p5 python src/client.py send P1 "ack_final_sistema"
```

---

## 5. Inspección de Bitácoras y Evidencias

Las bitácoras se almacenan en tiempo real dentro del directorio local `./logs/` gracias al volumen montado en `compose.yaml`.

* **Ver todas las bitácoras juntas:**
  ```bash
  head -n 50 logs/p*.log
  ```

* **Ver la bitácora de un proceso específico (ejemplo `P3`):**
  ```bash
  cat logs/p3.log
  ```

* **Formato de salida esperado en bitácoras:**
  ```text
  [INTERNAL] P1 tarea="iniciar_transaccion" vector=[1,0,0,0,0]
  [SEND] P1 -> P3 msg="solicitud_validacion" vector=[2,0,0,0,0]
  [RECEIVE] P3 <- P1 msg="solicitud_validacion" recibido=[2,0,0,0,0] actualizado=[2,0,1,0,0]
  [ACK] P1 <- P3 estado="OK" vector_remoto=[2,0,1,0,0]
  ```

---

## 6. Detención y Limpieza del Entorno

1. **Detener y eliminar los contenedores y la red virtual:**
   ```bash
   docker compose down
   ```

2. **Eliminar también imágenes generadas y volúmenes huérfanos (limpieza total):**
   ```bash
   docker compose down --rmi local -v
   ```

---

## 7. Checklist de Entregables del Proyecto

- [ ] **Código fuente:** `proto/cluster.proto`, `src/server.py`, `src/client.py`.
- [ ] **Infraestructura Docker:** `Dockerfile`, `compose.yaml`, `requirements.txt`.
- [ ] **Diagrama espacio-tiempo:** Representación visual de los 5 procesos (`P1`–`P5`) con los vectores en cada evento interno, envío, recepción y broadcast.
- [ ] **Documento técnico:** Descripción de arquitectura, explicación matemática de las actualizaciones vectoriales, evidencias de bitácoras, referencias en formato **APA** y declaración de uso de IA.
- [ ] **Video demostrativo:** Ejecución en vivo con `docker compose` y `docker exec`, revisión de `logs/*.log` y explicación causal de cada integrante.