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

face_recognize_bp = Blueprint(
    'face_recognize_bp', __name__, url_prefix='/face')


# oidc = OpenIDConnect()


@face_recognize_bp.record_once
def on_blueprint_registered(state):
    logger.info("oidc.init_app")
    # oidc.init_app(state.app)


@face_recognize_bp.route('/recognize', methods=['POST'])
# @oidc.accept_token(require_token=True, render_errors=False, scopes_required=['oidc'])
@rate_limited(limits=['100/d', '30/m'])
def recognize():
    """passing a file for face recognition and save the file in uploads folder and retern the vector id and name if found, and a found varibale true or false indicate the face recognized or not"""
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
    # check file hash exists in database

    
    restult = con.execute("SELECT * FROM users WHERE file_hash = ?", (file_hash,))
    output = restult.fetchone()
    logger.warning('sql output')
    logger.warning(output)

    if output and output['file_hash'] == file_hash:
        try:
            os.remove(file_path)
        except OSError:
            pass
        file_hash = output['file_hash']
        file_id = output['file_id']
        file_path = os.path.join(get_upload_folder(), file_id)
        logger.warning('file_path')
        logger.warning(file_path)
        user_name = output['user_name']
        con.commit()
        con.close()           
        return jsonify({'status': 'success','user_name':user_name, 'file_hash': file_hash, 'message': 'user authenticated, File already exists'})
    try:
        logger.warning("face recognition started")
        result = db.recognize(img=file_path)
        try:
            os.remove(file_path)
        except OSError:
            pass # Delete the file as it already exists
        logger.warning("face recognition completed")
        logger.warning(result)
        if result and result['id']:
            restult = con.execute("SELECT * FROM users WHERE file_hash = ?", (result['id'],))
            output = restult.fetchone()
            logger.info("user recognized")
            user_name = output['user_name']
            con.commit()
            con.close()
            return jsonify({'status': 'success','user_name':user_name, 'message': 'user authenticated'})
        else:
            con.commit()
            con.close()
            return jsonify({'status': 'failed','user_name':None, 'file_hash': file_hash, 'message': 'User not found in database'})
    except Exception as e_e:
        logger.error("error in face recognition")
        logger.error(e_e)
        try:
            os.remove(file_path)
        except OSError:
            pass
        con.commit()
        con.close()
        raise BadRequest(str(e_e)) from e_e

