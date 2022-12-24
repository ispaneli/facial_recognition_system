import uuid

import cv2
import numpy as np
import face_recognition as fr


def img_to_encoding(img_path: str, model_tag: str = "cnn") -> np.ndarray:
    """
    Converts a face photo to encoding.

    :param str img_path: The path to the image.
    :param str model_tag: The name of the model that will process the photo.
                          The 'hog' model is faster, the 'cnn' model is more accurate.
    :return: Encoding of the biggest face.
    :rtype: np.ndarray
    """
    rgb_layouts = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)
    face_boxes = fr.face_locations(rgb_layouts, model=model_tag)

    if not face_boxes:
        raise ValueError("There is no face in the photo.")

    if len(face_boxes) > 1:
        # Search for box with the maximum area.
        areas = (
            abs(box[0] - box[2]) * abs(box[1] - box[3])
            for box in face_boxes
        )
        main_face_idx = np.argmax(areas)
        face_boxes = (face_boxes[main_face_idx], )

    return fr.face_encodings(rgb_layouts, face_boxes)[0]


DATABASE_AS_MAP = dict()
threshold = 0.8
def who_is_it(img_path: str) -> uuid.UUID:
    unknown_encoding = img_to_encoding(img_path)

    for user_id, encodings in DATABASE_AS_MAP.items():
        prob = fr.compare_faces(np.array(encodings), unknown_encoding)

        if prob > threshold:
            return user_id

    raise ValueError("There is an unregistered user in the photo.")

