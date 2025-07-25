import math
import time

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class AnimationPanel(FigureCanvas):
    def __init__(self, nodes, area_size=100, environment="urban"):
        # Create larger figure for better visualization
        self.figure = Figure(figsize=(10, 8), dpi=100)
        super().__init__(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.nodes = nodes
        self.area_size = area_size
        self.environment = environment
        self.packet_lines = []
        self.connection_lines = []  # Store network topology lines
        self.motion_markers = []  # Store motion detection markers
        self.last_update = time.time()
        self.setup_plot()

        # Set size policy to expand
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("background-color: white; border: 1px solid #cccccc; border-radius: 4px;")

    def setup_plot(self):
        self.ax.clear()
        self.ax.set_title(f"LoRa Network: {len(self.nodes)} Nodes ({self.environment})", fontsize=12)
        self.ax.set_xlabel("X Position (m)", fontsize=10)
        self.ax.set_ylabel("Y Position (m)", fontsize=10)
        self.ax.set_xlim(0, self.area_size)
        self.ax.set_ylim(0, self.area_size)

        # Adjust font sizes
        self.ax.tick_params(axis='both', which='major', labelsize=9)

        # Environment-specific grid styling
        if self.environment.lower() == "indoor":
            self.ax.grid(True, linestyle='-', alpha=0.5, color='#cccccc')
            # Add walls/obstacles for indoor visualization
            self.ax.axvline(x=self.area_size / 3, color='gray', linestyle='-', alpha=0.5, linewidth=2)
            self.ax.axvline(x=2 * self.area_size / 3, color='gray', linestyle='-', alpha=0.5, linewidth=2)
            self.ax.axhline(y=self.area_size / 2, color='gray', linestyle='-', alpha=0.5, linewidth=2)
        else:
            self.ax.grid(True, linestyle='--', alpha=0.7)

        # Draw nodes
        self.draw_nodes()

        # Draw network connections
        self.draw_network_topology()

    def draw_nodes(self):
        """Draw all nodes with their current positions and status"""
        # Clear previous elements
        if hasattr(self, 'scatter'):
            try:
                self.scatter.remove()
            except:
                pass

        # Clear previous motion markers
        for marker in self.motion_markers:
            try:
                marker.remove()
            except:
                pass
        self.motion_markers = []

        # Clear previous text annotations
        if hasattr(self, 'node_texts'):
            for text in self.node_texts:
                try:
                    text.remove()
                except:
                    pass
            self.node_texts = []

        if hasattr(self, 'energy_texts'):
            for text in self.energy_texts:
                try:
                    text.remove()
                except:
                    pass
            self.energy_texts = []

        # Get current positions
        self.x = [node.position[0] for node in self.nodes]
        self.y = [node.position[1] for node in self.nodes]
        self.colors = [node.get_energy_color() for node in self.nodes]
        self.sizes = [40 + node.spreading_factor * 5 for node in self.nodes]  # Larger sizes

        # Create new scatter plot
        self.scatter = self.ax.scatter(self.x, self.y, c=self.colors, s=self.sizes, alpha=0.8, edgecolors='black',
                                       zorder=5)

        # Create text annotations
        self.node_texts = []
        self.energy_texts = []

        for i, node in enumerate(self.nodes):
            # Node ID and parameters
            node_text = self.ax.text(
                self.x[i] + 1.5, self.y[i] + 1.5,  # Slightly larger offset
                f"{node.node_id}",
                fontsize=9,
                zorder=6
            )
            self.node_texts.append(node_text)

            # Energy text - always show energy
            energy_text = self.ax.text(
                self.x[i] - 5, self.y[i] - 5,
                f"E:{node.energy:.1f}J\nSF:{node.spreading_factor}",
                fontsize=8,
                color='gray',
                zorder=6
            )
            self.energy_texts.append(energy_text)

            # Add motion detection marker
            if node.motion_detected:
                marker = self.ax.plot(
                    node.position[0], node.position[1],
                    'bo', markersize=10, alpha=0.5, zorder=4
                )[0]
                self.motion_markers.append(marker)

    def update_visualization(self):
        """Update all visualization elements"""
        current_time = time.time()
        if current_time - self.last_update < 0.2:  # Limit updates to 5fps
            return

        self.last_update = current_time
        self.draw_nodes()
        self.draw_network_topology()
        self.draw()

    def draw_network_topology(self):
        """Draw lines between connected nodes"""
        # Clear existing connection lines
        for line in self.connection_lines:
            try:
                line.remove()
            except:
                pass
        self.connection_lines = []

        # Draw connections between all nodes within communication range
        comm_range = 30 if self.environment.lower() == "indoor" else 50
        for i, src in enumerate(self.nodes):
            for j, dst in enumerate(self.nodes):
                if i >= j:
                    continue  # Avoid duplicate connections

                distance = math.sqrt((self.x[i] - self.x[j]) ** 2 + (self.y[i] - self.y[j]) ** 2)
                if distance <= comm_range:
                    line = self.ax.plot(
                        [self.x[i], self.x[j]],
                        [self.y[i], self.y[j]],
                        color='#1f77b4', alpha=0.3, linewidth=1.0, zorder=1
                    )[0]
                    self.connection_lines.append(line)

    def animate_packet(self, src_node, dst_node, success):
        """Animate a packet transmission between nodes"""
        # Remove old packet lines
        for line in self.packet_lines:
            try:
                line.remove()
            except:
                pass
        self.packet_lines.clear()

        line_color = '#4CAF50' if success else '#F44336'
        line_style = '-' if success else '--'

        line, = self.ax.plot(
            [src_node.position[0], dst_node.position[0]],
            [src_node.position[1], dst_node.position[1]],
            color=line_color, linewidth=2.0, linestyle=line_style, alpha=0.9, zorder=3
        )
        self.packet_lines.append(line)
        self.draw()

        # Schedule removal after delay
        QTimer.singleShot(800, lambda: self.remove_packet_line(line))

    def remove_packet_line(self, line):
        """Remove a packet transmission line"""
        if line in self.packet_lines:
            try:
                line.remove()
                self.packet_lines.remove(line)
                self.draw()
            except:
                pass