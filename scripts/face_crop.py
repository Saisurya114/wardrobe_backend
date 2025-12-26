import cv2
import numpy as np
import mediapipe as mp
from PIL import Image

mp_face = mp.solutions.face_detection

def crop_below_face(image: Image.Image, padding_ratio=0.15) -> Image.Image:
    """
    Detects face and crops image below it.
    If no face detected, returns original image.
    """

    img_np = np.array(image)
    h, w, _ = img_np.shape

    with mp_face.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        results = face_detection.process(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))

        if not results.detections:
            return image  # No face → keep original

        # Take first detected face
        bbox = results.detections[0].location_data.relative_bounding_box
        face_bottom = int((bbox.ymin + bbox.height) * h)

        # Add padding so neckline isn’t cut
        face_bottom = min(h, int(face_bottom + padding_ratio * h))

        cropped = img_np[face_bottom:, :, :]
        return Image.fromarray(cropped)
