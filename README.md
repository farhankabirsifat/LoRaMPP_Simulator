# LoRaMPP Simulator

**LoRaMPP (LoRa Multi-Purpose Protocol) Simulator** is a custom Python-based simulation framework for evaluating the performance of a context-aware and adaptive communication protocol designed for LoRa-based IoT networks. It supports detailed parameter control, mobility models, energy usage tracking, and real-time visualization.

---

## 🚀 Features

- ✅ **Custom Protocol Support**: Implements the LoRaMPP protocol for intelligent adaptation of SF, BW, CR.
- 📡 **Environment Simulation**: Supports indoor, urban, suburban, and rural environments.
- 🔋 **Energy Model**: Tracks energy consumption per node.
- 📈 **Performance Metrics**: Collects and reports PDR, delay, collisions, and energy usage.
- 🧭 **Mobility Model**: Optional support for node mobility.
- 🎨 **GUI-based Visualization** (via PyQt): View node status, packet flow, and network behavior.
- 🔄 **Parameter Adaptation Engine**: Automatically adjusts SF/BW based on environment and link quality.

---

## 📂 Project Structure


## File Descriptions

### Core Components
| File | Description |
|------|-------------|
| **core/node.py** | Defines LoRa node behavior including movement, energy consumption, and communication |
| **core/protocol.py** | Implements the LoRaMPP protocol logic including packet handling and error detection |
| **core/channel.py** | Models network channel characteristics including path loss and signal quality |
| **core/energy_model.py** | Calculates energy consumption for different node states (TX, RX, sleep) |

### GUI Components
| File | Description |
|------|-------------|
| **gui/main_window.py** | Main application window with controls and visualization tabs |
| **gui/visualizer.py** | Handles real-time network visualization and packet animation |

### Main Files
| File | Description |
|------|-------------|
| **simulation.py** | Controls the main simulation loop and coordinates components |
| **config.py** | Centralized configuration for simulation parameters |
| **README.md** | Project documentation and usage instructions |
| **requirements.txt** | Python package dependencies for the simulator |

This structure follows a modular design pattern:
1. **Core** - Contains fundamental simulation logic
2. **GUI** - Handles all user interface components
3. **Root** - Main entry points and configuration files

## 🛠️ Installation

```bash
git clone https://github.com/your-username/LoRaMPP-Simulator.git
cd LoRaMPP-Simulator
pip install -r requirements.txt
```
##To run the simulator:
```bash
python simulation.py
```
### 📁 Sample Results
### Results for different scenarios are saved in the /results/ folder:
- indoor_with_mpp.csv, indoor_without_mpp.csv
- urban_with_mpp.csv, urban_without_mpp.csv
- And so on...

### 🧪 Use Cases
- Research on energy-efficient and adaptive IoT protocols
- Demonstrations in IoT and wireless communication labs
- Performance comparisons with traditional LoRaWAN
### 📌 Citation
### If this simulator helps your research or publication, please cite it as:
```bibtex
@misc{kabir2025loramppsim,
  author = {Farhan Kabir},
  title = {LoRaMPP Simulator},
  year = {2025},
  howpublished = {\url{https://github.com/farhankabirsifat/LoRaMPP_Simulator}},
}
```
### 🤝 Contributing
### Pull requests are welcome! If you’d like to add features like:
- Additional mobility models
- MQTT/Cloud integration
- New adaptation algorithms
#### please feel free to contribute or open an issue.
### 📜 License
#### This is a Open source-project
### 📬 Contact
Author: Farhan Kabir Sifat
Email: fksifat12@gmail.com
GitHub: https://github.com/farhankabirsifat
