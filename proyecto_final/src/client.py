import sys
import grpc
import cluster_pb2
import cluster_pb2_grpc

def main():
    if len(sys.argv) < 3:
        print("Uso:")
        print("  python cli.py local <nombre_tarea>")
        print("  python cli.py send <P1..P5> <mensaje>")
        print("  python cli.py broadcast <mensaje>")
        sys.exit(1)

    action = sys.argv[1].lower()
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = cluster_pb2_grpc.NodeServiceStub(channel)
        if action == "local":
            resp = stub.ExecuteLocalTask(cluster_pb2.TaskRequest(task_name=sys.argv[2]))
        elif action == "send":
            resp = stub.SendMessage(cluster_pb2.SendRequest(target=sys.argv[2].upper(), content=sys.argv[3]))
        elif action == "broadcast":
            resp = stub.BroadcastMessage(cluster_pb2.BroadcastRequest(content=sys.argv[2]))
        else:
            print("Acción no válida")
            sys.exit(1)
        print(f"Respuesta: {resp.info} | Reloj actual: {list(resp.vector)}")

if __name__ == "__main__":
    main()