import glob
import pickle 
import hashlib
from os.path import basename, join, relpath, splitext, exists
from os import getcwd
from werkzeug.exceptions import BadRequest
from logging import getLogger
from typing import  List
from sqlite3.dbapi2 import Connection
import sqlite3
from uuid import uuid4
logger = getLogger(__name__)
from datetime import datetime


UPLOAD_FOLDER =  join(getcwd(), 'uploads')
FILE_UPLOAD_INDEX="file_upload_idx_v2"
def get_upload_folder():
    """get upload folder"""
    
    return UPLOAD_FOLDER

def get_db_connection() -> Connection:
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
def check_file_exists(file_id):
    """ get the extension of file from file name"""
    exact_file_name = join(UPLOAD_FOLDER, file_id)
    logger.info("exact_file_name")
    logger.info(exact_file_name)
    if exists(exact_file_name):
        return exact_file_name
    return None

def get_ext(file_name):
    """ get the extension of file from file name"""
    
    return splitext(file_name)[1]

def get_file_name(file_name):
    """ get the  file_name without extension of file from file name"""
    
    return splitext(file_name)[0]

def get_all_modules(dir_name, version="v1"):
    """Returns a list of relative paths to all modules in the current directory."""
    py_files = glob.glob(join(dir_name, "**_"+version+"/**.py"))
    modules = [f[:-3] for f in py_files if not f.endswith("__init__.py")]
    relative_paths = [relpath(f, join(
        dir_name, "../")).replace("/", ".").replace("\\", ".")+":"+basename(f)+"_bp" for f in modules]
    return relative_paths




def calculate_sha256_hash(file_path):
    """Calculate the SHA256 hash of a file"""
    hash_obj = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def hash_sha256(data):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(data.encode('utf-8'))
    return sha256_hash.hexdigest()

def get_uniq_file_id(file_name):
    """ get a unique file name with two uuids """
    logger.info('get_uniq_file_id')
    ext = get_ext(file_name)
    restricted_extensions = ['sh','exe', 'msi', 'bat', 'dll', 'sys', 'tar', 'zip','tar','rar', 'php', 'asp', 'js', 'ini', 'config', 'db', 'sql', 'bak', 'old', 'swf', 'flv','mp4','mp3']
    if ext in restricted_extensions:
        raise BadRequest(description="Sorry, we can't process this file type.")
    current_date = datetime.now().strftime("_%d%m%y_%H%M%S")
    uuid = str(uuid4())
    uniq_file_id = 'file_'+current_date+'_'+uuid+ext
    return uniq_file_id
