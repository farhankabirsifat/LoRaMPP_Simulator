class EnergyModel:
    def __init__(self, voltage=3.3):
        self.voltage = voltage
        self.states = {
            'TX': {'current': 120, 'startup': 0.002},  # 2ms startup
            'RX': {'current': 10, 'startup': 0.001},
            'IDLE': {'current': 1},
            'SLEEP': {'current': 0.01, 'wakeup': 0.005}
        }
        self.current_state = 'SLEEP'

    def calculate_energy(self, new_state, duration):
        energy = 0

        # Wakeup/sleep transition energy
        if self.current_state == 'SLEEP' and new_state != 'SLEEP':
            energy += self.states['SLEEP']['wakeup'] * self.voltage * 1000  # mJ

        # State-specific startup energy
        if 'startup' in self.states[new_state]:
            energy += self.states[new_state]['startup'] * self.voltage * 1000

        # Main operation energy
        energy += (self.states[new_state]['current'] * self.voltage * duration)

        self.current_state = new_state
        return energy / 1000  # Return in Joules