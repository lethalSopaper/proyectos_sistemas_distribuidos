# Documentación: Entendiendo el Coordinador gRPC

El archivo `coordinador.py` es el "cliente" en nuestro sistema distribuido. Su trabajo es tomar un mensaje y enviarlo a múltiples servidores (los receptores). Para cumplir con los requisitos de tu proyecto, hace esto de dos formas: **secuencial** (uno por uno) y **concurrente** (todos al mismo tiempo).

A continuación, desglosamos las partes más importantes y "raras" del código.

## 2. Explicación de las funciones clave

*   `contactar_receptor(receptor, mensaje)`: Esta función intenta enviar un mensaje a un *único* receptor. Lo más importante aquí es el `timeout=2.0` y el bloque `try...except`. Si el receptor está apagado (Prueba 2), la conexión fallará tras 2 segundos de espera, el código capturará el error `grpc.RpcError` y devolverá un resultado de "fallo" sin colgar todo el programa.
*   `imprimir_resumen(...)`: Solo formatea e imprime los resultados en pantalla, separando los exitosos de los fallidos y mostrando el tiempo total que tomó la operación.

## 3. ¿Qué es un "futuro" (`futuro`) y la ejecución concurrente?

En la función `ejecutar_difusion_concurrente`, usamos una biblioteca de Python llamada `concurrent.futures`. Aquí es donde aparecen los términos que suenan extraños.

**El problema de la ejecución secuencial:**
En la difusión secuencial, enviamos un mensaje a P1, esperamos a que responda. Luego a P2, esperamos. Si P3 está apagado, esperamos 2 segundos enteros antes de pasar a P4. Es lento.

**La solución concurrente:**
Usamos hilos (threads) para hablar con todos los receptores *al mismo tiempo*.

```python
with futures.ThreadPoolExecutor(max_workers=len(RECEPTORES)) as executor:
    # 1. Se "lanzan" las tareas al mismo tiempo
    futuros = [executor.submit(contactar_receptor, rec, mensaje) for rec in RECEPTORES]
    
    # 2. Se recogen las respuestas conforme van llegando
    for futuro in futures.as_completed(futuros):
        resultados.append(futuro.result())
```

### ¿Qué significa exactamente la variable `futuro`?
Un **`Future`** (Futuro) en programación es como un "ticket" o un "recibo" de una tarea que se está ejecutando en el fondo. 

1.  Cuando usas `executor.submit(...)`, le estás diciendo a Python: *"Oye, encarga a un trabajador (hilo) que envíe este mensaje. No me des la respuesta todavía, dame un recibo (un **futuro**)"*.
2.  Python envía los 5 mensajes casi instantáneamente y te devuelve 5 "futuros" o recibos. En ese momento, la tarea aún se está realizando en la red.
3.  El ciclo `for futuro in futures.as_completed(futuros):` se encarga de ir revisando esos recibos. Cuando la tarea de un recibo termina (ya sea con éxito o error), usamos `futuro.result()` para "canjear" el recibo por la respuesta real que devolvió la función.

Gracias a esto, si P3 está apagado y tarda 2 segundos en dar error, los otros 4 procesos no se quedan esperando; entregan sus resultados inmediatamente mientras el "futuro" de P3 sigue trabajando en el fondo.