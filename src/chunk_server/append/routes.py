from flask import Blueprint, request
from util.constants import HTTP_OK_STATUS_CODE, HTTP_BAD_REQUEST_STATUS_CODE, POST, GET
from .controller import AppendChunk

append_routes = Blueprint('append', __name__, url_prefix='/append')


'''
{
    "chunkHandle" : "3233",
    "data" : "",
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

@append_routes.route('/', methods=POST)
def append():
    json_pkt = request.get_json()
    resp = AppendChunk().operation(json_pkt)
    if not resp:
        return {"isSuccessful": False, "checksum" : ""}, HTTP_BAD_REQUEST_STATUS_CODE
    
    if resp in ["Overflow", "Append cannot be made for data more than forth of chunksize"]:
        return {"isSuccessful": False, "message" : resp, "checksum" : ""}, HTTP_BAD_REQUEST_STATUS_CODE


    return {"isSuccessful": True, "checksum" : resp}, HTTP_OK_STATUS_CODE

