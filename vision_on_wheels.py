import os
import sys

from PyQt5.QtWidgets import QApplication

from visionapp.client import api, MainWindow

# Monkeypatch the api to be an instantiated object
api.__dict__['api'] = api.API("http://localhost:8000")

# Set all stream analysis as "active" here, since there's no way to in the UI
configs = api.api.get_stream_configurations()
for config in configs:
    success = api.api.start_analyzing(config.id)

    for zone in api.api.get_zones(config.id):
        if zone.name == "Screen": continue  # TODO: Delete the zone-deletion debugging code
        api.api.delete_zone(config.id, zone.id)

# Ensure that all relative paths are correct
# os.chdir(os.path.dirname(__file__))

app = QApplication(sys.argv)
window = MainWindow()

app.exec_()

api.api.close()
