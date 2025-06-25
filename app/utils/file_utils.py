import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def get_folders():
    base = current_app.config['UPLOAD_FOLDER']
    folders = {
        'photo': os.path.join(base, 'photos'),
        'degree': os.path.join(base, 'degrees'),
        'aadhar': os.path.join(base, 'aadhar')
    }
    for path in folders.values():
        os.makedirs(path, exist_ok=True)
    return folders

def allowed_file(filename):
    return (
        '.' in filename and 
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    )

def save_file(file, folder_key):
    folders = get_folders()
    if file and allowed_file(file.filename):
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        filepath = os.path.join(folders[folder_key], filename)
        file.save(filepath)
        return filename
    return None
