# Proyecto 1: Caso de estudio - Interfaz de paso de mensajes y Cluster HPC

## Información general

- Materia: Sistemas Distribuidos
- Profesora: Elba Karen Sáenz García
- Tipo de proyecto: Caso de estudio con MPI y clúster HPC
- Número de integrantes: 4 personas por equipo
- Fecha de entrega: 16 de marzo de 2026

## Objetivo

Construir un sistema distribuido de cómputo de alto rendimiento (HPC) y ejecutar programas paralelos que distribuyan el trabajo entre los nodos del clúster. El proyecto busca demostrar la ejecución de tareas en múltiples procesos y máquinas, así como la aplicación de la interfaz de paso de mensajes MPI para resolver problemas distribuidos.

---

## 1. Construcción de un mini clúster HPC

Se debe construir un mini clúster de cómputo de alto rendimiento utilizando máquinas virtuales y la distribución PelicanHPC. La finalidad es mostrar que un problema puede dividirse y ejecutarse en diferentes procesos que corren en nodos distintos del clúster.

### Requisitos

- Utilizar máquinas virtuales para simular un clúster HPC.
- Emplear PelicanHPC como distribución base.
- Demostrar la ejecución distribuida de un programa paralelo.
- Mostrar mínimo 6 procesos activos durante la ejecución.
- Todos los integrantes del equipo deben participar en el video.

### Ejemplo requerido

El ejemplo a ejecutar debe cumplir lo siguiente:

- El proceso 0 envía un arreglo de flotantes de 5 elementos a otros cinco procesos.
- Cada proceso receptor imprime:
  - el arreglo recibido,
  - el nombre de la máquina o nodo,
  - su identificador de proceso.

### Evidencia requerida

- Video de la puesta en marcha del clúster.
- Video de la ejecución del ejemplo distribuido.
- Capturas de pantalla que muestren la ejecución y la fecha.

---

## 2. Resolución de problemas utilizando MPI

Se deben desarrollar programas con MPI para resolver los ejercicios descritos a continuación. Además del código fuente, se debe entregar documentación que explique la implementación y muestre capturas de pantalla con la fecha visible.

### a) Paso de matrices entre procesos

Implementar un programa que realice el paso de dos arreglos de n elementos, uno de enteros y otro de flotantes, utilizando n procesos, tal como se indica en la figura proporcionada en el enunciado.

#### Reglas del programa

- Cada proceso recibe los arreglos A y B.
- Cada vez que un proceso recibe los arreglos, debe agregar un elemento a cada arreglo.
- Debe mostrar en pantalla el arreglo actualizado junto con el identificador del proceso.
- El proceso 0 debe imprimir los arreglos A y B con sus valores iniciales.
- El proceso 0 debe mostrar el resultado final obtenido después de que los arreglos pasen por todos los procesos.

#### Salida esperada

- Los arreglos iniciales.
- Los arreglos después de cada paso entre procesos.
- El estado final de los arreglos una vez que regresan al proceso 0.

### b) Determinación del renglón con la suma mayor o menor de una matriz

Se tiene una matriz A de tamaño N x M con números enteros. Se debe desarrollar un programa distribuido con MPI para determinar qué renglón tiene la mayor suma de sus elementos.

> Nota: el documento presenta una redacción inconsistente en la parte final, donde se menciona también la "menor suma". Es recomendable confirmar con la profesora cuál es la condición correcta antes de entregar el proyecto.

#### Requerimientos

- La matriz A debe generarse o inicializarse en el proceso 0.
- La matriz debe distribuirse entre los procesos mediante comunicaciones colectivas de MPI.
- Cada proceso debe analizar la parte de la matriz que le corresponde.
- Cada proceso debe calcular la suma de los elementos de los renglones asignados.
- Cada proceso debe informar al proceso 0 la suma o el resultado local.
- El proceso 0 debe imprimir:
  - la matriz inicial,
  - el renglón con la suma relevante,
  - la suma correspondiente.

#### Restricciones

- Suponer que N es divisible entre el número de procesos.
- Usar mínimo 4 procesos.

---

## 3. Entregables esperados

El proyecto debe entregarse con los siguientes elementos:

1. Código fuente de los programas MPI.
2. Explicación breve de la implementación.
3. Capturas de pantalla de la ejecución con fecha visible.
4. Documento de reporte con estructura clara.
5. Video o enlace para revisarlo y poder descargarlo.
6. Tabla con la participación de cada integrante del equipo.

---

## 4. Requisitos del documento final

El reporte debe incluir una buena organización y calidad académica. Se recomienda:

- Títulos y subtítulos bien definidos.
- Redacción clara y correcta.
- Uso de fuente Georgia 11.
- Interlineado 1.5.
- Referencias bibliográficas o de apoyo.
- Tabla de participación de los integrantes.
- Ortografía y gramática correctas.

---

## 5. Criterios de evaluación

| Concepto | Puntos |
|---|---:|
| Desarrollo del clúster y video de construcción | 3.5 |
| Funcionamiento correcto de los programas distribuidos | 3.5 |
| Documentación del desarrollo y explicación del funcionamiento | 2 |
| Calidad del reporte y presentación | 1 |
| Total | 10 |

### Criterios adicionales

- El clúster debe funcionar con al menos un servidor y dos clientes.
- Se debe mostrar en pantalla qué máquina y proceso está trabajando.
- Los programas deben ejecutarse de forma correcta en ambientes distribuidos.
- La documentación debe justificar el uso de las funciones empleadas y solo usar funciones vistas en clase.

---

## 6. Estructura sugerida del repositorio

```text
proyecto/
├── README.md
├── codigo/
│   ├── mpi_matrices.c
│   ├── mpi_matriz_suma.c
│   └── ...
├── documentacion/
│   ├── reporte.pdf
│   └── capturas/
├── video/
│   └── cluster_hpc.mp4
└── referencias/
    └── bibliografia.md
```

---

## 7. Resumen ejecutivo

Este proyecto combina dos aspectos fundamentales de los sistemas distribuidos: la construcción de un clúster HPC y la resolución de problemas mediante MPI. A través de la ejecución simultánea de procesos en diferentes nodos, se busca demostrar cómo los cálculos pueden repartirse para mejorar el rendimiento y la escalabilidad. El trabajo final debe mostrar tanto la parte práctica del clúster como la parte algorítmica del procesamiento distribuido.

---

## 8. Notas para el equipo

- Definir roles dentro del equipo desde el inicio.
- Documentar cada etapa de la instalación y configuración del clúster.
- Probar cada programa MPI por separado antes de integrarlos al reporte.
- Mantener evidencia visual con fechas para todas las ejecuciones.
- Confirmar la interpretación correcta del problema de la matriz antes de la entrega final.

Este README sirve como base para documentar el desarrollo del proyecto, la implementación de MPI y la evidencia del clúster HPC.
