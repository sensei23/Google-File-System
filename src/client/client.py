import traceback
import requests
import base64
import time
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api_request import post_dict, get_dict
from utils.gen import make_url

MASTER_URL = "http://192.168.78.190:5000"
files = dict()

CHUNK_SIZE = 64
DATA_SIZE = CHUNK_SIZE // 4

class File:
    def __init__(self, file_name) -> None:
        self.chunks = dict()
        self.file_name = file_name
        self.size = 0
        self.last_chunk_id = -1
    
    def request_md(self, chunk_idx : int):
        print("File::request_md")
        chunk = None
        if chunk_idx not in self.chunks or self.chunks[chunk_idx].exp_time < time.time():
            # request Master: (file_name, chunk_idx) --> chunk_md
            body = {"file_name":self.file_name, "chunk_idx":chunk_idx, "checksum":"000"}
            print("requesting metadata")
            response, status_code = post_dict(MASTER_URL + "/read_chunk", body)
            print("response code = ", status_code)
            if status_code == 200:
                chunk = Chunk(response) # response == chunk_metadata
                self.chunks[chunk_idx] = chunk
                self.last_chunk_id = max(self.last_chunk_id, chunk.chunk_idx)
            else:
                print("Error: ", response)
        else:
            chunk = self.chunks[chunk_idx] # key error
        print("~File::request_md")
        return chunk
    
    def read_chunk(self, chunk_idx : int, byte_start : int, byte_count : int):
        print("File::read_chunk")
        chunk = self.request_md(chunk_idx)
        # print("Chunk Type:", type(chunk))
        response, status_code = chunk.read(byte_start, byte_count)
        print("~File::read_chunk")
        return response, status_code
    
    def readall_chunk(self, chunk_idx : int):
        print("File::readall_chunks")
        chunk = self.request_md(chunk_idx)
        # print("Chunk Type:", type(chunk))
        response, status_code = chunk.readall()
        print("~File::readall_chunks")
        return response, status_code

    def append_chunk(self, data):
        print("File::append_chunk")
        chunk = self.request_md(-1) # -1 denotes last chunk
        response, status_code = chunk.append(data)
        print("~File::append_chunk")
        return response, status_code
    
    def write_chunk(self, chunk_idx : int, byte_start : int, byte_end : int, data):
        chunk = self.request_md(chunk_idx)
        response, status_code = chunk.write(data, byte_start, byte_end)
        return response, status_code

    def create_new_chunk(self):
        print("File::create_new_chunk")
        body = {"file_name":self.file_name, "chunk_idx":self.last_chunk_id + 1, "checksum":"000"}
        print(body)
        response, status_code = post_dict(MASTER_URL + "/query_chunk", body)
        if status_code == 200:
            print(response)
        print("~File::create_new_chunk")

    def delete_file(self):
        print("File::delete_file")
        response = requests.delete(MASTER_URL + "/delete/" + self.file_name)
        print("Response status_code", response.status_code)

    def recover_file(self):
        print("File::recover_file")
        response = requests.get(MASTER_URL + "/recover/" + self.file_name)
        print("Response status_code", response.status_code)
        
