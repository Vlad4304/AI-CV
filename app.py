import os
import io
import logging
import traceback
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from werkzeug.utils import secure_filename
import tempfile
import json
from ai_analyzer import analyze_resume, generate_anschreiben  # Импорт из твоего текущего файла

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Store session data in files instead of cookies to handle larger data
from flask_session import Session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(tempfile.gettempdir(), 'flask_sessions')
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
Session(app)

# Configure upload settings
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
TEMP_FOLDER = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return "AIAI is running! Use /analyze for resume processing."

@app.route('/analyze', methods=['POST'])
def analyze():
    resume_text = ""
    
    # Check if file or text was uploaded
    if 'resume_file' in request.files and request.files['resume_file'].filename:
        file = request.files['resume_file']
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400
            
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(TEMP_FOLDER, filename)
            file.save(file_path)
            
            # Here you'd call your resume parser (if you have it)
            with open(file_path, 'r', encoding='utf-8') as f:
                resume_text = f.read()
            os.remove(file_path)
            
        except Exception as e:
            return jsonify({"error": f"File processing failed: {str(e)}"}), 500
            
    elif request.form.get('resume_text'):
        resume_text = request.form.get('resume_text')
    else:
        return jsonify({"error": "No resume data provided"}), 400

    # Call your AI analyzer
    try:
        result = analyze_resume(resume_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"AI analysis failed: {str(e)}"}), 500

@app.route('/generate_anschreiben', methods=['POST'])
def generate_cover_letter():
    data = request.json
    if not data or not all(k in data for k in ['resume_text', 'job_description']):
        return jsonify({"error": "Missing data"}), 400
        
    try:
        result = generate_anschreiben(data['resume_text'], data['job_description'])
        return jsonify({"anschreiben": result})
    except Exception as e:
        return jsonify({"error": f"Generation failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
