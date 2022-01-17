"""yotam shavit server technay project. the server"""
import subprocess
import shutil
from PIL import ImageGrab
import socket
import glob
import os
from constants import *


def execute(app_name):
    """
    method
    execute method, claim an app name and run the app
    """
    try:
        subprocess.call(app_name)
        return "program executed"
    except WindowsError:
        return "illegal command"


def copy(file_name, folder_path):
    """
    method
    copy method claim a file name and a folder path,
    then copy the file to the path
    return file copied
    """
    shutil.copy(file_name, folder_path)
    return "file copied"


def file_delete(file_name):
    """
    method
    claim a file name and delete the file
    returns file deleted
    """
    os.remove(file_name)
    return "file deleted"


def validate_folder(folder):
    """
    method
    claim a name and check if it is a folder
    """
    return os.path.exists(folder)  # Or folder, will return true or false


def list_folder(name):
    """
    method
    claim a folder name and returns the
    items in the list
    """
    files_list = glob.glob(name + "\\*.*")
    return str(files_list)


def valid_file(path):
    """
    a method thats claim a name and check if it is a file
    """
    return os.path.isfile(path)


def take_screenshot():
    """a method that returns a screenshot
    returns screenshot taken"""
    image = ImageGrab.grab()
    image.save(SCREENSHOT)
    return "screenshot taken"


def send_binary_data(sock, data):
    """
    a method that clain a socket and a data
    and send the data to the socket encrypted
    """
    l = len(data)
    ll = str(l)
    lll = ll.zfill(4)
    llll = lll.encode()
    sock.send(llll + data)


def send_file(file_name, sock):
    """
    :param file_name:
    :param sock:
    send the file in chunks to the socket, when finished
    send -1. return file sent
    """
    if valid_file(file_name):
        f1 = open(file_name, "rb")
        chunk = f1.read(MSG_LEN)
        while chunk != b"":
            send_binary_data(sock, chunk)
            chunk = f1.read(MSG_LEN)
        send_binary_data(sock, EOF)
        f1.close()
        return "file sent"
    else:
        send_binary_data(sock, EOF)
    return "illegal command"


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
    """

    :param client_socket:
    read from the socket
    """
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


def check_client_request(request, params, sock):
    """check if the client request is legal"""
    if request == "TAKE_SCREENSHOT" and params is None or \
            request == "DIR" and validate_folder(params[0]) or \
            request == 'QUIT' or request == "EXIT" or \
            request == "DELETE" and validate_folder(params[0]) \
            or request == "COPY" and validate_folder(params[1]) and \
            validate_folder(
                params[0]) or request == "EXECUTE" and len(params) == 1 or \
            request == "SEND_FILE" and \
            len(params) == 1:
        return True
    else:
        if request == "SEND_FILE":
            send_binary_data(sock, EOF)
        return False


def handle_single_client(client_socket):
    """check if the request is valid,
     make a response and sent it to the client"""
    try:
        request = ""
        done = False
        while not done:
            request, params = receive_client_request(client_socket)
            valid = check_client_request(request, params, client_socket)
            if valid:
                response = handle_client_request(
                    request, params, client_socket)
                send_response_to_client(response, client_socket)
                if request == 'EXIT':
                    done = True
            else:
                if request == "SEND_FILE":
                    send_response_to_client(-1, client_socket)
                send_response_to_client("illegal command", client_socket)
        return True
    except socket.error as e:
        print("handle single client", e)
    except Exception as e:
        print("handle single client", e)


def handle_clients(server_socket):
    """accepting the requests"""
    try:
        done = False
        while not done:
            client_socket, address = server_socket.accept()
            done = handle_single_client(client_socket)
    except socket.error as m:
        print("socket error handle clients", m)
    except Exception as m:
        print("general error handle clients", m)


def handle_client_request(request, params, sock):
    """return the method that fit"""
    try:
        if request == "TAKE_SCREENSHOT" and params is None:
            return take_screenshot()
        if request == "DIR" and validate_folder(params[START]):
            return list_folder(params[START])
        if request == "EXIT" and params is None:
            return "exit"
        if request == "QUIT" and params is None:
            return "quit"
        if request == "DELETE" and validate_folder(params[START]):
            return file_delete(params[START])
        if request == "COPY" and validate_folder(params[SECOND]):
            return copy(params[START], params[SECOND])
        if request == "EXECUTE" and len(params) == 1:
            return execute(params[START])
        if request == "SEND_FILE" and len(params) == SECOND:
            return send_file(params[START], sock)
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
    """ran the methods, initiate server socket and handle clients"""
    server_socket = initiate_server_socket(ALL_IFS, PORT)
    handle_clients(server_socket)
    server_socket.close()


if __name__ == "__main__":
    main()
