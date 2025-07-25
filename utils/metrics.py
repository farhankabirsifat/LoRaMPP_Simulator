from PyQt5.QtWidgets import QGridLayout, QWidget, QLabel


class MetricsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("""
                    QLabel {
                        font-weight: bold;
                        color: #333333;
                        font-size: 16px;
                    }
                    .metric-value {
                        font-size: 11px;
                        color: #1976d2;
                    }
                """)
        self.setMaximumHeight(150)

        # Create metric labels
        self.metric_labels = {}
        metrics = [
            ('PDR', 'Packet Delivery Ratio:'),
            ('Delay', 'Avg Delay:'),
            ('Energy', 'Energy Used:'),
            ('Packets', 'Packets Sent/Received:'),
            ('Collisions', 'Collisions:'),
            ('Nodes', 'Active Nodes:'),
            ('AvgSF', 'Avg Spreading Factor:'),
            ('AvgBW', 'Avg Bandwidth:'),
            ('IndoorDetect', 'Indoor Detections:'),
            ('Adaptations', 'Parameter Adaptations:')
        ]

        for i, (key, name) in enumerate(metrics):
            row = i // 2
            col = (i % 2) * 2
            label = QLabel(name)
            value = QLabel("N/A")
            value.setObjectName("metric-value")
            value.setStyleSheet("color: #1e88e5; font-weight: normal;")
            self.metric_labels[key] = value

            self.layout.addWidget(label, row, col)
            self.layout.addWidget(value, row, col + 1)

        # Add some spacing
        self.layout.setColumnStretch(4, 1)
        self.layout.setRowStretch(5, 1)

    def update_metrics(self, metrics):
        self.metric_labels['PDR'].setText(f"{metrics.get('PDR (%)', 0):.1f}%")
        self.metric_labels['Delay'].setText(f"{metrics.get('Avg Delay (ms)', 0):.1f} ms")
        self.metric_labels['Energy'].setText(f"{metrics.get('Total Energy Used (J)', 0):.1f} J")
        self.metric_labels['Packets'].setText(
            f"{metrics.get('Packets Sent', 0)}/{metrics.get('Packets Received', 0)}"
        )
        self.metric_labels['Collisions'].setText(f"{metrics.get('Collisions', 0)}")
        # FIX: Use 'Total Nodes' from metrics
        self.metric_labels['Nodes'].setText(
            f"{metrics.get('Active Nodes', 0)}/{metrics.get('Total Nodes', 0)}"
        )
        self.metric_labels['AvgSF'].setText(f"{metrics.get('Avg SF', 0):.1f}")
        self.metric_labels['AvgBW'].setText(f"{metrics.get('Avg BW (kHz)', 0):.1f} kHz")
        self.metric_labels['IndoorDetect'].setText(f"{metrics.get('Indoor Detections', 0)}")
        self.metric_labels['Adaptations'].setText(f"{metrics.get('Parameter Adaptations', 0)}")
