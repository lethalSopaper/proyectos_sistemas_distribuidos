#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <mpi.h>

#define M 6 // Definimos un número constante de columnas. Puedes cambiarlo.

int main(int argc, char **argv) {
    int id, np;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &id);
    MPI_Comm_size(MPI_COMM_WORLD, &np);

    // Hacemos que la cantidad de renglones (N) sea igual al número de procesos (np)
    int N = np;

    int *A = NULL;        // Matriz completa (solo existirá en el proceso 0)
    int *all_sums = NULL; // Arreglo para recolectar todas las sumas (solo proceso 0)

    // Todos los procesos reservan memoria para recibir su propio renglón
    int *local_row = (int *)malloc(M * sizeof(int));

    if (id == 0) {
        srand(time(NULL));

        // El proceso 0 reserva la memoria para toda la matriz (N * M)
        A = (int *)malloc(N * M * sizeof(int));
        // El proceso 0 reserva memoria para el arreglo que guardará los resultados de cada proceso
        all_sums = (int *)malloc(np * sizeof(int));

        printf("--- Matriz Inicial A (%d x %d) ---\n", N, M);
        for (int i = 0; i < N; i++) {
            printf("Renglón %d: ", i);
            for (int j = 0; j < M; j++) {
                A[i * M + j] = rand() % 50; // Valores aleatorios entre 0 y 49
                printf("%2d ", A[i * M + j]);
            }
            printf("\n");
        }
        printf("\n");
    }

    // El proceso 0 reparte M elementos (un renglón entero) a todos los procesos
    MPI_Scatter(A, M, MPI_INT, local_row, M, MPI_INT, 0, MPI_COMM_WORLD);

    // Cada proceso (incluido el 0) suma los elementos del renglón que le tocó
    int local_sum = 0;
    for (int i = 0; i < M; i++) {
        local_sum += local_row[i];
    }
    // Obtener el nombre del nodo
    char processor_name[MPI_MAX_PROCESSOR_NAME];
    int name_len;
    MPI_Get_processor_name(processor_name, &name_len);
    // Imprimimos para evidenciar que el trabajo está distribuido
    printf("Proceso %d en nodo %s calculó la suma de su renglón: %d\n", id, processor_name, local_sum);
    fflush(stdout); // Limpiamos el buffer para que se imprima ordenado en consola

    // Todos mandan su 'local_sum' (1 elemento) al proceso 0, quien los guarda en 'all_sums'
    MPI_Gather(&local_sum, 1, MPI_INT, all_sums, 1, MPI_INT, 0, MPI_COMM_WORLD);

    if (id == 0) {
        // Inicializamos asumiendo que el renglón 0 tiene la menor suma
        int min_sum = all_sums[0];
        int min_row = 0;

        // Buscamos si algún otro renglón tuvo una suma menor
        for (int i = 1; i < np; i++) {
            if (all_sums[i] < min_sum) {
                min_sum = all_sums[i];
                min_row = i; // El índice corresponde directamente al ID del proceso / renglón
            }
        }

        printf("\n--- RESULTADO FINAL ---\n");
        printf("El renglón con la suma menor es el renglón %d.\n", min_row);
        printf("La suma de sus elementos es: %d\n", min_sum);

        // Liberamos la memoria exclusiva del proceso 0
        free(A);
        free(all_sums);
    }

    // Todos los procesos liberan su renglón local
    free(local_row);

    MPI_Finalize();
    return 0;
}