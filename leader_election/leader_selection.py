import zmq
import sys
import threading
import time
import logging

# Node IDs to Names mapping for logging purposes
id_names = {
    'tcp://172.28.1.1:5555': 'Node 1',
    'tcp://172.28.1.2:5555': 'Node 2',
    'tcp://172.28.1.3:5555': 'Node 3'
}

def main(node_id, my_id, peers, peer_ids):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    context = zmq.Context()

    # Socket to receive messages on
    receiver = context.socket(zmq.REP)
    receiver.bind(my_id)

    # Socket to send messages to peers
    sender = context.socket(zmq.REQ)

    current_leader = None
    received_ok = 0
    lock = threading.Lock()

    logging.info(f"Node {node_id}, My ID: {my_id} has peers: {peers}")
    higher_nodes = [peer for peer, peer_id in zip(peers, peer_ids) if int(peer_id) > int(node_id)]
    logging.info(f"Node {node_id}, My ID: {my_id} has higher peers: {higher_nodes}")

    def receive_messages():
        nonlocal current_leader
        nonlocal received_ok
        while current_leader is None:
            try:
                message = receiver.recv_json()
                sender_id = message['id']
                action = message['action']
                logging.info(f"{id_names[my_id]} received {action} from {id_names[sender_id]}")
                if action == "election":
                    receiver.send_json({'ack': True})
                    sender.connect(sender_id)
                    sender.send_json({'id': my_id, 'action': 'ok'})
                    sender.recv_json()
                    sender.disconnect(sender_id)
                elif action == "leader":
                    current_leader = message['leader']
                    logging.info(f"{id_names[my_id]} acknowledges {id_names[current_leader]} as leader")
                    receiver.send_json({'ack': True})
                    return
                elif action == "ok":
                    with lock:
                        received_ok += 1
                    receiver.send_json({'ack': True})
                else:
                    logging.error(f"Unknown action {action}")
            except Exception as e:
                logging.error(f"Error in receive_message: {e}")

    def send_election():
        nonlocal current_leader
        logging.info(f"{id_names[my_id]} is initiating an election")

        for peer in higher_nodes:
            try:
                sender.connect(peer)
                sender.send_json({'id': my_id, 'action': 'election'})
                sender.recv_json()  # Waiting for 'ok' response
                sender.disconnect(peer)
            except Exception as e:
                logging.error(f"Error sending election to {id_names[peer]}: {e}")

        # Wait for responses from all higher-numbered nodes
        time.sleep(5)  # Wait a bit before declaring yourself the leader
        with lock:
            if received_ok == 0:
                current_leader = my_id
                send_leader()

    def send_leader():
        logging.info(f"{id_names[my_id]} is announcing itself as the leader")
        for peer in peers:
            try:
                sender.connect(peer)
                sender.send_json({'id': my_id, 'action': 'leader', 'leader': my_id})
                sender.recv_json()  # Waiting for acknowledgment
                sender.disconnect(peer)
            except Exception as e:
                logging.error(f"Error sending leader announcement to {id_names[peer]}: {e}")

    threading.Thread(target=receive_messages, daemon=False).start()
    time.sleep(5)  # Allow time for all nodes to start
    send_election()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python bully_algorithm.py <node_id> <my_id> <peer1> <peer2> ...")
        sys.exit(1)

    node_id = sys.argv[1]
    my_id = sys.argv[2]
    peers = sys.argv[3::2]
    peer_ids = sys.argv[4::2]
    main(node_id, my_id, peers, peer_ids)
