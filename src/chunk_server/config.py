from models.Chunk_Server import Chunk_Server
from util.constants import IP, PORT, CHUNK_SERVER_LOCATION_ID, DISK_AVAIL_GB, CHUNK_SERVER_ID

list_of_chunks = {}

temporary_chunks = {}

temporary_append_chunks = {}

chunk_server = Chunk_Server(
    ip=IP,
    port=PORT,
    loc=CHUNK_SERVER_LOCATION_ID,
    diskAvail=DISK_AVAIL_GB,
    id=CHUNK_SERVER_ID
)