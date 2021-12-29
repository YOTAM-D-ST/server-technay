import socket
from constants import *


def receive_file(request, my_socket):
    answer_file = RECEIVED_FILE_LOCATION + "\\" + request  # here you generate answer_file name from request
    done = False
    with open(answer_file, "wb") as f:
        while not done:
            raw_size = my_socket.recv(MSG_LEN)
            size = raw_size.decode()
            if size.isdigit():
                data = my_socket.recv(int(size))
            if data == EOF:
                done = True
            else:  # we write to file received data as is since we are in binary mode
                f.write(data)


def initiate_client_socket(ip, port):
    """initiate the client socket"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        return client_socket
    except socket.error as m:
        print("initiate client socket error", m)
    except Exception as m:
        print("initiate client socket error", m)


def valid_request(request, params):
    request = request.upper()
    if request == "TAKE_SCREENSHOT" and params is None or request == "QUIT" or \
            request == "EXIT" or request == "DIR" and \
            len(params) == 1 or request == "DELETE" and len(params) == 1 \
            or request == "COPY" and len(params) == 2 or request == "EXECUTE" and len(params) == 1 \
            or request == "SEND_FILE" and len(params) == 1:
        return True
    else:
        return False


def send_request_to_server(my_socket, request):
    """sent the request"""
    encoded_request = request.encode()
    l = len(encoded_request)
    ll = str(l)
    lll = ll.zfill(4)
    llll = lll.encode()
    my_socket.send(llll + encoded_request)


def handle_server_response(my_socket, request):
    """"print the response in a sting and in bytes"""
    if request == 'SEND_FILE':
        receive_file(request, my_socket)
    raw_size = my_socket.recv(4)
    data_size = raw_size.decode()
    if data_size.isdigit():
        data = my_socket.recv(int(data_size))
        print(data.decode())


def handle_user_input(my_socket):
    """takes the input from the user"""
    request = ''

    while request.upper() != 'EXIT' and request.upper() != "QUIT":
        request = input("please enter a request ")
        req_and_prms = request.split()
        if len(req_and_prms) > 1:
            name = req_and_prms[0]
            params = req_and_prms[1:]
        else:
            name = req_and_prms[0]
            params = None
        request = request.upper()
        if valid_request(name, params):
            send_request_to_server(my_socket, request)
            handle_server_response(my_socket)
        else:
            print("illegal request")


def main():
    """ran the methods, initiate client socket and handle user input"""
    my_socket = initiate_client_socket(IP, PORT)
    handle_user_input(my_socket)


if __name__ == "__main__":
    main()
