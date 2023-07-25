import json

class Chunk:
    def __init__(self,fileName,checkSum,chunkIndex,handle):
        self.fileName = fileName
        self.chunkIndex = chunkIndex
        self.handle = handle
        self.checkSum = checkSum
        self.replica_count = 3
        self.chunk_server_ip = []
        self.chunk_server_port = []
        self.usefulSpace = 64
        self.expiryTime = 60

    def __dict__(self):
        return {
            "fileName": self.fileName,
            "chunkIndex": self.chunkIndex,
            "handle": self.handle,
            "checkSum": self.checkSum,
            "replica_count": self.replica_count,
            "chunk_server_ip": self.chunk_server_ip,
            "chunk_server_port": self.chunk_server_port,
            "usefulSpace": self.usefulSpace,
            "expiryTime": self.expiryTime,
        }


    def __str__(self):
        return json.dumps(self.__dict__())
        

    