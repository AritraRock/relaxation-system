# 🧘 AI-Driven Relaxation & Posture Monitoring System

A research-driven prototype combining **biometric sensing**, **computer vision**, and **machine learning** to track a user's relaxation state and yoga posture accuracy. Developed as part of a joint research initiative between **University of Michigan** and **IIT Kharagpur**, built under the **Information Systems Lab (ISL)**.

---

## 🌟 Project Objective

To create an intelligent feedback system that:

1. Captures pre- and post- session vitals (heartbeat, thermal face image, eye tracking)
2. Guides users through a yoga video session
3. Tracks and scores the user's yoga pose accuracy in real time
4. Compares before/after biometric data to assess relaxation

---

## 🔁 System Flow

1. **User Login**  
   Session begins after successful login (session-based auth).

2. **Biometric Data Capture (Pre-Session)**  
   - **Heartbeat**: Captured via webcam or external input (e.g., pulse sensor/webcam RGB variation)  
   - **Thermal Imaging**: Simulated or fetched from device (if supported)  
   - **Eye Tracking**: Browser-based JS tracking or OpenCV model  

3. **Yoga Session Execution**  
   - A **yoga tutorial video** is played on the frontend  
   - User follows along; webcam tracks body posture  
   - Real-time pose estimation using **MediaPipe** or OpenPose

4. **Pose Accuracy Evaluation**  
   - Reference keypoints extracted from video  
   - User keypoints captured and compared using cosine similarity / Euclidean distance  
   - Pose accuracy is scored frame-wise and averaged

5. **Biometric Data Capture (Post-Session)**  
   - Same vitals re-captured  
   - Differences used to compute **relaxation score**

6. **Final Output**  
   - **Pose Accuracy Score**
   - **Relaxation Score**
   - Summary displayed in dashboard

---

## 🧠 Key Features

- 📹 Webcam-based real-time body pose detection
- 🧬 Relaxation score via biometric delta (heartbeat, thermal cues, eye movement)
- 🎥 In-session guidance with embedded yoga videos
- 🔐 Basic login/session management
- 🧪 Integration of Express.js + Flask for seamless JS + Python interoperability

---

## 🛠️ Tech Stack

| Layer            | Tools / Frameworks                         |
|------------------|---------------------------------------------|
| Frontend         | HTML, CSS, JavaScript, Video.js             |
| Backend (Routing)| Express.js                                  |
| ML Inference     | Flask (Python)                              |
| Pose Detection   | MediaPipe / OpenCV / OpenPose               |
| Eye Tracking     | WebGazer.js / OpenCV eye landmarks          |
| DB (Optional)    | MongoDB / JSON (for prototype sessions)     |

---


---

## 🔧 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/relaxation-system.git
cd relaxation-system
```
### 2. Start node server
```bash
cd backend
npm install
npm run dev
```
### 3. start python server ()

# 3. Start Flask backend (comeback to root directory)
```bash
pip install -r requirements.txt
python app.py
```
