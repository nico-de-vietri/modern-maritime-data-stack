import sys
import os

current_dir = os.path.dirname(__file__)
# Ajustá la ruta relativa según dónde esté el include y data_collector
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", "data_collector"))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Ahora importá lo que necesites de data_collector
from main_api_to_minio import process_and_upload
from ais_websocket import listen_and_process

# Podés agregar aquí funciones wrapper o cualquier cosa que el DAG necesite
