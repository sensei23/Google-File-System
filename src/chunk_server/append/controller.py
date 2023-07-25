from config import list_of_chunks
import traceback
from utils.constants import CHUNK_SIZE
from write.controller import WriteChunk

class AppendChunk:
    def __init__(self):
        pass

    def operation(self, pkt_json):
        try:
            
            if len(pkt_json['data']) > CHUNK_SIZE//4:
                return "Append cannot be made for data more than forth of chunksize"
            
            byte_start = 0
            byte_end = len(pkt_json['data']) - 1
            if pkt_json['chunkHandle'] in list_of_chunks:
                obj = list_of_chunks[pkt_json['chunkHandle']]
                if obj.getRemainingSize() < len(pkt_json['data']):
                    return "Overflow"
                byte_start = obj.dataSize
                byte_end = byte_start + byte_end

            pkt_json['byteStart'] = byte_start
            pkt_json['byteEnd'] = byte_end

            return WriteChunk().operation(pkt_json)

        except Exception as e:
            print(e)
            print(traceback.format_exc())
        return None
