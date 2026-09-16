#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <mpi.h>

#define NELEMENTS 5 // Tamaño inicial dictado por el proyecto

int main(int argc, char **argv) {
    int id, np;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &id);
    MPI_Comm_size(MPI_COMM_WORLD, &np);
    MPI_Status status;
    // Declaramos los punteros fuera de los 'if' para que todos los procesos los conozcan
    int *A = NULL;
    float *B = NULL;

    if (id == 0) {
        srand(time(NULL));
        // El proceso 0 inicializa con 5 elementos
        A = (int*)malloc(NELEMENTS * sizeof(int));
        B = (float*)malloc(NELEMENTS * sizeof(float));

        printf("Proceso %d: Arreglo A inicial: ", id);
        for (int i = 0; i < NELEMENTS; i++) {
            A[i] = rand() % 50;
            printf("%d ", A[i]);
        }
        printf("\n");

        printf("Proceso %d: Arreglo B inicial: ", id);
        for (int i = 0; i < NELEMENTS; i++) {
            B[i] = (float)(rand() % 50) / 10.0;
            printf("%.1f ", B[i]);
        }
        printf("\n\n");

        // El proceso 0 arranca el anillo enviando al proceso 1
        if (np > 1) {
            MPI_Send(A, NELEMENTS, MPI_INT, 1, 0, MPI_COMM_WORLD);
            MPI_Send(B, NELEMENTS, MPI_FLOAT, 1, 1, MPI_COMM_WORLD);
            // Calculamos el tamaño final (5 iniciales + 1 por cada proceso extra)
            int final_size = NELEMENTS + (np - 1);
            // Usamos realloc para agrandar la memoria del proceso 0 y poder recibir el arreglo final
            A = (int*)realloc(A, final_size * sizeof(int));
            B = (float*)realloc(B, final_size * sizeof(float));

            // Recibe del último proceso (np - 1)
            MPI_Recv(A, final_size, MPI_INT, np - 1, 0, MPI_COMM_WORLD, &status);
            MPI_Recv(B, final_size, MPI_FLOAT, np - 1, 1, MPI_COMM_WORLD, &status);

            printf("--- RESULTADOS FINALES AL REGRESAR AL PROCESO 0 ---\n");
            printf("Proceso %d: Arreglo A final: ", id);
            for (int i = 0; i < final_size; i++) printf("%d ", A[i]);
            printf("\n");

            printf("Proceso %d: Arreglo B final: ", id);
            for (int i = 0; i < final_size; i++) printf("%.1f ", B[i]);
            printf("\n");
        }
    }
    else {
        // Lógica para los procesos 1 en adelante
        // Cada proceso puede calcular exactamente cuántos elementos va a recibir
        // Ej. El proceso 1 recibe 5. El proceso 2 recibe 6...
        int recv_size = NELEMENTS + (id - 1);
        int send_size = recv_size + 1; // El tamaño de salida incluye el elemento nuevo

        // Asignamos memoria suficiente para recibir los datos Y agregar uno más
        A = (int*)malloc(send_size * sizeof(int));
        B = (float*)malloc(send_size * sizeof(float));

        // Recibimos los arreglos del proceso anterior
        MPI_Recv(A, recv_size, MPI_INT, id - 1, 0, MPI_COMM_WORLD, &status);
        MPI_Recv(B, recv_size, MPI_FLOAT, id - 1, 1, MPI_COMM_WORLD, &status);

        // Agregamos un nuevo elemento al final (en la posición de memoria recv_size)
        A[recv_size] = id;                // Insertamos el id del proceso en A
        B[recv_size] = (float)id + 0.5;   // Insertamos un valor flotante basado en el id en B

        printf("Proceso %d: Arreglo A modificado: ", id);
        for (int j = 0; j < send_size; j++) printf("%d ", A[j]);
        printf("\n");

        printf("Proceso %d: Arreglo B modificado: ", id);
        for (int j = 0; j < send_size; j++) printf("%.1f ", B[j]);
        printf("\n\n");
        fflush(stdout);

        // Enviamos el arreglo, que ahora tiene un tamaño send_size, al siguiente proceso
        int next_process = (id + 1) % np;
        MPI_Send(A, send_size, MPI_INT, next_process, 0, MPI_COMM_WORLD);
        MPI_Send(B, send_size, MPI_FLOAT, next_process, 1, MPI_COMM_WORLD);
    }

    // Todos los procesos liberan su propia memoria antes de terminar
    free(A);
    free(B);

    MPI_Finalize();
    return 0;
}