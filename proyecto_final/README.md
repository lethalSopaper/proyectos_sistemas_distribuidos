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
│   └── client.py           # Cliente CLI para disparar eventos vía docker exec
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

1. **Limpiar bitácoras anteriores (recomendado antes de iniciar una simulación limpia):**
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

## 4. Escenario y Flujo de Trabajo Propuesto (`docker exec`)

**Escenario:** *Pipeline Distribuido de Respaldo y Replicación de Datos*.  
El nodo coordinador de almacenamiento (`P2`) recibe una solicitud de respaldo, delega la fragmentación a `P1`, mientras en paralelo `P4` y `P3` verifican cuotas de disco. Posteriormente, `P5` consolida las réplicas y emite una difusión global (`broadcast`) de sincronización al clúster.

### Fase 1: Recepción y fragmentación (`P2` $\rightarrow$ `P1` $\rightarrow$ `P5`)
```bash
# 1. P2 ejecuta verificación inicial del lote -> P2: [0,1,0,0,0]
docker exec p2 python src/client.py local "verificar_lote_datos"

# 2. P2 envía bloque a P1 para fragmentación -> P2: [0,2,0,0,0] | P1: [1,2,0,0,0]
docker exec p2 python src/client.py send P1 "fragmentar_bloque"

# 3. P1 procesa localmente los fragmentos -> P1: [2,2,0,0,0]
docker exec p1 python src/client.py local "calcular_checksums"

# 4. P1 envía fragmentos listos al nodo de respaldo P5 -> P1: [3,2,0,0,0] | P5: [3,2,0,0,1]
docker exec p1 python src/client.py send P5 "fragmentos_verificados"
```

### Fase 2: Monitoreo concurrente de almacenamiento (`P4` y `P3`)
De manera independiente (concurrente con la Fase 1), `P4` evalúa el espacio disponible y notifica a `P3` antes de enlazar con `P5`:
```bash
# 5. P4 ejecuta diagnóstico local de cuotas -> P4: [0,0,0,1,0]
docker exec p4 python src/client.py local "medir_espacio_disco"

# 6. P4 envía métricas a P3 -> P4: [0,0,0,2,0] | P3: [0,0,1,2,0]
docker exec p4 python src/client.py send P3 "metricas_almacenamiento"

# 7. P3 valida políticas y reenvía autorización a P5 -> P3: [0,0,2,2,0] | P5: [3,2,2,2,2]
docker exec p3 python src/client.py send P5 "cuota_autorizada"
```
*(Nota causal: Al recibir el mensaje de `P3` con vector `[0,0,2,2,0]`, `P5` fusiona su conocimiento previo `[3,2,0,0,1]` mediante $\max$ componente a componente obteniendo `[3,2,2,2,1]` e incrementa su índice local a **`[3,2,2,2,2]`**).*

### Fase 3: Consolidación y Difusión Global (*Broadcast*) desde `P5`
```bash
# 8. P5 ejecuta escritura local de réplica -> P5: [3,2,2,2,3]
docker exec p5 python src/client.py local "consolidar_replica"

# 9. P5 difunde estado de sincronización a P1, P2, P3 y P4
docker exec p5 python src/client.py broadcast "replica_sincronizada"
```
*Efecto en relojes tras el broadcast de `P5` (que parte de `[3,2,2,2,3]` y emite 4 envíos incrementando su posición `P5` a `4`, `5`, `6` y `7`):*
* `P1` (tenía `[3,2,0,0,0]`) recibe `[3,2,2,2,4]` $\rightarrow$ actualiza a **`[4,2,2,2,4]`**
* `P2` (tenía `[0,2,0,0,0]`) recibe `[3,2,2,2,5]` $\rightarrow$ actualiza a **`[3,3,2,2,5]`**
* `P3` (tenía `[0,0,2,2,0]`) recibe `[3,2,2,2,6]` $\rightarrow$ actualiza a **`[3,2,3,2,6]`**
* `P4` (tenía `[0,0,0,2,0]`) recibe `[3,2,2,2,7]` $\rightarrow$ actualiza a **`[3,2,2,3,7]`**

### Fase 4: Auditoría final y cierre (`P3` $\rightarrow$ `P2`)
```bash
# 10. P3 registra auditoría final y confirma cierre al coordinador P2
# P3: [3,2,4,2,6] -> [3,2,5,2,6] | P2: [3,4,5,2,6]
docker exec p3 python src/client.py local "registrar_auditoria_final"
docker exec p3 python src/client.py send P2 "respaldo_completado"
```

---

## 5. Inspección de Bitácoras y Evidencias

Las bitácoras se almacenan en tiempo real dentro del directorio local `./logs/` gracias al volumen montado en `compose.yaml`.

* **Ver todas las bitácoras juntas:**
  ```bash
  head -n 50 logs/p*.log
  ```

* **Ver la bitácora de un proceso específico (ejemplo `P5`):**
  ```bash
  cat logs/p5.log
  ```

* **Ejemplo de salida esperada en `logs/p5.log`:**
  ```text
  [RECEIVE] P5 <- P1 msg="fragmentos_verificados" recibido=[3,2,0,0,0] actualizado=[3,2,0,0,1]
  [RECEIVE] P5 <- P3 msg="cuota_autorizada" recibido=[0,0,2,2,0] actualizado=[3,2,2,2,2]
  [INTERNAL] P5 tarea="consolidar_replica" vector=[3,2,2,2,3]
  [BROADCAST] P5 -> TODOS msg="replica_sincronizada"
  [SEND] P5 -> P1 msg="replica_sincronizada" vector=[3,2,2,2,4]
  [ACK] P5 <- P1 estado="OK" vector_remoto=[4,2,2,2,4]
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