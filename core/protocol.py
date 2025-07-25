import math
import random

class LoRaMPPProtocol:
    def __init__(self, nodes, channel, energy_model, adaptive=True):
        self.nodes = {node.node_id: node for node in nodes}
        self.channel = channel
        self.energy_model = energy_model
        self.collisions = 0
        self.adaptive = adaptive
        self.active_transmissions = set()

    def send_message(self, src_id, dst_id, payload):
        try:
            src = self.nodes.get(src_id)
            dst = self.nodes.get(dst_id)

            if not src or not dst or src.energy <= 0 or dst.energy <= 0:
                return False, 0

            # Check for collision
            if self._check_collision(src_id):
                self.collisions += 1
                tx_energy = self.energy_model.calculate_energy("TX", 0.05)
                src.consume_energy(tx_energy)
                return False, 0.05

            distance = self._calculate_distance(src.position, dst.position)

            # Get signal quality for adaptation
            signal_quality = self.channel.simulate_link(src.tx_power, distance)

            # Apply adaptive parameter tuning if enabled
            if self.adaptive:
                src.update_parameters(
                    signal_quality['rssi'],
                    signal_quality['snr'],
                    src.motion_detected
                )

            # Transmission time based on LoRa parameters
            symbol_time = (2 ** src.spreading_factor) / (src.bandwidth / 1000)  # ms
            payload_symbols = max(8, math.ceil((len(payload) * 8) / (4 * src.spreading_factor)))
            transmission_time = (payload_symbols + 8.25) * symbol_time / 1000  # seconds

            # Add to active transmissions
            self.active_transmissions.add(src_id)

            # Simulate propagation delay
            propagation_delay = distance / (3e8 * 0.7)  # 70% of light speed
            total_delay = transmission_time + propagation_delay

            # Check if packet is delivered
            delivery_success = self._packet_delivered(signal_quality, distance)

            # Remove from active transmissions
            self.active_transmissions.remove(src_id)

            if delivery_success:
                dst.receive_packet({
                    'src': src_id,
                    'dst': dst_id,
                    'payload': payload,
                    'rssi': signal_quality['rssi'],
                    'snr': signal_quality['snr'],
                    'distance': distance,
                    'delay': total_delay
                })
                return True, total_delay
            else:
                return False, total_delay

        except Exception as e:
            print("Protocol Error:", str(e))
            return False, 0

    def _calculate_distance(self, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def _packet_delivered(self, signal_quality, distance):
        # Delivery probability based on SNR and distance
        snr = signal_quality.get("snr", 0)
        base_prob = 0.9 if snr > 6 else 0.3

        # Distance penalty
        distance_penalty = min(1, max(0, 1 - (distance / 1000)))
        return random.random() < base_prob * distance_penalty

    def _check_collision(self, node_id):
        # Simple collision model - 10% chance per concurrent transmission
        collision_prob = 0.1 * len(self.active_transmissions)
        return random.random() < collision_prob