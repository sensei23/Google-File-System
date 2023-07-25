import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.Chunk_Server import Chunk_Server

"""
Directory structure:

src
├── chunk_server
│   ├── test_server.py
│   ├── __init__.py

├── models
│   ├── Chunk_Server.py

"""

if __name__ == "__main__":

    servers = {}
    while True:
        port = int(input("Enter port number: "))
        if port ==0 : break
        if port < 0 : 
            print("Stopping the server...")
            try:
                servers[port*-1].shutdown()
            except:
                print("Config Error: Can't stop the server.")
            continue
        server = Chunk_Server("localhost",port)
        try:
            server.start()
            servers[port] = server
        except Exception as e:
            print("Config Error: Can't start the server.")

