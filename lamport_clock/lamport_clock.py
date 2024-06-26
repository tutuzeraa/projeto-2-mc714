import zmq
import sys
import threading
import time
import logging


id_names = {
    'tcp://172.28.1.1:5555' : 'Node 1',
    'tcp://172.28.1.2:5555' : 'Node 2',
    'tcp://172.28.1.3:5555' : 'Node 3'
}


def main(my_id, peers):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    context = zmq.Context()

    # Socket to receive messages on
    receiver = context.socket(zmq.REP)
    receiver.bind(my_id)

    # Socket to send messages to peers
    sender = context.socket(zmq.REQ)

    logical_clock = 0

    def receive_messages():
        nonlocal logical_clock
        while True:
            message = receiver.recv_json()
            sender_id = message['id']
            received_clock = message['clock']
            logical_clock = max(logical_clock, received_clock) + 1
            logging.info(f"Process {id_names[my_id]} received message from {id_names[sender_id]} with clock {received_clock}. Updated clock to {logical_clock}")
            receiver.send_json({'ack': True})

    def send_messages():
        nonlocal logical_clock
        while True:
            time.sleep(5)  # send a message every 5 seconds
            logical_clock += 1
            for peer in peers:
                sender.connect(peer)
                sender.send_json({'id': my_id, 'clock': logical_clock})
                sender.recv_json()
                sender.disconnect(peer)
                logging.info(f"Process {id_names[my_id]} sent message to {id_names[peer]} with clock {logical_clock}")

    threading.Thread(target=receive_messages, daemon=False).start()
    send_messages()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python lamport_clock.py <my_id> <peer1> <peer2> ...")
        sys.exit(1)

    my_id = sys.argv[1]
    peers = sys.argv[2:]
    main(my_id, peers)
