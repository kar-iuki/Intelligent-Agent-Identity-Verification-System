import logging

import numpy as np

logger = logging.getLogger(__name__)

FACE_MATCH_THRESHOLD = 70.0

face_app = None
model_init_error = None


def _initialise_face_app():
    """Load InsightFace buffalo_l once. Records errors instead of crashing import."""
    global face_app, model_init_error

    try:
        from insightface.app import FaceAnalysis

        # InsightFace: ctx_id=-1 selects CPU (ctx_id>=0 is a GPU device index)
        app = FaceAnalysis(name='buffalo_l')
        app.prepare(ctx_id=-1, det_size=(640, 640))
        face_app = app
        model_init_error = None
        logger.info('InsightFace buffalo_l model loaded successfully')
    except Exception as exc:
        face_app = None
        model_init_error = str(exc)
        logger.error('Failed to initialise InsightFace model: %s', exc)


_initialise_face_app()


def ensure_model_ready():
    """Raise RuntimeError if the InsightFace model is unavailable."""
    if face_app is None:
        raise RuntimeError(
            model_init_error
            or 'InsightFace model is not initialised. Check model download and dependencies.'
        )


def detect_and_crop_face(image):
    """
    Detect faces and return the largest face object (contains embedding).
    Returns (face, error_message).
    """
    ensure_model_ready()

    faces = face_app.get(image)

    if not faces:
        return None, 'No face detected in image'

    if len(faces) == 1:
        return faces[0], None

    def _bbox_area(face):
        x1, y1, x2, y2 = face.bbox.astype(float)
        return max(0.0, x2 - x1) * max(0.0, y2 - y1)

    largest = max(faces, key=_bbox_area)
    return largest, None


def generate_embedding(image):
    """
    Return (embedding ndarray, error_message).
    embedding is None when no face is detected.
    """
    face, error = detect_and_crop_face(image)
    if face is None:
        return None, error

    embedding = getattr(face, 'normed_embedding', None)
    if embedding is None:
        embedding = getattr(face, 'embedding', None)

    if embedding is None:
        return None, 'Face detected but embedding could not be extracted'

    return np.asarray(embedding, dtype=np.float64), None


def compute_face_match_score(embedding1, embedding2):
    """Cosine similarity scaled to 0–100."""
    e1 = np.asarray(embedding1, dtype=np.float64)
    e2 = np.asarray(embedding2, dtype=np.float64)

    denom = np.linalg.norm(e1) * np.linalg.norm(e2)
    if denom == 0:
        return 0.0

    cosine = float(np.dot(e1, e2) / denom)
    # InsightFace normed embeddings → cosine typically in [-1, 1];
    # project example uses percentage form (e.g. 87.4 ≈ 0.874 * 100)
    score = max(0.0, min(100.0, cosine * 100.0))
    return round(score, 4)


def verify_face_match(document_image, selfie_image):
    """
    Compare ArcFace embeddings from document photo and live selfie.
    """
    document_embedding, document_error = generate_embedding(document_image)
    selfie_embedding, selfie_error = generate_embedding(selfie_image)

    document_face_detected = document_embedding is not None
    selfie_face_detected = selfie_embedding is not None

    if not document_face_detected or not selfie_face_detected:
        errors = []
        if not document_face_detected:
            errors.append(f'Document: {document_error or "No face detected in image"}')
        if not selfie_face_detected:
            errors.append(f'Selfie: {selfie_error or "No face detected in image"}')

        return {
            'faceMatchScore': 0.0,
            'documentFaceDetected': document_face_detected,
            'selfieFaceDetected': selfie_face_detected,
            'matched': False,
            'message': '; '.join(errors),
        }

    score = compute_face_match_score(document_embedding, selfie_embedding)

    return {
        'faceMatchScore': score,
        'documentFaceDetected': True,
        'selfieFaceDetected': True,
        'matched': score > FACE_MATCH_THRESHOLD,
    }
