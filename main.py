import cv2
import numpy as np
import face_recognition
import os
import warnings
from tqdm import tqdm
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db

class FaceRecognition:
    def __init__(self, images_path, swap_color_channels, capturing_device, display_video_window_dimension,
                 image_scaling_constant, face_recognition_tolerance_threshold, video_stream_window_name):
        super(FaceRecognition, self).__init__()

        self.images_path = images_path
        self.swap_color_channels = swap_color_channels
        self.capturing_device = capturing_device
        self.display_video_window_dimension = display_video_window_dimension
        self.image_scaling_constant = image_scaling_constant
        self.face_recognition_tolerance_threshold = face_recognition_tolerance_threshold
        self.video_stream_window_name = video_stream_window_name

        # Initialize Firebase
        self.initialize_firebase()
        self.last_detection = {} 
        self.entry_times = {}  # Track entry times for bounding box control

    def initialize_firebase(self):
        # Replace 'path/to/serviceAccountKey.json' with the path to your Firebase service account key file
        cred = credentials.Certificate('face-recognition-1e272-firebase-adminsdk-waq08-899355715e.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://face-recognition-1e272-default-rtdb.firebaseio.com"
        })

    def mark_attendance(self, name):
        ref = db.reference('face-recognition')
        
        # Fetch existing records
        existing_entries = ref.get()
        name_list = [entry['name'] for entry in existing_entries.values()] if existing_entries else []
        
        current_time = datetime.now()
        current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')

        if name not in name_list:
            # Record entry time
            ref.push({
                'name': name,
                'entry_time': current_time_str,
                'exit_time': ''  # Exit time will be updated later
            })
            self.last_detection[name] = current_time  # Record the time of the last detection
            self.entry_times[name] = current_time      # Store entry time for skipping detection
            print(f"Entry time marked for {name}")
        else:
            # Check if 60 seconds have passed since entry time to update exit time
            for key, value in existing_entries.items():
                if value['name'] == name:
                    entry_time = datetime.strptime(value['entry_time'], '%Y-%m-%d %H:%M:%S')
                    if (current_time - entry_time).total_seconds() >= 60:
                        if name in self.last_detection and (current_time - self.last_detection[name]).total_seconds() >= 5:
                            # Update exit time
                            ref.child(key).update({
                                'exit_time': current_time_str
                            })
                            print(f"Exit time updated for {name}")
                        self.last_detection[name] = current_time
                    break

    def recognize(self):
        validation_path = self.images_path
        images_list = []
        class_names = []
        my_image_list = os.listdir(validation_path)

        print("The Validation images that were found are {}{}".format(my_image_list, "\n"))

        print("Reading Images, please wait....")

        for class_name in tqdm(my_image_list):
            current_image = cv2.imread("{}/{}".format(validation_path, class_name))
            images_list.append(current_image)
            class_names.append(os.path.splitext(class_name)[0])

        print("The class names of the images are {}".format(class_names))

        def face_encoding_finder(parse, image_list_object):
            if parse:
                encoding_list = []
                print("Face Encoding is ongoing....")
                for image in tqdm(image_list_object):
                    image = cv2.cvtColor(
                        image, cv2.COLOR_BGR2RGB if self.swap_color_channels else cv2.COLOR_BGR2HSV
                    )
                    face_encoding = face_recognition.face_encodings(image)[0]
                    encoding_list.append(face_encoding)
                return encoding_list

        validation_image_encoding_list = face_encoding_finder(parse=True, image_list_object=images_list)
        print("There were {} face encodings found.{}Encoding Completed Successfully.".format(
            len(validation_image_encoding_list), "\n"))

        # Initializing the WebCamera
        cap = cv2.VideoCapture(self.capturing_device)
        video_feed_dimension = self.display_video_window_dimension

        try:
            while True:
                warnings.filterwarnings('ignore')
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, video_feed_dimension[0])
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, video_feed_dimension[1])

                success, img = cap.read()
                if not success:
                    print("Failed to grab frame")
                    break

                image_s = cv2.resize(img, (0, 0), None,
                                     self.image_scaling_constant,
                                     self.image_scaling_constant)

                image_s = cv2.cvtColor(image_s, cv2.COLOR_BGR2RGB)

                # Encoding Calculation of the WebCamera
                faces_cur_frame = face_recognition.face_locations(image_s)
                encodes_cur_frame = face_recognition.face_encodings(image_s, faces_cur_frame)

                for encode_face, face_location in zip(encodes_cur_frame, faces_cur_frame):
                    matches = face_recognition.compare_faces(known_face_encodings=validation_image_encoding_list,
                                                             face_encoding_to_check=encode_face,
                                                             tolerance=self.face_recognition_tolerance_threshold)
                    face_distance = face_recognition.face_distance(face_encodings=validation_image_encoding_list,
                                                                   face_to_compare=encode_face)
                    print(face_distance)

                    match_index = np.argmin(face_distance)

                    if matches[match_index]:
                        name = class_names[match_index].upper()
                        print(name)
                        current_time = datetime.now()
                        y1, x2, y2, x1 = face_location
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        self.mark_attendance(name)
                        # Only draw bounding box if the detected time and entry time differ by at least 60 seconds
                        if name in self.entry_times and 5<= (current_time - self.entry_times[name]).total_seconds() <=60 :
                            
                            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                            cv2.putText(img, "attndance marked", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 3)
                        else:
                            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 3)

                cv2.imshow(self.video_stream_window_name, img)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                else:
                    continue

        except KeyboardInterrupt:
            print("Code Exited -1")

        cap.release()
        cv2.destroyAllWindows()

# Example usage
images_path = "imagedata"
swap_color_channels = True
capturing_device = 0
display_video_window_dimension = (640, 480)
image_scaling_constant = 0.25
face_recognition_tolerance_threshold = 0.6
video_stream_window_name = "Video Feed"

face_recognition_system = FaceRecognition(
    images_path, swap_color_channels, capturing_device,
    display_video_window_dimension, image_scaling_constant,
    face_recognition_tolerance_threshold, video_stream_window_name
)

face_recognition_system.recognize()
