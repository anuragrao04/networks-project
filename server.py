import socket
import pickle
from concurrent.futures import ThreadPoolExecutor
import ssl

HOST = 'localhost'  
PORT = 6969
WORKER_HOSTS = ['localhost:6000', 'localhost:6001', 'localhost:6002', 'localhost:6003']

def handle_client(conn, addr):
    with conn:
        print('Connected by', addr)
        data = conn.recv(102400)
        program, args_list = pickle.loads(data)
        print("Received program: ", program)
        print("Received arguments: ", args_list)
        result_sockets = []
        results = []
        for i, arg in enumerate(args_list):
            while(True):
                worker_host, worker_port = WORKER_HOSTS[i % len(WORKER_HOSTS)].split(':')
                try:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    s = socket.create_connection((worker_host, int(worker_port)))
                    secureSocket = context.wrap_socket(s, server_hostname=worker_host)
                    data = pickle.dumps((program, arg))
                    secureSocket.sendall(data)
                    result_sockets.append((secureSocket, s))
                    break
                except Exception as e:
                    print(f"Error connecting to worker{i % len(WORKER_HOSTS)}: ", e)
                    i += 1 # try the next worker
                    continue




        for securesocki, socki in result_sockets:
            data = securesocki.recv(102400)
            results.append(pickle.loads(data))
            securesocki.close()
            socki.close()

        print("Sending results back to client: ", results)
        conn.sendall(pickle.dumps(results))


while(True):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('./ssl/certificate.pem', './ssl/key.pem')
        s.bind((HOST, PORT))
        s.listen()
        secureSocket = context.wrap_socket(s, server_side=True)
        with ThreadPoolExecutor(max_workers=4) as executor: # for handling concurrent connections
            while(True):
                conn, addr = secureSocket.accept()
                executor.submit(handle_client, conn, addr)



