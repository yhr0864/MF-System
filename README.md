# 🚀🤖 Automated High-Throughput Nanoparticle Synthesis System ⚙️💡 (TO BE CONTINUED)

![](https://gitlab.kit.edu/haoran.yu/mf-system/-/raw/new_interface/images/MF.png)

## 📝 Project Overview:

This project automates a **high-throughput system for accelerated production and characterization of organic semiconductor nanoparticle dispersions** for photovoltaic applications. The system integrates a gantry-based sample handler, turntables for vial handling, a microfluidic synthesis unit, and characterization tools for dynamic light scattering (DLS) and UV-Vis spectroscopy. The software enables precise control of process parameters, sample handling, and measurement workflows to achieve high-throughput optimization.
 
### 🌟 Core Capabilities
- Automated synthesis of nanoparticle dispersions using **precision microfluidics**
- Integrated characterization via **Dynamic Light Scattering (DLS)** and **UV-Vis spectroscopy**
- Robotic sample handling with **gantry systems** and **Turntables**

## 🔬 System Components & Hardware Integration 🔌

### 🧪 Synthesis Module
**Cetoni Nemeys M Syringe Pump System**  
<div align="center">
  <img src="https://gitlab.kit.edu/haoran.yu/mf-system/-/raw/new_interface/images/pumps.png" width="400" alt="System Architecture">
  <p><strong>Figure 1:</strong> Syringe Pump System</p>
</div>

<div align="center">
  <img src="https://gitlab.kit.edu/haoran.yu/mf-system/-/raw/new_interface/images/micro_chip.png" width="400" alt="System Architecture" width="400" alt="System Architecture">
  <p><strong>Figure 2:</strong> Micro Chip</p>
</div>

- Precision fluid handling with adjustable flow rates 
- Integrated microfluidic mixer chips for nanoparticle synthesis  
- **Control Method:** Cetoni offered SDK integration  
- Centralized configuration via `hardware_config.yaml`

### 🎛️ Pneumatic & Motion Control Module
**Custom Microcontroller System** ([Arduino Mega 2560](https://docs.arduino.cc/hardware/mega-2560/))
![Pneumatic & Motion Unit](https://gitlab.kit.edu/haoran.yu/mf-system/-/raw/new_interface/images/characterization.png)

- Controls 4 pneumatic actuators for immersion probe positioning  
- Manages rotary table motion for vial handling  
- **Control Method:** Custom C/C++ scripts via Serial/UART 

### 📊 Characterization Module

#### 🔍 Dynamic Light Scattering (DLS)  
**Microtrac Nanotrac Flex** ([DLS Analyzer](https://www.microtrac.com/products/dynamic-light-scattering/nanotrac-flex/))
- Measures particle size distribution: **range ???**  
- **Control Method:** Remote API through Microtrac Software and SDK

#### 🌈 UV-Vis Spectroscopy 
**Sarspec Absorbance Flex** ([UV-Vis](https://www.sarspec.com/products/spectrometers/flex))
- Spectral range: **range ???** (1 nm resolution)  
- Fiber-optic immersion probe with 10 mm pathlength  
- **Control Method:** Direct SDK control via Python 

---

## 🎯 Workflow Overview
![Workflow](https://gitlab.kit.edu/haoran.yu/mf-system/-/raw/new_interface/images/workflow.png)  
1. **Synthesis Phase**
   - Microfluidic mixing with parameter optimization
   - Automated vial filling via rotary table

2. **Characterization Phase**
   - DLS for nanoparticle size distribution
   - UV-Vis for optical absorption analysis
   - Probe cleaning/repositioning between measurements

---

## ⚙️ Control Infrastructure
| Component                | Protocol                | Interface             |
|--------------------------|-------------------------|-----------------------|
| Syringe Pumps            | Modbus-TCP              | Vendor SDK            |
| DLS System               | REST API                | Vendor Software & SDK |
| UV-Vis Spectrometer      | USB-HID                 | Vendor SDK            |
| Pneumatic System         | Serial (9600 baud)      | Custom C/C++ Firmware |

---

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
