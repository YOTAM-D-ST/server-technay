"""yotam shavit server technay project. the client"""
import socket
from constants import *


def receive_file(request, my_socket):
    """
    :param request:
    :param my_socket:
    receive the file in chunks from the server
    """
    request = request[1].split("\\")
    # here you generate answer_file name from request
    answer_file = RECEIVED_FILE_LOCATION + "\\" + request[END]
    done = False
    with open(answer_file, "wb") as f:
        while not done:
            raw_size = my_socket.recv(MSG_LEN_PROTOCOL)
            size = raw_size.decode()
            if size.isdigit():
                data = my_socket.recv(int(size))
            if data == EOF:
                done = True
            # we write to file received data as is since we are in binary mode
            else:
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
    """check if the request is valid"""
    request = request.upper()
    if request != "TAKE_SCREENSHOT" and params is None and \
            request != "EXIT" and params is None and request != "QUIT" \
            and params is None:
        return False
    if request == "TAKE_SCREENSHOT" and params is None or \
            request == "QUIT" or \
            request == "EXIT" or request == "DIR" and \
            len(params) == 1 or request == "DELETE" and \
            len(params) == 1 \
            or request == "COPY" and len(params) == 2 or \
            request == "EXECUTE" and len(params) == 1 \
            or request == "SEND_FILE" and len(params) == 1:
        return True
    else:
        return False


def send_request_to_server(my_socket, request):
    """sent the request to the server"""
    encoded_request = request.encode()
    l = len(encoded_request)
    ll = str(l)
    lll = ll.zfill(4)
    llll = lll.encode()
    my_socket.send(llll + encoded_request)


def handle_server_response(my_socket, request):
    """
    :param my_socket:
    :param request:
    handle the server response
    """
    try:

        request = request.split()
        if request[0] == "SEND_FILE":
            receive_file(request, my_socket)
        raw_size = my_socket.recv(4)
        data_size = raw_size.decode()
        if data_size.isdigit():
            data = my_socket.recv(int(data_size))
            print(data.decode())
    except socket.error as message:
        print("handle user input socket error", message)
    except Exception as e:
        print("handle user input general error", e)


def handle_user_input(my_socket):
    """takes the input from the user, split it
    to request and parameters call the next methods"""
    try:
        request = ''
        done = False
        while not done:
            request = input("please enter a request ")
            req_and_prms = request.split()
            if len(req_and_prms) > 1:
                name = req_and_prms[START]
                params = req_and_prms[SECOND:]
            else:
                name = req_and_prms[START]
                params = None
            request = request.upper()
            if valid_request(name, params):
                send_request_to_server(my_socket, request)
                handle_server_response(my_socket, request)
                if request.upper() == "EXIT" or request.upper() == "QUIT":
                    done = True
            else:
                print("illegal request")
    except socket.error as message:
        print("handle user input socket error", message)
    except Exception as e:
        print("handle user input general error", e)


def main():
    """ran the methods, initiate client socket and handle user input"""
    my_socket = initiate_client_socket(IP, PORT)
    handle_user_input(my_socket)


if __name__ == "__main__":
    main()
