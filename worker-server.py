import socket
import pickle
import os
import sys


HOST = sys.argv[1]
PORT = int(sys.argv[2])

def handle_client(conn, addr):
    with conn:
        print('Connected by', addr)
        data = conn.recv(102400)
        program, args = pickle.loads(data)
        print("Received program: ", program)
        print("Received arguments: ", args)
        with open(f"/tmp/worker{PORT}.py", "w") as f:
            f.write(program)
        os.system(f"python3 /tmp/worker{PORT}.py " + " ".join(map(str, args)) + f" > /tmp/worker{PORT}_output")
        with open(f"/tmp/worker{PORT}_output", "r") as f:
            output = f.read()
            print("sending output: ", output)
            conn.sendall(pickle.dumps(output))


        # conn.sendall(data)


while(True):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while(True):
            conn, addr = s.accept()
            handle_client(conn, addr)
