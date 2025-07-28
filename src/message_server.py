import yaml
import socketserver
import threading
from queue import Queue
from google.protobuf.json_format import ParseDict
from src.handlers import HANDLER_REGISTRY, default_handler
from src.logger import logger

class MessageServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, yaml_path, pb2_modules):
        super().__init__(server_address, self.TCPRequestHandler)
        with open(yaml_path) as f:
            self.messages_yaml = yaml.safe_load(f)
        self.pb2_modules = pb2_modules
        self.store = {}  # {msg_type: msg_pb_object}
        self.queues = {}  # {msg_type: Queue()}
        self.running = True

    def get_message_class(self, msg_type):
        for mod in self.pb2_modules.values():
            if hasattr(mod, msg_type):
                return getattr(mod, msg_type)
        raise Exception(f"Tipo messaggio '{msg_type}' non trovato nei proto caricati.")

    def set_message(self, msg_type, payload):
        msg_cls = self.get_message_class(msg_type)
        msg = msg_cls()
        ParseDict(payload, msg)
        self.store[msg_type] = msg
        logger.info(f"Set message for type {msg_type}: {payload}")

    def send_message(self, msg_type, conn):
        msg = self.store.get(msg_type)
        if not msg:
            logger.warning(f"Message type '{msg_type}' not set; send aborted.")
            return False
        conn.sendall(msg.SerializeToString())
        logger.info(f"Sent {msg_type} to {conn.getpeername()}")
        return True

    def start(self):
        thread = threading.Thread(target=self.serve_forever, daemon=True)
        thread.start()
        logger.info(f"MessageServer listening on {self.server_address}")

    class TCPRequestHandler(socketserver.BaseRequestHandler):
        def handle(self):
            data = self.request.recv(4096)
            handled = False
            # Try to decode as a message (receive mode)
            for msg_type in self.server.messages_yaml["messages"]:
                try:
                    msg_cls = self.server.get_message_class(msg_type)
                    msg = msg_cls()
                    msg.ParseFromString(data)
                    # Call handler
                    handler_fn = HANDLER_REGISTRY.get(msg_type, default_handler)
                    handler_fn(msg, msg_type)
                    q = self.server.queues.setdefault(msg_type, Queue())
                    q.put(msg)
                    logger.info(f"Received and handled {msg_type} from {self.client_address}")
                    handled = True
                    break
                except Exception:
                    continue
            if not handled:
                # Optionally: try to parse as a send command (if you really want to support text commands)
                try:
                    command = data.decode().strip().split()
                    if command and command[0] == "send" and len(command) > 1:
                        msg_type = command[1]
                        self.server.send_message(msg_type, self.request)
                        logger.info(f"Sent {msg_type} on request from {self.client_address}")
                        handled = True
                except Exception:
                    pass
            if not handled:
                logger.warning("Unrecognized or invalid message received.")
                self.request.sendall(b"Unknown or invalid message\n")