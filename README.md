

---

# Face Recognition Attendance System with Payroll Integration

## Overview

This project implements an **automated attendance system** using **face recognition** technology. It can recognize multiple faces at a time and automatically mark attendance for each recognized individual. The system logs the **entry and exit times** of employees, integrates with the **payroll system**, and ensures accurate tracking of working hours. 

Currently, **liveliness detection** (to prevent spoofing with photos or videos) is under development to improve security.

## Features

- **Multi-Face Recognition**: The system can recognize and identify more than one person simultaneously, making it efficient for group attendance marking.
- **Attendance Logging**: Entry and exit times are automatically recorded for each recognized individual.
- **Payroll Integration**: The system calculates working hours based on the recorded entry and exit times, which is then passed to the payroll system for salary calculation.
- **Liveliness Detection (In Progress)**: Ongoing work on detecting whether the face belongs to a real person or a static image/video to prevent fraudulent attendance marking.

## How It Works

1. **Face Detection and Recognition**: The system uses advanced face detection algorithms to identify individuals. It works in real-time and can recognize multiple faces simultaneously.
2. **Attendance Marking**: Once a face is recognized, the system updates the attendance record with the employee's entry or exit time.
3. **Payroll Integration**: The system calculates the total working hours of an individual based on their attendance and sends this information to the payroll system for salary processing.
4. **Ongoing Liveliness Detection**: The system is currently being updated to include liveliness detection, ensuring that only real, live faces are recognized.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/face-recognition-attendance.git
   cd face-recognition-attendance
   ```

2. **Install dependencies**:

   pip install -r requirements.txt
   

3. **Setup the system**:
   - Make sure you have a camera or an IP camera setup.
   - Configure the payroll system integration as per your organization's requirements.

4. **Run the system**:
   ```bash
   python main.py
   ```

## Technologies Used

- **Python**: For the core logic of the system.
- **OpenCV**: For face detection and recognition.
- **dlib**: For facial feature extraction and matching.
- **firebase**: For storing attendance data.
  

## Future Improvements

- **Liveliness Detection**: A key feature in progress to detect whether a person is alive to prevent spoofing using photos or videos.
- **Improved UI**: Development of a user-friendly interface for easy access to reports.
- **Mobile App Integration**: A mobile app for real-time notifications and access to attendance data.

## Contribution

Feel free to fork this repository, create issues, and submit pull requests to improve this project. Contributions towards liveliness detection and system optimizations are welcome.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Feel free to modify it according to your specific implementation and add any additional instructions or features you've worked on!
