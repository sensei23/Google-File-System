import os
from threading import Thread
import time
import requests

#local import 
from models.Master import MasterServer

class Garbage_Collection_Routine():
    def __init__(self, master_server: MasterServer,logger):
        self.master_server = master_server
        self.logger = logger
        self.gc_gap = 120
        self.gc()

    def gc(self):
        
        recovery_cap = 90
        def garbage_collect():
            while True:
                print("Garbage Collecting for Master Server -> PermanentDelete")
                self.logger.warning("Garbage Collecting for Master Server -> PermanentDelete")
                files = list(self.master_server.delete_ts_files.items())
                for file in files:
                    if time.time() - file[1] > recovery_cap:
                        self.master_server.deleteFilePermanent(file[0])
                time.sleep(self.gc_gap)

        def garbage_collect_cs():
            
            while True:
                print("Garbage Collecting for Chunk Servers... ")
                for chunk_server in list(self.master_server.chunk_servers.values()):
                    if not chunk_server.isAlive:
                        continue
                    del_chunks = []
                    try:
                        chunk_list = self.master_server.ping_chunk_catelog[chunk_server.id]
                        #chunks in sorted order
                        for handle in chunk_list:
                            if handle not in chunk_server.chunkList:
                                del_chunks.append(handle)
                        if len(del_chunks) > 0:
                            #request chunk_server to delete chunks
                            URL = chunk_server.get_url() + "/delete"
                            payload = {"deletedChunks": del_chunks}
                            requests.delete(URL, json=payload)
                    except:
                        pass
                time.sleep(self.gc_gap)
                        
        Thread(target=garbage_collect).start()
        Thread(target=garbage_collect_cs).start()


