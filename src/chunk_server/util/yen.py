import threading
import time
from .constants import HTTP_OK_STATUS_CODE
from utils.api_request import post
from config import chunk_server, list_of_chunks
from utils.constant_routes import CHUNK_SERVER_PING, CHUNK_SERVER_INITIATE
from utils.checksum import generate_checksum, validate_checksum
from util.general import get_master_url, update_chunks_list

'''
{
    "chunkServerId" : " ",
    "isAlive" : true,

    "diskAvail" : 10,
    "chunkInfo" : [
        {
            "checksum" : "",
            "chunkHandle" : "",
            "isPrimary" : true/false,
            "lease" : 20,

        },
        ...,
        {
        
        }
    ]
}

'''

'''
{
    "chunkServerId" : " ",
    "ipAdress" : " ",
    "port" : 2345,
    "chunkLocationId": 12,
    "diskAvail" : 10,

}
'''

class Heartbeat(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def collectInfo(self):
        data = chunk_server.getPingInfo()
        all_chunks = list(list_of_chunks.values())
        data['chunkInfo'] = [obj.getChunkInfo() for obj in all_chunks]
        data['diskAvail'] -= len(all_chunks)
        del all_chunks
        return data

    def sendInfo(self, data):
        url = get_master_url()
        full_url = url + CHUNK_SERVER_PING
        resp = post(full_url, data)
        if resp.status_code == HTTP_OK_STATUS_CODE:
            print('successfull ping')
        else:
            print('failure ping')
        
    def flow(self):
        try:
            data = self.collectInfo()
            self.sendInfo(data)
        except Exception as e:
            print('error while ping')
            print(e)

    def run(self):
        while True:
            time.sleep(20)
            print('now pinging master')
            self.flow()


class StartServer:
    def __init__(self):
        pass

    def init_chunk_server(self):
        try:
            ping_pkt = chunk_server.getInitInfo()
            url = get_master_url()
            full_url = url + CHUNK_SERVER_INITIATE
            resp = post(full_url, ping_pkt)
            print('inititate working ...')
            if resp.status_code == HTTP_OK_STATUS_CODE:
                print('initiate success')
                return True
            print('initiate fail')
            return False
        except Exception as e:
            print('initiate not working')
            print(e)
        

    def up(self):
        update_chunks_list()
        
        if not self.init_chunk_server():
            print('chunk server start failure')
            return False

        Heartbeat().start()
        return True
