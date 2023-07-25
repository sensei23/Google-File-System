
import os
from util.constants import MASTER_URLS, CHUNK_LOCATION 
from config import list_of_chunks
from random import choice
from util.models import ChunkMetaInfo
from utils.checksum import generate_checksum

def get_master_url():
    return choice(MASTER_URLS)

def update_chunks_list():
    try:
        for chunk in os.listdir(CHUNK_LOCATION):
            filepath = os.path.join(CHUNK_LOCATION, chunk)
            with open(filepath, 'r') as f:
                data = f.read()
                checksum = generate_checksum(data)
                size = len(data)
            list_of_chunks[chunk] = ChunkMetaInfo(chunk, checksum, size)
    except Exception as e:
        print('error while updating chunkList')
        print(e)