from driver import app
from chunk_server.util.constants import IP, PORT
from util.yen import StartServer
from util.general import update_chunks_list

if __name__ == '__main__':
    if StartServer().up():
        print('Successful Start')
        app.run(host=IP, port=PORT, debug=False, threaded=True)
    else:
        print('unable to start')
    # update_chunks_list()
    # # app.run(host=IP, port=PORT, debug=True, threaded=False)
    # app.run(host=IP, port=PORT, debug=False, threaded=True)