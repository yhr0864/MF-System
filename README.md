# 🚀🤖 Automated High-Throughput Nanoparticle Synthesis System ⚙️💡 (TO BE CONTINUED)

![](https://gitlab.kit.edu/haoran.yu/mf-system/-/raw/main/images/MF.png)

## 📝 Description:

This project automates a **high-throughput system for accelerated production and characterization of organic semiconductor nanoparticle dispersions** for photovoltaic applications. The software integrates a state machine-based automation process with hardware control, real-time monitoring, and a PyQt6 GUI for user interaction.

---

## 🚀 Project Overview

### 🌟 Core Capabilities
- Automated synthesis of nanoparticle dispersions using **precision microfluidics**
- Integrated characterization via **Dynamic Light Scattering (DLS)** and **UV-Vis spectroscopy**
- Robotic sample handling with **gantry systems** and **Turntables**

### 🔬 System Components
1. **Synthesis Module**
   - Cetoni Nemeys M Syringe Pump System (SDK-controlled)
   - Microfluidic mixer chips
   - Automated turntable filling (microcontroller-driven)

2. **Characterization Module**
   - **Dynamic Light Scattering**: Microtrac Nanotrac Flex (remote-controlled)
   - **UV-Vis Spectroscopy**: Sarspec Absorbance Flex (SDK-controlled)
   - Immersion probes with pneumatic actuation

3. **Control Infrastructure**
   - Custom microcontroller scripts (C-based) for pneumatic/hardware control
   - PySerial communication for device interfacing
   - Centralized configuration via `hardware_config.yaml`

### 🎯 Workflow Overview
![Workflow](https://example.com/workflow.jpg)  
1. **Synthesis Phase**
   - Microfluidic mixing with parameter optimization
   - Automated vial filling via rotary table

2. **Characterization Phase**
   - DLS for nanoparticle size distribution
   - UV-Vis for optical absorption analysis
   - Probe cleaning/repositioning between measurements

---

## 🔌 Hardware Integration

### 🧪 Microfluidic Control System

**Cetoni Nemeys M Syringe Pump System**  
- Precision fluid handling 
- Integrated microfluidic mixer chips
- **Control Method:** Native Python SDK integration  

### 🎛️ Pneumatic Control Unit
![Pneumatic Control Unit](https://example.com/p.jpg)  
**Custom Microcontroller System** (Arduino Mega 2560)
- Controls 4 pneumatic actuators for probe immersion
- Manages rotary table positioning
- **Control Method:** Custom C++ scripts via Serial

### 📏 Nanoparticle Characterization
![Nanoparticle Characterization](https://example.com/nano.jpg) 
**Microtrac Nanotrac Flex DLS**
- Measures particle size distribution (1-1000 nm range) ???
- Integrated temperature control
- **Control Method:** Remote API through Microtrac Software

### 🌈 Optical Spectroscopy
![Optical Spectroscopy](https://example.com/spect.jpg) 
**Sarspec Absorbance Flex UV-Vis**
- 200-850 nm wavelength range ???
- Fiber-optic immersion probe
- **Control Method:** Direct SDK control

## 📂 Folder Structure

```
project-root/
│── requirements.txt         # Dependencies list
│── README.md                # Project documentation
│── resources/               # Icons, UI assets, etc.
│── src/
│   ├── mf_system
│       ├── hardware/        # Low-level hardware control scripts
│       ├── logic/           # State machine logic
│       ├── ui/              # PyQt6 UI components
│── tests/                   # Unit tests
│── .github/workflows/       # CI/CD pipelines
```

---

## 🔧 Installation & Setup

### 1️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 2️⃣ Configure Hardware Setups
Modify `hardware_config.yaml` to customize settings, such as:
```yaml
Arduino:
   port: "COM14"
   baudrate: 9600
   timeout: 0.1
```

### 3️⃣ Run the Application
```sh
python main.py
```

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

## 📞 Contact
For issues or contributions, open an issue or contact the project maintainer.


## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