class Chunk:
    def __init__(self, chunk_md) -> None:
        print("Chunk")
        try:
            self.md = chunk_md
            self.replica_count = int(chunk_md["replica_count"])
            self.primary_server = int(chunk_md["primary_server"])
            self.chunk_idx = int(chunk_md["chunkIndex"])
            self.exp_time = chunk_md["expiryTime"]
            self.file_name = chunk_md["fileName"]
            self.checksum = chunk_md["checkSum"]
            self.handle = chunk_md["handle"]
            self.chunk_server_info = list()

            # sort chunk_servers wrt client's location
            for chi in range(self.replica_count):
                chunk_server_i = {
                    "ipAddress":chunk_md["chunk_server_ip"][chi],
                    "port":chunk_md["chunk_server_port"][chi],
                    "chunkServerId": chunk_md["server_ids"][chi],
                }
                self.chunk_server_info.append(chunk_server_i)
        except Exception as e:
        	print(e)
        print("~Chunk")
    
    def read(self, byte_start: int, byte_count : int):
        print("Chunk::read")
        for chs_i in range(self.md["replica_count"]):
            # request chunk_server: (chunk_handle, byte_range) --> (status, data, check_sum)
            chunk_server_url = make_url(self.md["chunk_server_ip"][chs_i], self.md["chunk_server_port"][chs_i])
            body = {
                "chunkHandle" : self.md["handle"],
                "byteOffset" : byte_start,
                "totalBytes" : byte_count,
            }
            print("Read request sent to:", chunk_server_url)
            print("body: \n", body)
            response, status_code = post_dict(chunk_server_url + "/read/", body)
            print("status_code = ", status_code)
            if status_code != 200:
                continue
            print("~Chunk::read")
            return response, status_code
        print("~Chunk::read")
        return None, None
    
    def readall(self):
        print("Chunk::readall")
        for chs_i in range(self.md["replica_count"]):
            # request chunk_server: (chunk_handle, byte_range) --> (status, data, check_sum)
            chunk_server_url = make_url(self.md["chunk_server_ip"][chs_i], self.md["chunk_server_port"][chs_i])
            body = {"chunkHandle" : self.md["handle"]}
            print("Read request sent to:", chunk_server_url)
            print("body: \n", body)
            response, status_code = post_dict(chunk_server_url + "/read/complete", body)
            print("status_code = ", status_code)
            if status_code != 200:
                continue
            print("~Chunk::read")
            return response, status_code
        print("~Chunk::readall")
        return None, None
    
    def append(self, data):
        # request primary: (chunk_handle, data) --> (status)
        print("Chunk::append")
        chunk_server_url = make_url(self.chunk_server_info[self.primary_server]["ipAddress"],self.chunk_server_info[self.primary_server]["port"])
        body = {
            "chunkServerInfo" : self.chunk_server_info,
            "chunkHandle" : self.handle,
            "clientIP" : "localhost",
            "clientPort" : 6969,
            "data" : data,
        }
        print("Append request sent to:", chunk_server_url)
        print("body: \n", body)
        response, status_code =  post_dict(chunk_server_url + "/append", body)
        print("status_code = ", status_code)
        print("~Chunk::append")
        return response, status_code
        
        
    def write(self, data, byteStart : int, byteEnd : int):
        print("Chunk::write")
        chunk_server_url = make_url(self.chunk_server_info[self.primary_server]["ipAddress"],self.chunk_server_info[self.primary_server]["port"])
        body = {
            "chunkServerInfo" : self.chunk_server_info,
            "chunkHandle" : self.handle,
            "clientIP" : "localhost",
            "byteStart" : byteStart,
            "clientPort" : 6969,
            "byteEnd" : byteEnd,
            "data" : data,
        }
        print("Write request sent to:", chunk_server_url)
        response, status_code = post_dict(chunk_server_url + "/write/", body)
        print("status_code = ", status_code)
        print("~Chunk::write")
        return response, status_code

def read_handler(file_name : str, chunk_idx : int, byte_start : int, byte_count : int):
    if file_name not in files:
        new_file = File(file_name)
        files[file_name] = new_file
    print("Read initiated")
    response, status_code = files[file_name].read_chunk(chunk_idx, byte_start, byte_count)
    print("status_code = ", status_code)
    if status_code == 200:
        print("Response:", response["data"])
    else:
        print("Error reading chunk: \n", response)

def append_handler(file_name : str, file_path : str):
    with open(file_path, "rb") as f:
        # file_data = base64.b64encode(f.read())
        file_data = f.read().decode("utf-8")        
    
    print(file_data, type(file_data))
    if file_name not in files:
        new_file = File(file_name)
        files[file_name] = new_file
    print("Append initiated")
    for attepmts in range(3):
        print("Attempt#: ", attepmts)
        response, status_code = files[file_name].append_chunk(file_data)
        if status_code == 200:
            print("Response:", response)
            return
        else:
            print("Error appending data: \n", response)
            files[file_name].create_new_chunk()
            print("waiting for 5 seconds...")
            time.sleep(5)
    print("Cannot append, try again later.")

def write_handler(file_name : str, chunk_idx : int, byte_start : int, byte_end : int, file_path : str):
    with open(file_path, "rb") as f:
        file_data = f.read().decode("utf-8")
    if file_name not in files:
        new_file = File(file_name)
        files[file_name] = new_file
    print("Write initiated")
    for attepmts in range(3):
        print("Attempt#: ", attepmts)
        response, status_code = files[file_name].write_chunk(chunk_idx, byte_start, byte_end, file_data)
        if status_code == 200:
            print("Response:", response)
            return
        else:
            print("Error writing data: \n", response)
    print("Cannot write, try again later.")

