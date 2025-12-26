import mediapipe as mp
import numpy as np
from PIL import Image


mp_face = mp.solutions.face_detection


def crop_below_face(image: Image.Image) -> Image.Image:
    img_np = np.array(image)
    h, w, _ = img_np.shape

    with mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face:
        result = face.process(img_np)

        if not result.detections:
            return image  # no face → return original

        bbox = result.detections[0].location_data.relative_bounding_box
        y_min = int((bbox.ymin + bbox.height) * h)

        y_min = max(0, min(y_min, h))

        cropped = img_np[y_min:h, 0:w]
        return Image.fromarray(cropped)

