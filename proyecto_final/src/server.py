import os
import threading
from concurrent import futures
import grpc
import cluster_pb2
import cluster_pb2_grpc

NODES = ["P1", "P2", "P3", "P4", "P5"]
PORT = 50051

class NodeServicer(cluster_pb2_grpc.NodeServiceServicer):
    def __init__(self, node_name: str):
        self.node_name = node_name
        self.idx = NODES.index(node_name)
        self.clock = [0, 0, 0, 0, 0]
        self.lock = threading.Lock()
        os.makedirs("/app/logs", exist_ok=True)
        self.log_path = f"/app/logs/{node_name.lower()}.log"

    def _fmt_vec(self, vec):
        return "[" + ",".join(map(str, vec)) + "]"

    def _log(self, entry: str):
        print(entry, flush=True)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(entry + "\n")

    def ExecuteLocalTask(self, request, context):
        with self.lock:
            self.clock[self.idx] += 1
            current = list(self.clock)
            self._log(f'[INTERNAL] {self.node_name} tarea="{request.task_name}" vector={self._fmt_vec(current)}')
        return cluster_pb2.AckResponse(success=True, info="Tarea ejecutada", vector=current)

    def _send_single(self, target: str, content: str):
        if target not in NODES or target == self.node_name:
            self._log(f'[ERROR] {self.node_name} destino inválido="{target}"')
            return False, []

        with self.lock:
            self.clock[self.idx] += 1
            vec_to_send = list(self.clock)
            self._log(f'[SEND] {self.node_name} -> {target} msg="{content}" vector={self._fmt_vec(vec_to_send)}')

        try:
            with grpc.insecure_channel(f"{target.lower()}:{PORT}") as channel:
                stub = cluster_pb2_grpc.NodeServiceStub(channel)
                resp = stub.ReceiveMessage(
                    cluster_pb2.MessageRequest(
                        sender=self.node_name,
                        receiver=target,
                        content=content,
                        vector=vec_to_send,
                    ),
                    timeout=5.0,
                )
            self._log(f'[ACK] {self.node_name} <- {target} estado="OK" vector_remoto={self._fmt_vec(resp.vector)}')
            return True, vec_to_send
        except grpc.RpcError as e:
            self._log(f'[ERROR] {self.node_name} -> {target} detalle="{e.code().name}"')
            return False, vec_to_send

    def SendMessage(self, request, context):
        ok, vec = self._send_single(request.target, request.content)
        return cluster_pb2.AckResponse(success=ok, info="Enviado" if ok else "Fallo envío", vector=vec)

    def ReceiveMessage(self, request, context):
        received_vec = list(request.vector)
        with self.lock:
            self.clock = [max(local, rem) for local, rem in zip(self.clock, received_vec)]
            self.clock[self.idx] += 1
            updated_vec = list(self.clock)
            self._log(
                f'[RECEIVE] {self.node_name} <- {request.sender} msg="{request.content}" '
                f'recibido={self._fmt_vec(received_vec)} actualizado={self._fmt_vec(updated_vec)}'
            )
        return cluster_pb2.AckResponse(success=True, info="ACK", vector=updated_vec)

    def BroadcastMessage(self, request, context):
        self._log(f'[BROADCAST] {self.node_name} -> TODOS msg="{request.content}"')
        all_ok = True
        for target in NODES:
            if target != self.node_name:
                ok, _ = self._send_single(target, request.content)
                all_ok = all_ok and ok
        with self.lock:
            current = list(self.clock)
        return cluster_pb2.AckResponse(success=all_ok, info="Broadcast completado", vector=current)

def serve():
    node_name = os.environ.get("NODE_NAME", "P1").upper()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cluster_pb2_grpc.add_NodeServiceServicer_to_server(NodeServicer(node_name), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"[{node_name}] Servidor gRPC escuchando en puerto {PORT}...", flush=True)
    server.wait_for_termination()

if __name__ == "__main__":
    serve()