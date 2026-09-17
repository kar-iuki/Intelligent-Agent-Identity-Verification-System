from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys

# Ensure ai-service root is on the path when running as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.qualityRoutes import quality_bp
from routes.ocrRoutes import ocr_bp
from routes.faceRoutes import face_bp
from routes.livenessRoutes import liveness_bp

load_dotenv()

app = Flask(__name__)
CORS(app)

PORT = int(os.getenv('FLASK_PORT', 5000))
ENV = os.getenv('FLASK_ENV', 'development')

app.register_blueprint(quality_bp, url_prefix='/api/quality')
app.register_blueprint(ocr_bp, url_prefix='/api/ocr')
app.register_blueprint(face_bp, url_prefix='/api/face')
app.register_blueprint(liveness_bp, url_prefix='/api/liveness')


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    # use_reloader=False so concurrently/npm can manage the process cleanly
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=(ENV == 'development'),
        use_reloader=False,
    )
