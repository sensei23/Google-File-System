import os
from util.constants import CHUNK_LOCATION
from config import list_of_chunks

class DeleteChunk:
    def __init__(self):
        pass

    def delete(self, handle):

        if handle not in list_of_chunks:
            return
        
        file_path = os.path.join(CHUNK_LOCATION, handle)
        try:
            os.remove(file_path)
        except Exception as e:
            print(handle, e)
        
        del list_of_chunks[handle]


    def operation(self, json_pkt):
        
        for handle in json_pkt['deletedChunks']:
            self.delete(handle)
        