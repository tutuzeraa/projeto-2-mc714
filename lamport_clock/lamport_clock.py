import zmq
import sys
import threading
import time
import logging

def main(my_id, peers):
    # Create id_names dictionary automatically based on peers
    id_names = {peer: f'Node {peer.split(":")[1].split(".")[-1]}' for peer in peers}
    id_names[my_id] = f'Node {my_id.split(":")[1].split(".")[-1]}'

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    logging.info(f"{id_names[my_id]} is starting up")

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
            try:
                message = receiver.recv_json()
                sender_id = message['id']
                received_clock = message['clock']
                logical_clock = max(logical_clock, received_clock) + 1
                logging.info(f"Process {id_names[my_id]} received message from {id_names[sender_id]} with clock {received_clock}. Updated clock to {logical_clock}")
                receiver.send_json({'ack': True})
            except Exception as e:
                logging.error(f"Error receiving messages: {e}")

    def send_messages():
        nonlocal logical_clock
        while True:
            time.sleep(5)  # Send a message every 5 seconds
            logical_clock += 1
            for peer in peers:
                try:
                    sender.connect(peer)
                    sender.send_json({'id': my_id, 'clock': logical_clock})
                    sender.recv_json()
                    logging.info(f"Process {id_names[my_id]} sent message to {id_names[peer]} with clock {logical_clock}")
                except Exception as e:
                    logging.error(f"Error sending message to {id_names[peer]}: {e}")
                finally:
                    sender.disconnect(peer)

    threading.Thread(target=receive_messages, daemon=True).start()
    send_messages()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python lamport_clock.py <my_id> <peer1> <peer2> ...")
        sys.exit(1)

    my_id = sys.argv[1]
    peers = sys.argv[2:]
    main(my_id, peers)
