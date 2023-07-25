import time
from utils.constants import LEASE_TIME

#local imports
from .Chunk import Chunk
from .Chunk_Server import Chunk_Server
from utils.gen import generate_uuid
import requests


class MasterServer:
    def __init__(self):
        self.name = "MasterServer"
        self.ip = ""
        self.port = 0
        self.chunk_to_servers = {} # key: Chunk Handle, value: ChunkServer ID list
        self.chunk_servers = {} # key: ChunkServer ID, value: ChunkServer Object
        self.isServerAlive = {} # key: ChunkServer ID, value: True/False
        self.ServerCapacity = {} # key: ChunkServer ID, value: Capacity i.e. available space
        self.fileToChunks = {} # key: File Name, value: List of Chunk Objects Corresponding to file
        self.chunkHandleToObj = {} # key: Chunk Handle, value: ChunkObject
        self.chunkHandleToPrimary = {} # key: Chunk Handle, value: [Primary ChunkServer ID, Start Time]
        self.ping_chunk_catelog = {} # key: ChunkServer ID, value: Last Ping chunks
        self.delete_ts_files = {}

    
    def chunk_avail(self,file_name,index):        
        if file_name in self.delete_ts_files.keys():
            return False
        if file_name in self.fileToChunks and len(self.fileToChunks[file_name]) > index:
            return True
        return False   

    def addChunk(self, file_name, index,checksum):   

        if file_name in self.delete_ts_files.keys():
            #delete permanent
            self.deleteFilePermanent(file_name)
        
        handle = generate_uuid()
        chunk = Chunk(file_name,checksum,index,handle)

        if file_name not in self.fileToChunks:
            self.fileToChunks[file_name] = []
        self.fileToChunks[file_name].append(chunk)
        self.chunkHandleToObj[handle] = chunk
        
        chunkServers = self.getChunkServers()
        if len(chunkServers) == 0:
            return False, "No Chunk Servers Available"
        
        for server in chunkServers:
            server.chunkList.append(handle)
        self.chunk_to_servers[handle] = [server.id for server in chunkServers]
        chunk.chunk_server_ip = [server.ip for server in chunkServers]
        chunk.chunk_server_port = [server.port for server in chunkServers]            
        self.chunkHandleToPrimary[handle] = [self.DecidePrimaryServer(chunkServers), time.time()]
        chunk.replica_count = len(chunkServers)

        response = chunk.__dict__()    
        response["server_locations"] = [server.loc for server in chunkServers]
        response["server_ids"] = [server.id for server in chunkServers]
        response["primary_server"] = 0   
        return True, response

    def getChunkInfo(self, fileName, chunkIndex):
        if self.chunk_avail(fileName,chunkIndex):
            chunkList = self.fileToChunks[fileName]
            chunk = chunkList[chunkIndex]
            response = chunk.__dict__()
            avail_time = self.getExpiryTime(chunk.handle)
            response["expiryTime"] = avail_time
            response["primary_server"] = 0
            csIDS = self.chunk_to_servers[chunk.handle]
            response["chunk_server_ip"] = [self.chunk_servers[csID].ip for csID in csIDS]
            response["chunk_server_port"] = [self.chunk_servers[csID].port for csID in csIDS]
            response["server_ids"] = csIDS
            response["server_locations"] = [self.chunk_servers[csID].loc for csID in csIDS]
            return True, response
        else:
            return False, "Chunk Not Found"
    
    def recoverFile(self, fileName):
        if fileName in self.delete_ts_files.keys():
            del self.delete_ts_files[fileName]
            return True, "File Recovered"
        else:
            return False, "File Not Found"

    def deleteFileTemporary(self, fileName):
        self.delete_ts_files[fileName] = time.time()
        return True, "File Deleted"
    
    def deleteFilePermanent(self,file_name,logger=None):
        if file_name in self.delete_ts_files.keys():
            if logger:
                logger.info(f"Deleting File: {file_name}")
            del self.delete_ts_files[file_name]
            #delete chunk list
            chunkList = self.fileToChunks[file_name]
            for chunk in chunkList:
                #delete for servers
                for server in self.chunk_to_servers[chunk.handle]:
                    self.chunk_servers[server].chunkList.remove(chunk.handle)
                del self.chunkHandleToObj[chunk.handle]
                del self.chunk_to_servers[chunk.handle]
                del self.chunkHandleToPrimary[chunk.handle]
            del self.fileToChunks[file_name]
            return True, "File Deleted"
        return False, "File Not Found"

    #Methods for Chunk Servers  
    def getChunkServers(self,top=3):
        #return top 3 chunk diskAvail servers
        servers = []
        for server in self.chunk_servers.values():
           if server.isAlive:
                servers.append(server)
        servers.sort(key=lambda x: x.diskAvail, reverse=True)
        return servers[:top] if len(servers) > 3 else servers

    def addChunkServer(self, payload: dict):
        try:
            id = payload.get("chunkServerId")
            ip = payload.get("ipAdress")
            port = payload.get("port")
            loc = payload.get("chunkLocationId")
            diskAvail = payload.get("diskAvail")
            chunk_server = Chunk_Server(ip,port,id, diskAvail, loc,[])  

            self.chunk_servers[chunk_server.id] = chunk_server
            self.isServerAlive[chunk_server.id] = True
            self.ServerCapacity[chunk_server.id] = chunk_server.diskAvail
            return True, "OK"
        except Exception as e:
            raise e

    def getCSList(self):
        return list(server.__dict__() for server in self.chunk_servers.values())
    
    def update_ts(self, chunkServerID, timestamp):
        self.chunk_servers[chunkServerID].update_ts(timestamp)
    
    def update_diskAvail(self, chunkServerID, diskSize):
        self.chunk_servers[chunkServerID].update_diskAvail(diskSize)

    def removeChunkServer(self, chunk_server):
        # set chunk server to dead
        self.chunk_servers[chunk_server.id].isAlive = False
    
    
    def update_chunkInfo(self, chunkServerID, chunkInfo_lis):
        CS_ChunkList  = [chunkInfo["chunkHandle"] for chunkInfo in chunkInfo_lis]
        CS_ChunkList.sort()
        self.ping_chunk_catelog[chunkServerID]  = CS_ChunkList
            
        
    def DecidePrimaryServer(self, chunkServerLis):
        # chunkServerIDs = [server.id for server in chunkServerLis]
        # spaceAvailable = -1
        # primaryID = -1
        # for id in chunkServerIDs:
        #     id = str(id)
        #     if id in self.isServerAlive and self.isServerAlive[id]:
        #         if id in self.ServerCapacity and self.ServerCapacity[id] > spaceAvailable:
        #             spaceAvailable = self.ServerCapacity[id]
        #             primaryID = id
            
        return chunkServerLis[0].id
                
    


    # # Methods for Chunk

    def getExpiryTime(self, handle):
        requestTime = time.time()
        # if(handle not in self.chunkHandleToPrimary):
        #     return -1
        diff = requestTime - self.chunkHandleToPrimary[handle][1]
        time_gap = LEASE_TIME - diff
        if(time_gap < 5):            
            chunkServers = [self.chunk_servers[serverID] for serverID in self.chunk_to_servers[handle]] 
            self.chunkHandleToPrimary[handle] = [self.DecidePrimaryServer(chunkServers), time.time()]
            diff = 0
        return LEASE_TIME - diff

    #feature

    def replicate(self,server_id):
        chunk_server = self.chunk_servers[server_id]
        chunk_handles = chunk_server.chunkList
        for handle in chunk_handles:
            servers = self.chunk_to_servers[handle]
            fcs = self.getChunkServers()
            #index of server id in servers
            idx = servers.index(server_id)
            new_server = None
            for id in fcs:
                if id not in servers:
                    new_server = id
                    self.chunk_to_servers[handle][idx] = new_server.id
                    break
            new_server.chunkList.append(handle)
            url = new_server.get_url()
            req_json = {"chunkHandle":handle,
                        "chunkServerInfo":[]}
            
            for cur in range(3):
                if cur != idx:
                    server_info = {
                        "chunkServerId":self.chunk_servers[servers[cur]].id,
                        "ipAddress":self.chunk_servers[servers[cur]].ip,
                        "port":self.chunk_servers[servers[cur]].port    
                    }
                    req_json["chunkServerInfo"].append(server_info)

            #/write/replicate
            r = requests.post(url+"/write/replicate",json=req_json)
            if r.status_code != 200:
                print("Replication Failed")
                return False
        return True



            