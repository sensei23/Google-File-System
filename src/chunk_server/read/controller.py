import os
from util.constants import CHUNK_LOCATION
from config import list_of_chunks
import traceback
from utils.checksum import generate_checksum

class ReadChunk:
    def __init__(self):
        pass

    def operation(self, json_pkt):
        try:
            resp = self.read(json_pkt['chunkHandle'], json_pkt['byteOffset'], json_pkt['totalBytes'])
            if not resp:
                return resp
            
            checksum = generate_checksum(resp)
            pkt = {
                'data' : resp,
                'checksum' : checksum
            }

            return pkt
        except Exception as e:
            print(e)
            print(traceback.format_exc())
        return None

    def read(self, handle, byteOffset, totalBytes):
        if handle not in list_of_chunks:
            return None
        file_path = os.path.join(CHUNK_LOCATION, handle)
        if not os.path.isfile(file_path):
            return None
        
        file_size = os.path.getsize(file_path)

        if (byteOffset < 0 or byteOffset > file_size or file_size < byteOffset + totalBytes):
            return None
        
        data = None
        with open(file_path, 'r') as f:
            f.seek(byteOffset)
            data = f.read(totalBytes)
        
        return data
    
    def complete(self, json_pkt):
        try:
            handle = json_pkt['chunkHandle']
            if handle not in list_of_chunks:
                return None
            json_pkt['totalBytes'] = list_of_chunks[handle].dataSize
            json_pkt['byteOffset'] = 0

            return self.operation(json_pkt)

        except Exception as e:
            print('error while reading complete chunk')
            print(e)