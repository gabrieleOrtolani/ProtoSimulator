import zmq
import time

def test_set_send_get():
    ctx = zmq.Context()
    s = ctx.socket(zmq.REQ)
    s.connect("tcp://127.0.0.1:6000")

    # SET
    s.send_json({
        "action": "set",
        "type": "ExampleMessage",
        "payload": {"text": "Test via ZMQ", "id": 123}
    })
    print("SET:", s.recv_json())

    # SEND
    s.send_json({
        "action": "send",
        "type": "ExampleMessage"
    })
    print("SEND:", s.recv_json())

    # GET (prova a leggere la queue del message handler)
    s.send_json({
        "action": "get",
        "type": "ExampleMessage"
    })
    print("GET:", s.recv_json())

def test_periodic():
    ctx = zmq.Context()
    s = ctx.socket(zmq.REQ)
    s.connect("tcp://127.0.0.1:6000")

    # Avvio periodic
    s.send_json({
        "action": "start_periodic_message",
        "message_type": "ExampleMessage",
        "interval": 2
    })
    print("START PERIODIC:", s.recv_json())

    time.sleep(5)

    # Stop periodic
    s.send_json({
        "action": "stop_periodic_message",
        "message_type": "ExampleMessage"
    })
    print("STOP PERIODIC:", s.recv_json())

if __name__ == "__main__":
    print("== Test ZMQ set/send/get ==")
    test_set_send_get()
    print("== Test ZMQ periodic ==")
    test_periodic()