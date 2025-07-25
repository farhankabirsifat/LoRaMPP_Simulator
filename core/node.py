import random
import math
import time
from collections import deque

from core.energy_model import EnergyModel


class LoRaNode:
    def __init__(self, node_id=None, position=(0, 0), tx_power=14, sf=7, cr=1, bw=125, energy=100.0,
                 environment="urban"):
        self.node_id = node_id or f"Node{random.randint(1000, 9999)}"
        self.position = position
        self.tx_power = tx_power
        self.spreading_factor = sf
        self.coding_rate = cr
        self.bandwidth = bw
        self.energy = energy
        self.initial_energy = energy  # Track initial energy for consumption calculation
        self.packet_queue = deque()
        self.received_packets = []
        self.transmitted_packets = 0
        self.received_packets_count = 0
        self.energy_model = EnergyModel()
        self.current_state = 'IDLE'
        self.environment = environment
        self.motion_detected = False
        self.adaptation_counter = 0  # Track how many times parameters have been adapted

    def transmit_packet(self, destination_id, payload):
        if self.energy <= 0:
            return None

        packet = {
            'src': self.node_id,
            'dst': destination_id,
            'payload': payload,
            'sf': self.spreading_factor,
            'bw': self.bandwidth,
            'cr': self.coding_rate,
            'timestamp': time.time()
        }

        # Consume energy for transmission
        energy_used = self.energy_model.calculate_energy('TX', 0.1)
        self.consume_energy(energy_used)

        self.packet_queue.append(packet)
        self.transmitted_packets += 1
        return packet

    def receive_packet(self, packet):
        if self.energy <= 0:
            return False

        # Consume energy for reception
        energy_used = self.energy_model.calculate_energy('RX', 0.05)
        self.consume_energy(energy_used)

        self.received_packets.append(packet)
        self.received_packets_count += 1
        return True

    def consume_energy(self, amount):
        self.energy = max(0, self.energy - amount)
        return self.energy

    def move(self, area_size=100, environment="urban"):
        """Move node with environment-specific behavior"""
        if self.energy <= 0:
            return  # Dead nodes don't move

        # Store previous position for motion detection
        prev_position = self.position

        # Environment-specific movement patterns
        if environment.lower() == "indoor":
            # Indoor nodes move in smaller steps
            step_max = 2
            # Indoor nodes don't consume movement energy
        else:
            step_max = min(5, int(self.energy / 20))

        if step_max < 1:
            return

        dx = random.randint(-step_max, step_max)
        dy = random.randint(-step_max, step_max)
        x, y = self.position
        new_x = max(0, min(area_size, x + dx))
        new_y = max(0, min(area_size, y + dy))
        self.position = (new_x, new_y)

        # Detect motion patterns
        distance_moved = math.sqrt((new_x - x) ** 2 + (new_y - y) ** 2)
        speed = distance_moved / 1.0  # Assuming 1s interval

        # Detect motion patterns: small, irregular movements = indoor
        self.motion_detected = (distance_moved > 0.2 and distance_moved < 3.0 and
                                random.random() > 0.7 and environment == "indoor")

        # Only consume energy for movement in outdoor environments
        if environment.lower() != "indoor":
            self.consume_energy(0.005)

    def update_parameters(self, rssi, snr, motion_detected):
        """Dynamically adjust parameters based on environment and signal quality"""
        self.adaptation_counter += 1

        # Environment detection
        is_indoor = motion_detected or self.environment == "indoor"

        if is_indoor:
            # Indoor optimization: higher data rate, lower power
            self.spreading_factor = max(7, min(9, self.spreading_factor))
            self.bandwidth = 500 if snr > -5 else 250
            self.tx_power = max(2, min(14, self.tx_power))
            self.coding_rate = 1  # 4/5
        else:
            # Outdoor optimization: longer range
            if rssi < -110 or snr < 0:
                # Weak signal conditions
                self.spreading_factor = min(12, self.spreading_factor + 1)
                self.tx_power = min(20, self.tx_power + 3)
                self.bandwidth = 125
                self.coding_rate = 4  # 4/8
            elif rssi > -80 and snr > 10:
                # Strong signal conditions
                self.spreading_factor = max(7, self.spreading_factor - 1)
                self.bandwidth = 250
                self.tx_power = max(10, self.tx_power - 2)
                self.coding_rate = 1  # 4/5

        # Ensure values stay within valid ranges
        self.spreading_factor = max(7, min(12, self.spreading_factor))
        self.bandwidth = 125 if self.bandwidth < 125 else self.bandwidth
        self.tx_power = max(2, min(20, self.tx_power))

    def distance_to(self, other_node):
        x1, y1 = self.position
        x2, y2 = other_node.position
        return math.hypot(x2 - x1, y2 - y1)

    def get_energy_color(self):
        if self.energy > 50:
            return 'green'
        elif self.energy > 20:
            return 'orange'
        else:
            return 'red'