# 🚀🤖 Microfluidic System Automation ⚙️💡 (TEMPLATE README FILE)

![](https://gitlab.kit.edu/haoran.yu/mf-system/-/raw/main/images/MF.png)

## 📝 Description:

This project automates a microfluidic system using a state machine-based automation process. It includes hardware control, real-time monitoring, and a GUI (PyQt6) for user interaction.

## 🚀 Project Overview
This project automates a microfluidic system using **state machine-based automation**. It includes:
- **Hardware control** for valves, robotic arms, turntables, and syringe pumps.
- **Multi-threading** to ensure smooth execution without UI blocking.
- **PyQt6 GUI** with radio buttons, logs, and start/stop controls.
- **Serial Communication** using `pyserial`.
- **Logging & Monitoring** for real-time experiment tracking.

---

## 📂 Folder Structure

```
project-root/
│── requirements.txt         # Dependencies list
│── README.md                # Project documentation
│── resources/               # Icons, UI assets, etc.
│── dist/                    # Compiled EXE output (after build)
│── src/
│   ├── mf_system
│       ├── hardware/        # Low-level hardware control scripts
│       ├── logic/           # State machine logic
│       ├── ui/              # PyQt6 UI components
│── tests/                   # Unit tests
│── .github/workflows/       # CI/CD pipeline
```

---

## 🔧 Installation & Setup

### 1️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 2️⃣ Run the Application
```sh
python main.py
```

### 3️⃣ Build Executable (Windows)
```sh
pyinstaller --onefile --noconsole --icon=resources/app.ico main.py
```
- The **EXE file** will be in the `dist/` folder.

---

## 📜 Configuration
Modify `config.yaml` to customize settings, such as:
```yaml
hardware:
  port: COM3
  baudrate: 115200
```

---

## 🛠 CI/CD & Deployment
- **Build Automation:** GitHub Actions builds the EXE on each commit.
- **Sync to GitLab:** Uses a workflow to mirror GitHub repo.
- **Deployment:** Copies the latest `dist/main.exe` to a remote server.

---

## 🎯 Usage Guide

### 📌 Start Experiment
1. Select an option:
   - 🔹 Dispense Only
   - 🔹 Measure Only
   - 🔹 Both
2. Click **"Start"** to begin the process.
3. The system logs will appear in the UI.

### 📌 Stop Experiment
- Click **"Stop"** to halt execution.

---

## 📷 Screenshots
*(Add images of your GUI and system in action here!)*

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).

---

## ❓ Troubleshooting & FAQ

### ❓ Why is my serial port not detected?
Check `Device Manager` and update the port in `config.yaml`.

### ❓ The GUI freezes while running!
Ensure multi-threading is correctly implemented in the experiment thread.

---

## 📞 Contact
For issues or contributions, open an issue or contact the project maintainer.


## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
