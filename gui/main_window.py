import threading

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QGroupBox, QGridLayout, QLabel, QSpinBox, \
    QComboBox, QCheckBox, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QSlider, QSplitter

from core.simulation import LoRaMPPSimulation
from gui.animation_panel import AnimationPanel
from gui.logger import Logger
from utils.metrics import MetricsPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LoRaMPP Simulator")
        self.setGeometry(100, 100, 1200, 900)  # Larger window

        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.central_widget.setLayout(self.main_layout)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #cccccc; }
            QTabBar::tab {
                padding: 8px;
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom: 2px solid #4CAF50;
            }
        """)
        self.main_layout.addWidget(self.tab_widget)

        # Create simulation tab
        self.simulation_tab = QWidget()
        self.simulation_layout = QVBoxLayout()
        self.simulation_layout.setContentsMargins(5, 5, 5, 5)
        self.simulation_tab.setLayout(self.simulation_layout)
        self.tab_widget.addTab(self.simulation_tab, "Simulation")

        # Create visualization tab
        self.visualization_tab = QWidget()
        self.visualization_layout = QVBoxLayout()
        self.visualization_layout.setContentsMargins(0, 0, 0, 0)
        self.visualization_tab.setLayout(self.visualization_layout)
        self.tab_widget.addTab(self.visualization_tab, "Visualization")

        # Setup simulation tab
        self.setup_simulation_tab()

        # Setup visualization tab
        self.setup_visualization_tab()

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        # Internal variables
        self.simulation = None
        self.visualizer = None
        self.area_size = 100
        self.simulation_thread = None

    def setup_simulation_tab(self):
        # Create a splitter to divide the space
        splitter = QSplitter(Qt.Vertical)
        self.simulation_layout.addWidget(splitter)

        # Create control panel
        control_group = QGroupBox("Simulation Configuration")
        control_layout = QGridLayout()
        control_layout.setContentsMargins(10, 15, 10, 15)
        control_group.setLayout(control_layout)
        splitter.addWidget(control_group)

        # Node control
        control_layout.addWidget(QLabel("Number of Nodes:"), 0, 0)
        self.node_spin = QSpinBox()
        self.node_spin.setRange(2, 100)
        self.node_spin.setValue(10)
        control_layout.addWidget(self.node_spin, 0, 1)

        # Area size
        control_layout.addWidget(QLabel("Area Size (m):"), 0, 2)
        self.area_spin = QSpinBox()
        self.area_spin.setRange(50, 1000)
        self.area_spin.setValue(100)
        self.area_spin.valueChanged.connect(self.update_area_size)
        control_layout.addWidget(self.area_spin, 0, 3)

        # Environment selector
        control_layout.addWidget(QLabel("Environment:"), 1, 0)
        self.env_combo = QComboBox()
        self.env_combo.addItems(["Urban", "Suburban", "Rural", "Free Space", "Indoor"])
        self.env_combo.currentTextChanged.connect(self.update_environment_settings)
        control_layout.addWidget(self.env_combo, 1, 1)

        # Mobility checkbox
        self.mobility_check = QCheckBox("Enable Mobility")
        self.mobility_check.setChecked(True)
        control_layout.addWidget(self.mobility_check, 1, 2, 1, 2)

        # Adaptive protocol controls
        control_layout.addWidget(QLabel("Adaptive Protocol:"), 2, 0)
        self.adaptive_check = QCheckBox("Enable LoRaMPP")
        self.adaptive_check.setChecked(True)
        control_layout.addWidget(self.adaptive_check, 2, 1)

        control_layout.addWidget(QLabel("Adaptation Sensitivity:"), 2, 2)
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(1, 10)
        self.sensitivity_slider.setValue(5)
        control_layout.addWidget(self.sensitivity_slider, 2, 3)

        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_container.setLayout(button_layout)
        control_layout.addWidget(button_container, 3, 0, 1, 4)

        # Run button
        self.run_button = QPushButton("Run Simulation")
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.run_button.clicked.connect(self.run_simulation)
        button_layout.addWidget(self.run_button)

        # Timed simulation button
        self.timed_button = QPushButton("Start Timed Simulation")
        self.timed_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #0b7dda; }
        """)
        self.timed_button.clicked.connect(self.start_timed_simulation)
        button_layout.addWidget(self.timed_button)

        # Stop button
        self.stop_button = QPushButton("Stop Simulation")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336; 
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        self.stop_button.clicked.connect(self.stop_simulation)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        # Export button
        self.export_button = QPushButton("Export Results")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800; 
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #e68a00; }
        """)
        self.export_button.clicked.connect(self.export_results)
        button_layout.addWidget(self.export_button)

        # Logger container
        logger_container = QWidget()
        logger_layout = QVBoxLayout()
        logger_container.setLayout(logger_layout)
        splitter.addWidget(logger_container)

        # Logger
        self.logger = Logger()
        logger_layout.addWidget(self.logger)

        # Metrics panel
        self.metrics_panel = MetricsPanel()
        logger_layout.addWidget(self.metrics_panel)

        # Set splitter sizes to give more space to visualization
        splitter.setSizes([250, 600])

    def setup_visualization_tab(self):
        # Create a container for visualization with centered layout
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(container_layout)
        self.visualization_layout.addWidget(container)

        # Add centered placeholder
        self.visualization_placeholder = QLabel("Network visualization will appear here during simulation")
        self.visualization_placeholder.setAlignment(Qt.AlignCenter)
        self.visualization_placeholder.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666;
                font-style: italic;
            }
        """)
        container_layout.addWidget(self.visualization_placeholder)

    def update_area_size(self):
        self.area_size = self.area_spin.value()
        if self.visualizer:
            self.visualizer.area_size = self.area_size
            self.visualizer.ax.set_xlim(0, self.area_size)
            self.visualizer.ax.set_ylim(0, self.area_size)
            self.visualizer.draw()

    def run_simulation(self):
        num_nodes = self.node_spin.value()
        environment = self.env_combo.currentText()
        adaptive = self.adaptive_check.isChecked()

        # Initialize simulation
        self.simulation = LoRaMPPSimulation(
            num_nodes=num_nodes,
            area_size=self.area_size,
            environment=environment.lower(),
            adaptive=adaptive
        )

        # Connect simulation signals
        self.simulation.signals.log_message.connect(self.logger.log)
        self.simulation.signals.packet_sent.connect(self.handle_packet_animation)
        self.simulation.signals.visualization_update.connect(self.update_visualization)
        self.simulation.signals.simulation_finished.connect(self.handle_simulation_finished)

        # Create visualizer
        self.clear_visualization_tab()
        self.visualizer = AnimationPanel(
            self.simulation.nodes,
            self.area_size,
            environment=environment
        )

        # Add to visualization tab with expanding layout
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(container_layout)
        container_layout.addWidget(self.visualizer)
        self.visualization_layout.addWidget(container)

        self.visualizer.draw_nodes()
        self.visualizer.draw()

        # Run simulation
        self.logger.log("Starting simulation...")
        self.run_button.setEnabled(False)
        self.timed_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # Run in a separate thread to keep UI responsive
        self.simulation_thread = threading.Thread(target=self.simulation.run)
        self.simulation_thread.start()

    def handle_packet_animation(self, src, dst, success):
        if self.visualizer:
            self.visualizer.animate_packet(src, dst, success)

    def update_visualization(self):
        if self.visualizer:
            self.visualizer.update_visualization()

    def handle_simulation_finished(self, metrics):
        # Update UI
        self.metrics_panel.update_metrics(metrics)
        self.run_button.setEnabled(True)
        self.timed_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # Update visualization
        if self.visualizer:
            self.visualizer.draw_nodes()
            self.visualizer.draw()

    def start_timed_simulation(self):
        num_nodes = self.node_spin.value()
        environment = self.env_combo.currentText()
        adaptive = self.adaptive_check.isChecked()

        # Initialize simulation
        self.simulation = LoRaMPPSimulation(
            num_nodes=num_nodes,
            area_size=self.area_size,
            environment=environment.lower(),
            adaptive=adaptive
        )

        # Connect simulation signals
        self.simulation.signals.log_message.connect(self.logger.log)
        self.simulation.signals.packet_sent.connect(self.handle_packet_animation)
        self.simulation.signals.visualization_update.connect(self.update_visualization)
        self.simulation.signals.simulation_finished.connect(self.handle_simulation_finished)

        # Create visualizer
        self.clear_visualization_tab()
        self.visualizer = AnimationPanel(
            self.simulation.nodes,
            self.area_size,
            environment=environment
        )

        # Add to visualization tab with expanding layout
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(container_layout)
        container_layout.addWidget(self.visualizer)
        self.visualization_layout.addWidget(container)

        self.visualizer.draw_nodes()
        self.visualizer.draw()

        # Start timed simulation
        self.logger.log("Starting timed simulation with mobility...")
        self.run_button.setEnabled(False)
        self.timed_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # Run in a separate thread
        self.simulation_thread = threading.Thread(
            target=self.simulation.run_with_mobility,
            kwargs={'duration': 30, 'interval': 1}
        )
        self.simulation_thread.start()

    def stop_simulation(self):
        if self.simulation:
            self.simulation.stop()
            self.logger.log("Simulation stopped by user.")
            self.stop_button.setEnabled(False)
            self.run_button.setEnabled(True)
            self.timed_button.setEnabled(True)

    def export_results(self):
        if self.simulation:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Results",
                "",
                "CSV Files (*.csv)"
            )

            if file_path:
                # Ensure .csv extension
                if not file_path.lower().endswith('.csv'):
                    file_path += '.csv'

                export_path = self.simulation.export_results_to_csv(filename=file_path)
                self.logger.log(f"✅ Results exported to: {export_path}")
                QMessageBox.information(self, "Export Successful",
                                        f"Results exported to:\n{export_path}")

    def clear_visualization_tab(self):
        # Remove all widgets from visualization tab
        for i in reversed(range(self.visualization_layout.count())):
            widget = self.visualization_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
                self.visualization_layout.removeWidget(widget)

        # Add placeholder back if no visualization
        if self.visualization_layout.count() == 0:
            self.setup_visualization_tab()

    def update_environment_settings(self, environment):
        """Update area size based on selected environment"""
        env_size_map = {
            "Indoor": 50,
            "Urban": 100,
            "Suburban": 200,
            "Rural": 500,
            "Free Space": 1000
        }

        if environment in env_size_map:
            self.area_spin.setValue(env_size_map[environment])
            self.area_size = env_size_map[environment]

        # Update channel model if simulation exists
        if self.simulation:
            self.simulation.channel.environment = environment.lower()
            self.logger.log(f"Environment changed to {environment}")
