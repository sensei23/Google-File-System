from flask import Flask
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from read.routes import read_bp
from write.routes import write_bp
from append.routes import append_routes
from delete.routes import delete_routes

app = Flask(__name__)

app.register_blueprint(read_bp)
app.register_blueprint(write_bp)
app.register_blueprint(append_routes)
app.register_blueprint(delete_routes)