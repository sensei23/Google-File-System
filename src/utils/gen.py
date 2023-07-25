import uuid

# def generate_file_Path():

def generate_uuid():
    return str(uuid.uuid1().int>>64)


def make_url(url, port):
    if 'http://' in url:
        return f'{url}:{port}'
    return f'http://{url}:{port}'