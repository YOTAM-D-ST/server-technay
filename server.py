import subprocess
import shutil
from PIL import ImageGrab
import socket
import glob
import os
from constants import *


def execute(app_name):
    subprocess.call(app_name)
    return "execute successfully"


def copy(file_name, folder_path):
    shutil.copy(file_name, folder_path)
    return "file copied"


def file_delete(file_name):
    os.remove(file_name)
    return "file deleted"


def validate_folder(folder):
    return os.path.exists(folder)  # Or folder, will return true or false


def list_folder(name):
    files_list = glob.glob(name + "\\*.*")
    return str(files_list)


def take_screenshot():
    image = ImageGrab.grab()
    image.save(SCREENSHOT)
    return "screenshot taken"


def initiate_server_socket(ip, port):
    """initiate the server socket"""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, port))
        server_socket.listen(1)
        return server_socket
    except socket.error as m:
        print("initiate server socket error", m)
    except Exception as m:
        print("initiate server socket error", m)


def receive_client_request(client_socket):
    # read from socket
    raw_size = client_socket.recv(MSG_LEN_PROTOCOL)
    size = raw_size.decode()
    if size.isdigit():
        raw_request = client_socket.recv(int(size))
        request = raw_request.decode()
        # split to request and parameters
        req_and_prms = request.split()
        if len(req_and_prms) > 1:
            return req_and_prms[0], req_and_prms[1:]
        else:
            return req_and_prms[0], None  # no parameters
    else:
        return None, None  # illegal size parameter     ;l


def check_client_request(request, params):
    """check if the client request is one of the four options
    time or name or rand or exit or quit"""
    if request == "TAKE_SCREENSHOT" and params is None or request == "DIR" and validate_folder(params[0]) or \
            request == 'QUIT' or request == "EXIT" or request == "DELETE" and validate_folder(params[0]) \
            or request == "COPY" and validate_folder(params[1]) or request == "EXECUTE" and len(params) == 1:
        return True
    else:
        return False


def handle_single_client(client_socket):
    """check if the request is valid, make a response and sent it to the client"""
    try:
        request = ""
        while request.upper() != "QUIT" and request.upper() != "EXIT":
            request, params = receive_client_request(client_socket)
            valid = check_client_request(request, params)
            if valid:
                response = handle_client_request(request, params)
                send_response_to_client(response, client_socket)
            else:
                send_response_to_client("illegal command", client_socket)
        else:
            if request.upper() == 'QUIT':
                return False
            else:
                return True
    except socket.error as e:
        print("handle single client", e)
    except Exception as e:
        print("handle single client", e)


def handle_clients(server_socket):
    """accepting the requests, the main method"""
    try:
        done = False
        while not done:
            client_socket, address = server_socket.accept()
            done = handle_single_client(client_socket)
    except socket.error as m:
        print("socket error handle clients", m)
    except Exception as m:
        print("general error handle clients", m)


def handle_client_request(request, params):
    """return the method that fit"""
    try:
        if request == "TAKE_SCREENSHOT" and params is None:
            return take_screenshot()
        if request == "DIR" and validate_folder(params[0]):
            return list_folder(params[0])
        if request == "EXIT" and params is None:
            return "exit"
        if request == "QUIT" and params is None:
            return "quit"
        if request == "DELETE" and validate_folder(params[0]):
            return file_delete(params[0])
        if request == "COPY" and validate_folder(params[1]):
            return copy(params[0], params[1])
        if request == "EXECUTE" and len(params) == 1:
            return execute(params[0])
    except socket.error as m:
        print("handle single client error", m)
    except Exception as m:
        print("handle single client error", m)


def send_response_to_client(response, client_socket):
    """send the response to the client"""
    encoded_response = response.encode()
    l = len(encoded_response)
    ll = str(l)
    lll = ll.zfill(4)
    llll = lll.encode()
    client_socket.send(llll + encoded_response)


def main():
    """ren the methods, initiate server socket and handle clients"""
    server_socket = initiate_server_socket(ALL_IFFS, PORT)
    handle_clients(server_socket)
    server_socket.close()


if __name__ == "__main__":
    main()
