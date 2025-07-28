import yaml
import socketserver
from google.protobuf.json_format import ParseDict
from src.logger import logger

class MessageSender(socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass, yaml_path, pb2_modules):
        """
        pb2_modules: dict {modulename (str): python module}, es: {"message_pb2": <module>, ...}
        """
        super().__init__(server_address, RequestHandlerClass)
        with open(yaml_path) as f:
            self.messages_yaml = yaml.safe_load(f)
        self.pb2_modules = pb2_modules
        self.store = {}  # {msg_type: msg_pb_object}

    def get_message_class(self, msg_type):
        """
        Cerca la classe msg_type in tutti i moduli caricati.
        """
        for mod in self.pb2_modules.values():
            if hasattr(mod, msg_type):
                return getattr(mod, msg_type)
        raise Exception(f"Tipo messaggio '{msg_type}' non trovato in nessun modulo dei proto caricati.")

    def set_message(self, msg_type, payload):
        msg_cls = self.get_message_class(msg_type)
        msg = msg_cls()
        ParseDict(payload, msg)
        self.store[msg_type] = msg
        logger.info(f"Set message for type {msg_type}: {payload}")

    def send_message(self, msg_type, conn=None):
        msg = self.store.get(msg_type)
        if not msg:
            logger.warning(f"Message type '{msg_type}' not set; send aborted.")
            return False
        if conn:
            conn.sendall(msg.SerializeToString())
            logger.info(f"Sent {msg_type} via existing connection.")
        else:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(self.server_address)
                s.sendall(msg.SerializeToString())
                logger.info(f"Sent {msg_type} as TCP client.")
        return True