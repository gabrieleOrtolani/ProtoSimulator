import zmq
from src.logger import logger

class RequestHandler:
    def __init__(self, sender, handler, zmq_port, periodic_sender=None):
        self.sender = sender
        self.handler = handler
        self.zmq_port = zmq_port
        self.periodic_sender = periodic_sender

    def start(self):
        ctx = zmq.Context()
        socket = ctx.socket(zmq.REP)
        socket.bind(f"tcp://*:{self.zmq_port}")
        logger.info(f"RequestHandler listening on ZMQ port {self.zmq_port}")
        while True:
            req = socket.recv_json()
            action = req.get("action")
            logger.info(f"Received ZMQ action: {action}")
            if action == "set":
                self.sender.set_message(req["type"], req["payload"])
                socket.send_json({"status": "ok"})
            elif action == "send":
                ok = self.sender.send_message(req["type"])
                socket.send_json({"status": "sent" if ok else "not_found"})
            elif action == "get":
                q = self.handler.queues.get(req["type"])
                if q and not q.empty():
                    msg = q.get()
                    socket.send_json({"msg": getattr(msg, "text", ""), "id": getattr(msg, "id", None)})
                else:
                    socket.send_json({"status": "empty"})
            elif action == "start_periodic_message":
                msg_type = req["message_type"]
                interval = req.get("interval")
                if self.periodic_sender:
                    self.periodic_sender.start_periodic_message(msg_type, interval)
                    socket.send_json({"status": "started"})
                else:
                    socket.send_json({"status": "periodic_sender_unavailable"})
            elif action == "stop_periodic_message":
                msg_type = req["message_type"]
                if self.periodic_sender:
                    self.periodic_sender.stop_periodic_message(msg_type)
                    socket.send_json({"status": "stopped"})
                else:
                    socket.send_json({"status": "periodic_sender_unavailable"})
            else:
                logger.warning(f"Unknown ZMQ action: {action}")
                socket.send_json({"status": "unknown_action"})