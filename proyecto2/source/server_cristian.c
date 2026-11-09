#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <sys/time.h>

#define PORT 5000

void *atender_cliente(void *socket_desc) {
    int sock = *(int*)socket_desc;
    free(socket_desc);
    char buffer[1024] = {0};

    // Recibir solicitud del cliente
    if (read(sock, buffer, 1024) > 0) {
        if (strncmp(buffer, "HORA", 4) == 0) {
            // Obtener la hora del servidor en double
            struct timeval tv;
            gettimeofday(&tv, NULL);
            double hora_servidor = (double)tv.tv_sec + (double)tv.tv_usec / 1000000.0;
            
            char time_str[64];
            snprintf(time_str, sizeof(time_str), "%lf", hora_servidor);
            
            // Enviar la hora al cliente
            write(sock, time_str, strlen(time_str));
            printf("Enviando hora a cliente: %s\n", time_str);
        }
    }
    
    close(sock);
    printf("Cliente desconectado.\n");
    pthread_exit(NULL);
}

int main() {
    int server_fd, *new_sock;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);

    // Crear socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // Opciones del socket para reutilizar puerto
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    // Bind
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    // Listen
    if (listen(server_fd, 10) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    printf("==========================================\n");
    printf("     SERVIDOR - ALGORITMO DE CRISTIAN\n");
    printf("==========================================\n");
    printf("Servidor escuchando en el puerto %d\n", PORT);
    printf("Esperando clientes...\n\n");

    while(1) {
        int client_socket;
        if ((client_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
            perror("accept");
            continue;
        }
        
        printf("\nCliente conectado.\n");
        
        pthread_t sn_thread;
        new_sock = malloc(sizeof(int));
        *new_sock = client_socket;
        
        if(pthread_create(&sn_thread, NULL, atender_cliente, (void*) new_sock) < 0) {
            perror("could not create thread");
            return 1;
        }
        
        pthread_detach(sn_thread);
    }
    return 0;
}
