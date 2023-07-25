from flask import Blueprint, request
from utils.constants import POST
from .controller import WriteChunk
from utils.constants import HTTP_BAD_REQUEST_STATUS_CODE, HTTP_OK_STATUS_CODE

write_bp = Blueprint('write', __name__, url_prefix='/write')

'''
{
    "clientIP" : " ",
    "clientPort" : 34434,
    "chunkHandle" : "323",
    "data" : "  ",
    "byteStart" : 0,
    "byteEnd" : 232,
    "chunkServerInfo" : [
        {
            "chunkServerId" : "323 ",
            "ipAddress" : " ",
            "port" : 2323,
            "isPrimary" : True
        },
        {
            
        }
    ]

}
'''

@write_bp.route('/', methods = POST)
def writeChunk():
    pckt_json = request.get_json()
    #write data 
    resp = WriteChunk().operation(pckt_json)
    if not resp:
        return {"isSuccessful": False, "checksum" : ""}, HTTP_BAD_REQUEST_STATUS_CODE

    return {"isSuccessful": True, "checksum" : resp}, HTTP_OK_STATUS_CODE


@write_bp.route('/commit', methods = POST)
def commitChunk():
    pckt_json = request.get_json()
    #commit data
    resp = WriteChunk().commit(pckt_json)
    if not resp:
        return {"isSuccessful": False, "checksum" : ""}, HTTP_BAD_REQUEST_STATUS_CODE
    
    return {"isSuccessful": True, "checksum" : resp}, HTTP_OK_STATUS_CODE



'''
{
    "chunkHandle" : "323",
    "chunkServerInfo" : [
        {
            "chunkServerId" : "323 ",
            "ipAddress" : " ",
            "port" : 2323,
        },
        {
            "chunkServerId" : "999 ",
            "ipAddress" : " ",
            "port" : 2321,
        }
    ]

}

'''

@write_bp.route('/replicate', methods=POST)
def replicateChunk():
    json_pkt = request.get_json()
    resp = WriteChunk().makingReplication(json_pkt)
    if resp == 'success':
        return {"isSuccessful": True, "message" : resp}, HTTP_OK_STATUS_CODE
    return {"isSuccessful" : False, "message" : resp}, HTTP_BAD_REQUEST_STATUS_CODE
