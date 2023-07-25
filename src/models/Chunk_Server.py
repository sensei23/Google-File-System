# import requests
from threading import Thread
import time

# local imports
# from utils.gen import generate_uuid

class Chunk_Server:
    def __init__(self, ip, port, id=None, diskAvail=0, loc = (0,0), chunkList=[]):
        self.id = id
        # if id == None:
        #     self.id = generate_uuid()
        self.ip = ip
        self.port = port
        self.isAlive = True
        self.masters = ["localhost:5000"]
        self.last_ping = time.time()
        self.diskAvail = diskAvail
        self.loc = loc
        self.chunkList = chunkList 

    def getInitInfo(self):
        return {
            "chunkServerId" : self.id,
            "ipAdress" : self.ip,
            "port" : self.port,
            "chunkLocationId": self.loc,
            "diskAvail" : self.diskAvail,
        }
    
    def getPingInfo(self):
        return {
            "chunkServerId" : self.id,
            "isAlive" : self.isAlive,
            "diskAvail" : self.diskAvail,
            "timestamp" : time.time(),
            # "chunkInfo" : self.availableChunks
        }

    def get_url(self):
        return "http://{}:{}".format(self.ip, self.port)    

    # def start(self):
    #     for master in self.masters:
    #         url = "http://{}/initiate".format(master)
    #         payload = {"id": self.id, "ip": self.ip, "port": self.port}
    #         try:
    #             response = requests.post(url, json=payload)
    #             if response.status_code == 200:
    #                 self.ping_master()
    #                 print(response.json())
    #                 break
    #         except Exception as e:
    #             print("Error: {}".format(str(e)))

    # def ping_master(self):
    #     ping_route = "/ping"

    #     def ping():
    #         while self.isAlive:
    #             for master in self.masters:
    #                 url = "http://{}{}".format(master, ping_route)
    #                 payload = {"id": self.id, "timestamp": time.time()}
    #                 try:
    #                     response = requests.post(url, json=payload)
    #                     if response.status_code == 200:
    #                         # print(response.json())
    #                         break
    #                 except Exception as e:
    #                     print("Error: {}".format(str(e)))
    #             time.sleep(15)
                
    #     Thread(target=ping).start()

    def shutdown(self):
        self.isAlive = False

    def alive(self):
        return self.isAlive

    def update_ts(self, timestamp):
        
        # print("TimeStamp type:", type(timestamp))
        # print("Last Ping Type: ", type(self.last_ping))
        if(self.last_ping < timestamp):
            self.last_ping = timestamp
    
    def update_diskAvail(self, diskAvail):
        self.diskAvail = diskAvail
    
    def add_chunk(self,chunk):
        self.chunkList.append(chunk)

    def __dict__(self):
        return {"id": self.id, 
                "ip": self.ip, 
                "port": self.port, 
                "isAlive": self.isAlive, 
                "last_ping": self.last_ping, 
                "Avail Space":self.diskAvail,
                "Location":self.loc,
                "chunkList":self.chunkList}

