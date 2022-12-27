from pathlib import Path
from typing import BinaryIO

import cv2
import numpy as np
import face_recognition as fr
from pyaml_env import parse_config

from models import MONGO_DB


CONFIG_PATH = Path(__file__).parents[2] / "config.yaml"
CONFIG = parse_config(str(CONFIG_PATH))


async def photo_stream_to_encoding(
    photo_stream: BinaryIO,
    model_tag: str = 'cnn'
) -> list[float]:
    """
    Converts a face photo to encoding.

    :param BinaryIO photo_stream: The photo as byte string.
    :param str model_tag: The name of the model that will process the photo.
                          The 'hog' model is faster, the 'cnn' model is more accurate.
    :return: Encoding of the biggest face.
    :rtype: list[float]
    """
    photo_as_np_array = np.asarray(bytearray(photo_stream.read()), dtype=np.uint8)
    rgb_layouts = cv2.imdecode(photo_as_np_array, cv2.COLOR_BGR2RGB)
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

    return fr.face_encodings(rgb_layouts, face_boxes)[0].tolist()


async def who_is_it(
    photo_stream: BinaryIO,
    model_tag: str = 'cnn'
) -> str | None:
    """
    Searches for the employee in database of biometrics.

    :param BinaryIO photo_stream: The photo as byte string.
    :param str model_tag: The name of the model that will process the photo.
                          The 'hog' model is faster, the 'cnn' model is more accurate.
    :return: ID of the employee or None
    :rtype: str
    """
    unknown_encoding = photo_stream_to_encoding(photo_stream, model_tag=model_tag)

    async for biometric in MONGO_DB.biometrics.find():
        prob = 0
        for encoding in biometric['encodings']:
            prob += fr.compare_faces(np.array(encoding), unknown_encoding)
        prob /= len(biometric['encodings'])

        if prob > CONFIG['model']['prob_threshold']:
            return str(biometric['_id'])
