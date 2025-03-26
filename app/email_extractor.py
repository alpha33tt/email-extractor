from flask import Blueprint, request, jsonify
from .email_extractor import EmailExtractor
from .tasks import process_extraction
import os

api = Blueprint('api', __name__)

@api.route('/extract', methods=['POST'])
def extract_emails():
    data = request.json
    source_type = data.get('type')
    
    if source_type == 'website':
        url = data.get('url')
        depth = data.get('depth', 2)
        task = process_extraction.delay(url, depth)
        return jsonify({'task_id': task.id}), 202
        
    elif source_type == 'text':
        text = data.get('text')
        extractor = EmailExtractor()
        emails = extractor.extract_emails_from_text(text)
        return jsonify({'emails': list(emails)}), 200
        
    return jsonify({'error': 'Invalid request'}), 400

@api.route('/results/<task_id>', methods=['GET'])
def get_results(task_id):
    task = process_extraction.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        return jsonify({'status': 'processing'}), 202
    elif task.state == 'SUCCESS':
        return jsonify({'status': 'completed', 'result': task.result}), 200
    else:
        return jsonify({'status': 'failed'}), 500