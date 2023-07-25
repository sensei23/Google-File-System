import time
from utils.constants import CHUNK_SIZE

class ChunkMetaInfo:
    def __init__(self, chunkHandle, checksum, dataSize=0):
        self.chunkHandle = chunkHandle
        self.checksum = checksum
        self.dataSize = dataSize
        self.isPrimary = False
        self.leaseTimestamp = None

    def setPrimary(self, leaseTimestamp=time.time()):
        self.isPrimary = True
        self.leaseTimestamp = leaseTimestamp

    def getRemainingSize(self):
        return CHUNK_SIZE - self.dataSize

    def getLeaseSpanDuration(self) -> float:
        if self.isPrimary:
            return time.time()
        return 0
    
    def getChunkInfo(self) -> dict:
        return {
            "checksum" : self.checksum,
            "chunkHandle" : self.chunkHandle,
            "isPrimary" : self.isPrimary,
            "lease" : self.getLeaseSpanDuration(),
        }
    
    def __str__(self) -> str:
        return self.getChunkInfo()
    
class chunkTempInfo:
    def __init__(self, chunkData, byteStart, byteEnd, timestamp=time.time()):
        self.chunkData = chunkData
        self.byteStart = byteStart
        self.byteEnd = byteEnd
        self.timestamp = timestamp
    def stillValid(self):
        return time.time() - self.timestamp < 60