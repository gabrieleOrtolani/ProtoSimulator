from src.logger import logger

HANDLER_REGISTRY = {}

def handler(msg_type):
    def decorator(func):
        HANDLER_REGISTRY[msg_type] = func
        return func
    return decorator

def default_handler(msg, msg_type):
    logger.info(f"[DEFAULT HANDLER] Ricevuto {msg_type}: {msg}")

@handler("ExampleMessage")
def handle_example(msg, msg_type):
    logger.info(f"[SPECIFIC HANDLER] ExampleMessage! Testo: {msg.text}, ID: {msg.id}")