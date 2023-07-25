from flask import Blueprint, request
from util.constants import HTTP_OK_STATUS_CODE, HTTP_BAD_REQUEST_STATUS_CODE, POST, GET, DELETE
from .controller import DeleteChunk

delete_routes = Blueprint('delete', __name__, url_prefix='/delete')


@delete_routes.route('/', methods=DELETE)
def delete():
    json_pkt = request.get_json()
    DeleteChunk().operation(json_pkt)
    return "done"
