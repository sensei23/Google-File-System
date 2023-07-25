

# Chunk Server
- lorem ipsum

# how to run
- change .env file according to your system
- run `pip install -r requirements.txt`
- run `./run.sh` 

Note: python app.py 2342 chunk1 <br>
here, 2342 is port no. and chunk1 is the folder specific to where chunks will be added. its not important to add this though, if proper path is given in .env 

# .env
- master_urls: seperate by commas (,) if multiple
- chunk_location: absolute path to where chunks will be added