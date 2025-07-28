import os
import sys
import threading
from src.message_server import MessageServer
from src.periodic_sender import PeriodicSender
from src.logger import logger

# Import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'config')))
import config

def load_pb2_modules(interface_dir="interface"):
    """
    Carica dinamicamente tutti i moduli *_pb2.py dalla cartella interface/
    Restituisce un dict: { "messages_pb2": modulo, ... }
    """
    import importlib
    modules = {}
    abs_interface = os.path.abspath(interface_dir)
    for fname in os.listdir(abs_interface):
        if fname.endswith("_pb2.py") and not fname.startswith("__"):
            mod_name = fname[:-3]  # rimuove .py
            full_mod = f"interface.{mod_name}"
            modules[mod_name] = importlib.import_module(full_mod)
    return modules

def main():
    # Percorsi
    base_dir = os.path.dirname(__file__)
    yaml_path = os.path.abspath(os.path.join(base_dir, 'config', 'messages.yaml'))
    interface_dir = os.path.abspath(os.path.join(base_dir, 'interface'))

    # Carica proto modules
    pb2_modules = load_pb2_modules(interface_dir)

    # Configurazione porte
    HOST, PORT = config.TCP_HOST, config.TCP_PORT

    # Importa la classe unica server
    from src.message_server import MessageServer

    # Crea il server (sender + handler)
    server = MessageServer((HOST, PORT), yaml_path, pb2_modules)
    server.start()
    logger.info(f"MessageServer listening on {HOST}:{PORT}")

    # Periodic Sender (configura secondo le tue esigenze)
    # Esempio: {"ExampleMessage": 2} invia ExampleMessage ogni 2 secondi
    periodic = PeriodicSender(server, interval_map={})
    periodic.start()
    logger.info("Started PeriodicSender.")

    # Rimani attivo
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.shutdown()
        periodic.stop()

if __name__ == "__main__":
    main()