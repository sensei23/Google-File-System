from flask import Blueprint, request
from utils.constants import POST, HTTP_BAD_REQUEST_STATUS_CODE, HTTP_OK_STATUS_CODE
from .controller import ReadChunk

read_bp = Blueprint('read', __name__, url_prefix='/read')

'''
{
    "chunkHandle" : "23423",
    "byteOffset" : 0,
    "totalBytes" : 33
}
'''


@read_bp.route('/', methods = POST)
def readChunk():
    json_pkt = request.get_json()
    resp = ReadChunk().operation(json_pkt)
    if not resp:
        return {'isSuccessfull': False}, HTTP_BAD_REQUEST_STATUS_CODE
    
    return {'isSuccessfull': True, **resp}, HTTP_OK_STATUS_CODE

@read_bp.route('/complete', methods=POST)
def readingCompleteChunk():
    json_pkt = request.get_json()
    resp = ReadChunk().complete(json_pkt)
    if not resp:
        return {'isSuccessfull' : False}, HTTP_BAD_REQUEST_STATUS_CODE
    return {'isSuccessfull' : True, **resp}, HTTP_OK_STATUS_CODE