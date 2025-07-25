import random
import math

class LoRaChannel:
    def __init__(self, frequency=868e6, bandwidth=125e3, environment="urban"):
        self.frequency = frequency
        self.bandwidth = bandwidth
        self.environment = environment
        self.c = 3e8  # Speed of light

    def calculate_path_loss(self, distance):
        """Calculate path loss using log-distance model"""
        if distance == 0:
            return 0

        # Environment-specific parameters
        if self.environment == "urban":
            exponent = 3.0
            shadowing_std = 10.0
        elif self.environment == "suburban":
            exponent = 2.75
            shadowing_std = 8.0
        elif self.environment == "rural":
            exponent = 2.5
            shadowing_std = 6.0
        elif self.environment == "free_space":
            exponent = 2.0
            shadowing_std = 4.0
        elif self.environment == "indoor":
            # Multi-wall model for indoor environments
            exponent = 3.5
            shadowing_std = 12.0
            num_walls = max(1, int(distance / 5))  # 1 wall per 5m
            wall_loss = 8 * num_walls  # 8dB loss per wall
        else:  # Default to urban
            exponent = 3.0
            shadowing_std = 10.0
            wall_loss = 0

        # Free space path loss
        lambda_ = self.c / self.frequency
        fspl = 20 * math.log10(4 * math.pi * distance / lambda_)

        # Log-distance path loss
        path_loss_db = fspl + 10 * exponent * math.log10(distance)

        # Add wall loss for indoor environments
        if self.environment == "indoor":
            path_loss_db += wall_loss

        # Shadowing effect
        shadowing = random.gauss(0, shadowing_std)

        return path_loss_db + shadowing

    def calculate_rssi(self, tx_power, path_loss):
        """Calculate Received Signal Strength Indicator"""
        return tx_power - path_loss

    def calculate_snr(self, rssi):
        """Calculate Signal-to-Noise Ratio"""
        # Thermal noise calculation
        noise_floor = -174 + 10 * math.log10(self.bandwidth)
        return rssi - noise_floor

    def simulate_link(self, tx_power, distance):
        """Simulate wireless link with realistic parameters"""
        path_loss = self.calculate_path_loss(distance)
        rssi = self.calculate_rssi(tx_power, path_loss)
        snr = self.calculate_snr(rssi)

        # Add multipath fading effect
        fading = random.uniform(-3, 3)
        rssi += fading
        snr += fading

        return {
            'rssi': rssi,
            'snr': snr,
            'path_loss': path_loss
        }

