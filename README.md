# Driver Monitoring System 🚗👀

_Developed by Mohab Alwakeel_

A real-time drowsiness and distraction detection system for drivers using **OpenCV**, **MediaPipe**, and a clean **Tkinter GUI**.

---

## 🔧 Features

- Eye Aspect Ratio (EAR) drowsiness detection
- Head pose tracking (Yaw & Pitch) for distraction
- Tkinter-based GUI for ease of use
- Instant alarm sound when driver is not alert

---

## 📁 Project Structure

driver-monitoring-system
│
├── src/
│ └── main.py → Source code
│
├── audio/
│ └── audio2.mp3 → Alarm sound
│
├── requirements.txt → Python dependencies
├── README.md → This file
└── .gitignore

---

## ⚙️ Installation

> Make sure Python **3.8+** is installed and your webcam is connected.

### 1) Clone the repository

```bash
git clone https://github.com/alwakeelmhb/driver-monitoring-system.git
cd driver-monitoring-system

```

2. Install dependencies

```bash
pip install -r requirements.txt

```

3. Run the application

```bash
cd src
python main.py

```

---

## 🎯 Notes

- 🔉 Ensure that `audio/audio2.mp3` exists — this is the alarm sound.
- 📸 When you run the script, it will automatically access your webcam (allow access if asked).
- 🛑 An alarm + red alert will appear if the system detects closed eyes or distracted head movement.

---

## 🚀 Future Improvements

- Save alert logs to a file
- Add night mode UI
- Export as standalone `.exe` app (PyInstaller)

---

## 🤝 Contributions

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---