def create_file_handler(file_name : str):
    if file_name not in files:
        new_file = File(file_name)
        files[file_name] = new_file
    print("Create initiated")
    files[file_name].create_new_chunk()

def delete_file_handler(file_name : str):
    if file_name not in files:
        new_file = File(file_name)
        files[file_name] = new_file
    print("Create initiated")
    files[file_name].create_new_chunk()

def recover_file_handler(file_name : str):
    if file_name not in files:
        new_file = File(file_name)
        files[file_name] = new_file
    print("Create initiated")
    files[file_name].create_new_chunk()

def large_file_append_handler(file_name : str, local_file_name : str):
    if file_name not in files:
        new_file = File(file_name)
        files[file_name] = new_file
    with open(local_file_name, "rb") as f:
        chunk_number = 0
        while True:
            file_data = f.read(DATA_SIZE).decode("utf-8")
            if file_data == "":
                break
            print("Appending chunk#:", chunk_number)
            for attepmts in range(3):
                print("Attempt#: ", attepmts)
                response, status_code = files[file_name].append_chunk(file_data)
                if status_code == 200:
                    print("Response:", response)
                    break
                else:
                    print("Error appending data: \n", response)
                    files[file_name].create_new_chunk()
                    print("waiting for 5 seconds...")
                    time.sleep(5)
            # print("Cannot append, try again later.")
            chunk_number += 1

def sequential_read_handler(file_name : str):
    if file_name not in files:
        new_file = File(file_name)
        files[file_name] = new_file
    
    chi = 0
    data = ""
    while True:
        print("Read initiated : ", chi)
        try:
            response, status_code = files[file_name].readall_chunk(chi)
            print("status_code = ", status_code)
            if status_code == 200:
                print("Response:", response["data"])
                data += response["data"]
            else:
                print("Error reading chunk: \n", response)
                break
            chi += 1
        except Exception as e:
            print(e)
            break
    print("FILE DATA")
    print(data)

def delete_handler(file_name : str):
    if file_name not in files:
        new_file = File(file_name)
        files[file_name] = new_file
    files[file_name].delete_file();          

def recover_handler(file_name : str):
    if file_name not in files:
        new_file = File(file_name)
        files[file_name] = new_file
    files[file_name].recover_file();          

if __name__ == "__main__":
    while True:
        cmd = input().split()
        try:
            if cmd[0] == "read": # read file_name chunk_idx byte_start byte_count
                file_name = cmd[1]
                chunk_idx = int(cmd[2])
                byte_start = int(cmd[3])
                byte_count = int(cmd[4])
                read_handler(file_name, chunk_idx, byte_start, byte_count)

            elif cmd[0] == "readall": # read file_name
                file_name = cmd[1]
                sequential_read_handler(file_name)

            elif cmd[0] == "write": # write file_name chunk_idx byte_start byte_end local_file_path
                write_handler(cmd[1], int(cmd[2]), int(cmd[3]), int(cmd[4]), cmd[5])

            elif cmd[0] == "append": # append file_name local_file_path
                file_name = cmd[1]
                file_path = cmd[2]
                append_handler(file_name, file_path)

            elif cmd[0] == "create": # create file_name
                file_name = cmd[1]
                create_file_handler(file_name)
            
            elif cmd[0] == "delete": # delete file_name
                delete_handler(cmd[1])
            
            elif cmd[0] == "recover": # recover file_name
                recover_handler(cmd[1])
            
            elif cmd[0] == "setmaster": # setmaster master_url; eg 10.37.155.40:8080
                MASTER_IP = cmd[1]
                MASTER_PORT = cmd[2]
                MASTER_URL = make_url(MASTER_IP, MASTER_PORT)
                print("Master set:", MASTER_URL)

            elif cmd[0] == "appendall": # appendall file_name local_file_name
                large_file_append_handler(cmd[1], cmd[2])

            elif cmd[0] == "exit":
                break

        except Exception as e:
            print("Invalid command: \n", e)  
            print(traceback.format_exc())  
