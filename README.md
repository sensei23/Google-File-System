# Google-File_System
This is implementation of the paper "The Google File System" - ( t.ly/r_f7 ) 

## USED TECHNOLOGIES:
- Python
- Flask
- Docker

## Features Implemented:
- Master Server
    - Write
    - Read
    - Delete
    - Recover
    - Heartbeat
    - Chunkserver Failure Detection -> Replication
    - Garbage Collection
- Chunkserver
    - Write
    - Read
    - Delete
    - Recover
    - Heartbeat
- Client
    - Append
    - Read
    - Delete
    - Recover

## How to run:

### 1. Install Docker and Docker Compose
### 2. Clone the repository
### 3. Run the following commands:
```bash
# This will start the master server
docker-compose build
docker-compose up
```
### 4. Start ChunkServers
```bash
# This will start the chunkserver
python3 chunk_server/app.py <port>
```
### 5. Start Client
```bash
# This will start the client
python3 client/client.py
```

## How to use:
### 1. Append
```bash
append <filename> <local_file_path>
# Appends the contents of the local file to the file in the GFS. The data to be appended must be less than chunk capacity.

appendall <filename> <local_file_path>
# Appends the contents of the local file to the file in the GFS. The data can be arbitrarily large. Client will break the data into chunks and append them to the file in the GFS.
```
### 2. Read
```bash
read <filename> <chunk_index> <offset> <length>
# Reads the data from the chunk at the given index. The data is read from the given offset and the length of the data to be read is given by length.

readall <filename>
# Reads the entire file from the GFS.
```
### 3. Delete
```bash
delete <filename>
# Deletes the file from the GFS.
```
### 4. Recover
```bash
recover <filename>
# Recovers the deleted file from the GFS.
```

### 5. Write
```bash
write <filename> <chunk_index> <start_offset> <end_offset> <data>
# Writes the data to the chunk at the given index. The data is written to the given offset.
```

## Authors:
- [Shreyash Agrawal](https://github.com/sensei23)
- [Sarthak Rawat](https://github.com/sarthak-rawat-1101)
- [Lalit Gupta](https://github.com/devLalitx86Repo)
- [Gagan Agarwal](https://github.com/GaganAgarwal1813)



