import csv
import os
import random
import time

from PyQt5.QtCore import QObject, pyqtSignal

from core.channel import LoRaChannel
from core.energy_model import EnergyModel
from core.node import LoRaNode
from core.protocol import LoRaMPPProtocol

class SimulationSignals(QObject):
    packet_sent = pyqtSignal(object, object, bool)
    update_metrics = pyqtSignal(dict)
    log_message = pyqtSignal(str)
    simulation_finished = pyqtSignal(dict)
    visualization_update = pyqtSignal()

class LoRaMPPSimulation(QObject):
    def __init__(self, num_nodes=5, area_size=100, environment="urban", logger=None, visualizer=None, adaptive=True):
        super().__init__()
        self.nodes = []
        self.area_size = area_size
        self.environment = environment
        self.logger = logger
        self.visualizer = visualizer
        self.protocol = None
        self.running = False
        self.simulation_thread = None
        self.adaptive = adaptive
        self.signals = SimulationSignals()

        # Statistics
        self.total_packets_sent = 0
        self.total_packets_received = 0
        self.total_delay = 0.0
        self.total_energy_used = 0.0
        self.collisions = 0
        self.start_time = 0
        self.end_time = 0
        self.adaptation_count = 0

        # Initialize channel and energy model
        self.channel = LoRaChannel(environment=environment)
        self.energy_model = EnergyModel()

        # Adjust number of nodes for indoor environments
        if environment == "indoor" and num_nodes > 15:
            num_nodes = 15  # Limit nodes for indoor simulations
            if logger:
                self.signals.log_message.emit(f"Reduced nodes to {num_nodes} for indoor environment")

        # Create nodes
        for i in range(num_nodes):
            position = (
                random.randint(0, area_size),
                random.randint(0, area_size)
            )
            # Adjust energy for indoor nodes
            energy = random.uniform(80, 120)
            if environment == "indoor":
                energy *= 1.5  # Indoor devices often have better power supply

            node = LoRaNode(
                node_id=f"Node{i + 1}",
                position=position,
                energy=energy,
                environment=environment
            )
            self.nodes.append(node)

        # Initialize protocol
        self.protocol = LoRaMPPProtocol(self.nodes, self.channel, self.energy_model, adaptive)

    def run(self, num_messages=5):
        self.start_time = time.time()
        self.signals.log_message.emit(
            f"🚀 Simulation started with {len(self.nodes)} nodes in {self.environment} environment.")
        self.signals.log_message.emit(f"📡 Adaptive protocol: {'ENABLED' if self.adaptive else 'DISABLED'}")

        for _ in range(num_messages):
            src = random.choice(self.nodes)
            dst = random.choice([n for n in self.nodes if n.node_id != src.node_id])
            self.send_packet(src, dst)

        self.end_time = time.time()
        duration = self.end_time - self.start_time
        self.signals.log_message.emit(f"✅ Simulation completed in {duration:.2f} seconds.")
        metrics = self.get_metrics()
        self.signals.log_message.emit("📊 Simulation Results:")
        for k, v in metrics.items():
            self.signals.log_message.emit(f"   {k}: {v}")

        self.signals.simulation_finished.emit(metrics)
        return metrics

    def send_packet(self, src, dst):
        payload = f"Msg{self.total_packets_sent + 1} from {src.node_id}"
        success, delay = self.protocol.send_message(src.node_id, dst.node_id, payload)

        self.total_packets_sent += 1
        self.collisions = self.protocol.collisions
        self.adaptation_count = sum(node.adaptation_counter for node in self.nodes)

        if success:
            self.total_packets_received += 1
            self.total_delay += delay

        # Log transmission details
        distance = src.distance_to(dst)
        msg = (f"[{'✔' if success else '✘'}] {src.node_id} → {dst.node_id} | "
               f"Dist: {distance:.1f}m | SF: {src.spreading_factor} | BW: {src.bandwidth}kHz | "
               f"Delay: {delay * 1000:.1f}ms | "
               f"Energy: {src.energy:.1f}J | "
               f"Motion: {'Yes' if src.motion_detected else 'No'}")

        self.signals.log_message.emit(msg)
        self.signals.packet_sent.emit(src, dst, success)
        self.signals.visualization_update.emit()

    def run_with_mobility(self, duration=10, interval=1):
        self.running = True
        self.start_time = time.time()
        self.total_packets_sent = 0
        self.total_packets_received = 0
        self.total_delay = 0.0
        self.collisions = 0
        self.adaptation_count = 0

        self.signals.log_message.emit(f"🔄 Starting timed simulation for {duration} seconds...")
        self.signals.log_message.emit(f"📡 Adaptive protocol: {'ENABLED' if self.adaptive else 'DISABLED'}")

        while time.time() - self.start_time < duration and self.running:
            # Update node positions
            for node in self.nodes:
                if node.energy > 0:  # Only move if node has energy
                    node.move(self.area_size, self.environment)

            self.signals.visualization_update.emit()

            # Send packets from each node
            for src in self.nodes:
                if src.energy <= 0:  # Skip dead nodes
                    continue

                # Select a destination
                dst = random.choice([n for n in self.nodes if n.node_id != src.node_id and n.energy > 0])
                if dst:
                    self.send_packet(src, dst)

            # Sleep for the interval
            time.sleep(interval)

        self.end_time = time.time()
        sim_duration = self.end_time - self.start_time
        self.signals.log_message.emit(f"🛑 Simulation ended after {sim_duration:.1f} seconds.")
        metrics = self.get_metrics()
        for k, v in metrics.items():
            self.signals.log_message.emit(f"   {k}: {v}")

        self.signals.simulation_finished.emit(metrics)

    def stop(self):
        self.running = False
        self.signals.log_message.emit("⏹ Simulation stopped manually.")

    def get_metrics(self):
        pdr = (self.total_packets_received / self.total_packets_sent * 100) if self.total_packets_sent else 0
        avg_delay = (self.total_delay / self.total_packets_received * 1000) if self.total_packets_received else 0

        # FIX: Calculate actual energy used based on initial energy
        total_energy = 0.0
        for node in self.nodes:
            energy_used = node.initial_energy - node.energy
            if energy_used > 0:
                total_energy += energy_used

        # Calculate adaptive metrics
        avg_sf = sum(node.spreading_factor for node in self.nodes) / len(self.nodes) if self.nodes else 0
        avg_bw = sum(node.bandwidth for node in self.nodes) / len(self.nodes) if self.nodes else 0
        indoor_detections = sum(1 for node in self.nodes if node.motion_detected)

        return {
            'Packets Sent': self.total_packets_sent,
            'Packets Received': self.total_packets_received,
            'PDR (%)': round(pdr, 2),
            'Avg Delay (ms)': round(avg_delay, 1),
            'Total Energy Used (J)': round(total_energy, 2),
            'Collisions': self.collisions,
            'Active Nodes': sum(1 for node in self.nodes if node.energy > 0),
            'Total Nodes': len(self.nodes),  # Added for metrics panel
            'Avg SF': round(avg_sf, 2),
            'Avg BW (kHz)': round(avg_bw, 2),
            'Indoor Detections': indoor_detections,
            'Parameter Adaptations': self.adaptation_count
        }

    def export_results_to_csv(self, filename="simulation_results.csv"):
        data = self.get_metrics()
        headers = list(data.keys())
        values = list(data.values())

        os.makedirs("exports", exist_ok=True)
        path = os.path.join("exports", filename)

        with open(path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerow(values)

        return path