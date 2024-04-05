import os
from flask import Blueprint, request, jsonify, current_app
# from flask_oidc_ext import OpenIDConnect
from werkzeug.exceptions import BadRequest
from facedb import FaceDB
from core.fn import  get_db_connection,calculate_sha256_hash, get_uniq_file_id, get_upload_folder, check_file_exists
from core.util import rate_limited

from uuid import uuid4
from logging import getLogger
from sqlite3.dbapi2 import Connection
logger = getLogger(__name__)

# Create a FaceDB instance and specify where to store the database
db = FaceDB(
    path="facedata",
)



# Create a table if not exists
con:Connection = get_db_connection()
con.execute('''CREATE TABLE IF NOT EXISTS users
                (file_hash VARCHAR(256) PRIMARY KEY, file_id VARCHAR(256), user_name TEXT)''')
con.commit()
con.close()

face_register_bp = Blueprint(
    'face_register_bp', __name__, url_prefix='/face')


# oidc = OpenIDConnect()


@face_register_bp.record_once
def on_blueprint_registered(state):
    logger.info("oidc.init_app")
    # oidc.init_app(state.app)


@face_register_bp.route('/register', methods=['POST'])
# @oidc.accept_token(require_token=True, render_errors=False, scopes_required=['oidc'])
@rate_limited(limits=['100/d', '30/m'])
def register():
    """register new face"""
    logger.warning("file uploading")
    uploaded_file = request.files['file']
    file_id = get_uniq_file_id(uploaded_file.filename)
    file_path = os.path.join(get_upload_folder(), file_id)
    uploaded_file.save(file_path)
    
    logger.warning("file uploading completed started hashing ")
    
    file_hash = calculate_sha256_hash(file_path)
    logger.warning('file hash')
    logger.warning(file_hash)
    con:Connection =get_db_connection()
    
    restult = con.execute("SELECT * FROM users WHERE file_hash = ?", (file_hash,))
    output = restult.fetchone()
    logger.warning('sql output')
    logger.warning(output)
    if output and output['file_hash'] == file_hash and output['user_name']:
        os.remove(file_path)  # Delete the file as it already exists
        con.commit()
        con.close()
        return jsonify({'status': 'error', 'message': 'user name already exists'})     
    form = request.form
    user_name = form.get('user_name')
    logger.warning('file hash')
    logger.warning(file_hash)

   

    file_path = os.path.join(get_upload_folder(), file_id)
    logger.warning('file_path')
    logger.warning(file_path)
    logger.warning('user_name')
    logger.warning(user_name)
    face_id = db.add(user_name, img=file_path, id=file_hash)
    logger.warning('face_id')
    logger.warning(face_id)
    try:
        con.execute("INSERT INTO users (file_hash, file_id, user_name) VALUES (?, ?, ?)", (file_hash, file_id, user_name))
    except Exception as e:
        logger.error(e)
        os.remove(file_path)
        return jsonify({'status': 'error', 'message': 'user name already exists'})
    logger.info("saved in database")

    con.commit()
    con.close()
    return jsonify({'status': 'success','user_name':user_name, 'message': 'user name registration successful'})


