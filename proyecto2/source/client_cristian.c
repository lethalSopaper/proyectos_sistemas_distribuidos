#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <sys/time.h>

#define PORT 5000

double obtener_tiempo() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (double)tv.tv_sec + (double)tv.tv_usec / 1000000.0;
}

int main(int argc, char const *argv[]) {
    // Requerimos la IP del servidor y el desfase como argumentos
    if (argc != 3) {
        printf("Uso: ./client <IP_SERVIDOR> <DESFASE>\n");
        printf("Ejemplo: ./client 192.168.124.230 -15.5\n");
        return -1;
    }

    const char* ip_servidor = argv[1];
    double desfase = atof(argv[2]);

    printf("==========================================\n");
    printf("      CLIENTE - ALGORITMO DE CRISTIAN\n");
    printf("==========================================\n");
    printf("Conectando a IP: %s\n", ip_servidor);
    printf("Desfase del reloj: %+.2f segundos\n", desfase);

    double hora_antes = obtener_tiempo() + desfase;

    int sock = 0;
    struct sockaddr_in serv_addr;

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        printf("\n Error al crear el socket \n");
        return -1;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);

    if (inet_pton(AF_INET, ip_servidor, &serv_addr.sin_addr) <= 0) {
        printf("\n Dirección Invalida / No soportada \n");
        return -1;
    }

    // T0
    double T0 = obtener_tiempo();

    // Conectar
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        printf("\n Fallo de conexion con el servidor \n");
        return -1;
    }

    // Enviar solicitud "HORA"
    char *mensaje = "HORA";
    send(sock, mensaje, strlen(mensaje), 0);

    // Recibir hora
    char buffer[1024] = {0};
    read(sock, buffer, 1024);

    // T1
    double T1 = obtener_tiempo();
    double hora_servidor = atof(buffer);

    // Calculos RTT y Cristian
    double RTT = T1 - T0;
    double retraso = RTT / 2.0;

    double hora_ajustada = hora_servidor + retraso;
    
    // C es la hora calculada y Cc la hora simulada local
    double C = hora_ajustada;
    double Cc = T1 + desfase;

    // Sincronización lógica (C > Cc o C < Cc)
    if (C > Cc) {
        Cc = C;
        desfase = C - obtener_tiempo();
        printf("\n[AJUSTE] C > Cc : El reloj de referencia se ADELANTA hasta C.\n");
    } else if (C < Cc) {
        double diferencia = Cc - C;
        printf("\n[AJUSTE] C < Cc : El reloj local se DETIENE temporalmente por %f segundos...\n", diferencia);
        usleep((useconds_t)(diferencia * 1000000.0)); // Esperar
        C += diferencia;
        Cc = C;
    }

    // Resultados
    printf("\n--------------- DATOS ----------------\n");
    printf("T0: %lf\n", T0);
    printf("Hora del servidor: %lf\n", hora_servidor);
    printf("T1: %lf\n", T1);
    printf("RTT: %.6f segundos\n", RTT);
    printf("Retraso estimado: %.6f segundos\n", retraso);
    printf("Hora ajustada: %lf\n", hora_ajustada);
    printf("Hora sincronizada C: %lf\n", C);
    printf("Hora sincronizada Cc: %lf\n", Cc);

    printf("\n--------------- RESULTADO ----------------\n");
    printf("Diferencia antes:   %+.6f segundos\n", hora_antes - hora_servidor);
    printf("Diferencia despues: %+.6f segundos\n", hora_ajustada - hora_servidor);
    printf("Diferencia entre C y Cc: %+.6f segundos\n", C - Cc);

    close(sock);
    return 0;
}
