import socket
import pickle
import ssl 
def send_function(function, args_list, host, port):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    s = socket.create_connection((host, port))
    secureSocket = context.wrap_socket(s, server_hostname=host)
    data = pickle.dumps((function, args_list))
    secureSocket.sendall(data)
    print("sent")
    received = secureSocket.recv(102400)
    secureSocket.close()
    s.close()
    return received


if __name__ == '__main__':
    program_text = r'''
import sys
def add(a, b):
    return a + b
print(add(int(sys.argv[1]), int(sys.argv[2])))
'''
    args_list = [(1,2), (3,4), (5,6), (7,8), (9,10), (11,12), (13,14), (15,16), (17,18), (19,20)]

    print("This is the function we're sending: ", program_text)

    print("These are the arguments we're sending: ")
    for args in args_list:
        print(args)
    print("sending now...")
    response = send_function(program_text, args_list, 'localhost', 6969)
    print("Received: ", pickle.loads(response))

