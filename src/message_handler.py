import threading
import socket
from queue import Queue
import yaml
from src.handlers import HANDLER_REGISTRY, default_handler
from src.logger import logger

class MessageHandler:
    def __init__(self, tcp_host, tcp_port, pb2_modules, yaml_path):
        """
        pb2_modules: dict {modulename (str): python module}, es: {"message_pb2": <module>, ...}
        """
        self.queues = {}  # {msg_type: Queue()}
        self.running = True
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.pb2_modules = pb2_modules
        with open(yaml_path) as f:
            self.messages_yaml = yaml.safe_load(f)

    def get_message_class(self, msg_type):
        """
        Cerca la classe msg_type in tutti i moduli caricati.
        """
        for mod in self.pb2_modules.values():
            if hasattr(mod, msg_type):
                return getattr(mod, msg_type)
        raise Exception(f"Tipo messaggio '{msg_type}' non trovato in nessun modulo dei proto caricati.")

    def start(self):
        thread = threading.Thread(target=self.listen)
        thread.daemon = True
        thread.start()
        logger.info(f"MessageHandler listening on {self.tcp_host}:{self.tcp_port}")

    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.tcp_host, self.tcp_port))
            s.listen()
            while self.running:
                conn, addr = s.accept()
                data = conn.recv(4096)
                handled = False
                for msg_type in self.messages_yaml["messages"]:
                    try:
                        msg_cls = self.get_message_class(msg_type)
                        msg = msg_cls()
                        msg.ParseFromString(data)
                        handler_fn = HANDLER_REGISTRY.get(msg_type, default_handler)
                        handler_fn(msg, msg_type)
                        q = self.queues.setdefault(msg_type, Queue())
                        q.put(msg)
                        logger.info(f"Received and handled {msg_type} from {addr}")
                        handled = True
                        break
                    except Exception:
                        continue
                if not handled:
                    logger.warning("Unrecognized or invalid message received.")