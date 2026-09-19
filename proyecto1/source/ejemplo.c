#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

int main(int argc, char **argv) {
    int id, np;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &id);
    MPI_Comm_size(MPI_COMM_WORLD, &np);
    MPI_Status status;
    float data[5];

    if (id == 0) {
        // Proceso 0 inicializa el arreglo con valores diferentes
        for (int i = 0; i < 5; i++) {
            data[i] = (float)(i + 1) * 1.1; // Valores: 1.1, 2.2, 3.3, 4.4, 5.5
        }
        // Enviar el arreglo a los otros procesos
        for (int dest = 1; dest < np; dest++) {
            MPI_Send(data, 5, MPI_FLOAT, dest, 0, MPI_COMM_WORLD);
        }
    } else {
        // Procesos receptores reciben el arreglo
        MPI_Recv(data, 5, MPI_FLOAT, 0, 0, MPI_COMM_WORLD, &status);
        // Obtener el nombre del nodo
        char processor_name[MPI_MAX_PROCESSOR_NAME];
        int name_len;
        MPI_Get_processor_name(processor_name, &name_len);
        
        // Imprimir el arreglo recibido y la información del proceso
        printf("Proceso %d en nodo %s recibió el arreglo: ", id, processor_name);
        for (int i = 0; i < 5; i++) {
            printf("%.2f ", data[i]);
        }
        printf("\n");
    }


    MPI_Finalize();
    return 0;
}