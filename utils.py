
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import cv2
from collections import deque
import requests


# better models - 6th(64 ,50), 3rd(64,20) and 256(20)

activity_model = load_model('models/lnrc_64_2.h5')
weapon_model = load_model('models/WEAPON_MODEL_128.h5')

# classes_list = ["suspicious", "normal"]
classes_list = ["normal", "suspicious"]

SEQUENCE_LENGTH = 50
# image_height, image_width = 256, 256
# image_height, image_width = 128, 128
image_height, image_width = 64, 64


ALERT_CRITICLE_RATIO = 0.2

sinch_from_number = "447520652529"


def send_sms_to_auth_sinch(to):
    sinch_url = ' https://sms.api.sinch.com/xms/v1/4a6c76e897ca4eddae6b53d91ba12281/batches'

    body = {
        "from": sinch_from_number,
        "to": [to],
        "body": "Some Suspicious Activity Detected In Your Camera.\n\nInform To Police Station: https://report_via_sms.herokuapp.com/to_police/ \n\nOR Call: 100"
    }

    headers = {
        "Authorization": "Bearer 8117304fea5f4b958c2c1de79b3f6554"
    }

    r = requests.post(sinch_url, json=body, headers=headers)

    if r.status_code == 200 or r.status_code == 201:
        print('Alert Sent to Authority!')


def predict_on_realtime(output_file_path, SEQUENCE_LENGTH):

    video_reader = cv2.VideoCapture(0)

    orignal_video_width = int(video_reader.get(cv2.CAP_PROP_FRAME_WIDTH))
    orignal_video_height = int(video_reader.get(cv2.CAP_PROP_FRAME_HEIGHT))

    video_writer = cv2.VideoWriter(output_file_path, cv2.VideoWriter_fourcc('M', 'P', '4', 'V'),
                                   video_reader.get(cv2.CAP_PROP_FPS), (orignal_video_width, orignal_video_height))

    frames_queue = deque(maxlen=SEQUENCE_LENGTH)
    predictions = []

    predicted_class_name = ''

    while video_reader.isOpened():

        ok, frame = video_reader.read()

        if not ok:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):  # taking keyboard input 'q' to brake it
            cv2.destroyAllWindows()
            break

        resized_frame = cv2.resize(frame, (image_height, image_width))
        normalized_frame = resized_frame / 255
        resized_frame_weapon = cv2.resize(frame, (128, 128))
        normalized_frame_weapon = resized_frame_weapon / 255

        isWeapon = weapon_model.predict(
            np.expand_dims(normalized_frame_weapon, axis=0))[0]

        print(isWeapon)
        if isWeapon > 0.5:
            labeled_frame = cv2.putText(
                frame, f'Weapon Detected', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), cv2.LINE_4)

        frames_queue.append(normalized_frame)
        if len(frames_queue) == SEQUENCE_LENGTH:
            predicted_label_probabilities = activity_model.predict(
                np.expand_dims(frames_queue, axis=0))[0]
            predicted_label = np.argmax(predicted_label_probabilities)

            predictions.append(predicted_label)
            predicted_class_name = classes_list[predicted_label]

            if (predicted_class_name == 'normal'):
                labeled_frame = cv2.putText(frame, f'Activity: {predicted_class_name}', (
                    50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), cv2.LINE_4)
                cv2.imshow('frame', labeled_frame)

            elif (predicted_class_name == 'suspicious'):
                labeled_frame = cv2.putText(frame, f'Activity: {predicted_class_name}', (
                    50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (226, 122, 19), cv2.LINE_4)
                cv2.imshow('frame', labeled_frame)

        video_writer.write(frame)

    video_reader.release()
    video_writer.release()
