from flask import Blueprint, Response
from threading import Thread
import time

errors = Blueprint("errors", __name__)

@errors.app_errorhandler(Exception)
def server_error(error):
    return Response(f"Oops, got an error! {error}", status=500)

class Crash_Routine():
    def __init__(self, master_server,logger):
        self.master_server = master_server
        self.logger = logger
        self.inspect_servers()

    def inspect_servers(self):
        inspect_gap = 15
        alive_cap = 30
        def start_replication(server_id):
            print("Starting Replication for Chunk Server: " + str(server_id))
            self.logger.warning("Replication Initiated for Chunk Server: " + str(server_id))
            try:
                status = self.master_server.replicate(server_id)
                if status:
                    print("Replication started!")
                    self.logger.warning("Server Replication done.")
                else:
                    print("Replication failed!")
            except Exception as e:
                print("Error in starting replication: ", e)
        def inspect():
            while True:
                print("Server Inspection Started -> ", time.time())
                for chunk_server in self.master_server.chunk_servers.values():
                    if chunk_server.isAlive and time.time() - chunk_server.last_ping > alive_cap:
                        self.master_server.removeChunkServer(chunk_server)
                        Thread(target=start_replication, args=(chunk_server.id,)).start()            
                time.sleep(inspect_gap)
        Thread(target=inspect).start()
