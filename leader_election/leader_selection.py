import zmq
import sys
import threading
import time
import logging
import random

def generate_id_names(peers, peer_ids):
    return {peer: f'Node {peer_ids}' for peer, peer_ids in zip(peers, peer_ids)}

def main(node_id, my_id, start_election, peers, peer_ids):
    id_names = generate_id_names(peers, peer_ids)
    id_names[my_id] = f'Node {node_id}'

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    logging.info(f"{id_names[my_id]} is starting up")

    context = zmq.Context()

    # Socket to receive messages on
    receiver = context.socket(zmq.REP)
    receiver.bind(my_id)

    current_leader = None
    received_ok = 0
    lock = threading.Lock()
    has_started_election = False
    #has_received_leader = False
    election_requested = threading.Event()

    higher_nodes = [peer for peer, peer_id in zip(peers, peer_ids) if int(peer_id) > int(node_id)]

    def receive_messages():
        nonlocal current_leader, received_ok, has_started_election#, has_received_leader

        while True:
            try:
                message = receiver.recv_json()
                sender_id = message['id']
                action = message['action']
                logging.info(f"{id_names[my_id]} received {action} from {id_names[sender_id]}")

                if action == "election":
                    logging.info(f"{id_names[my_id]} received election message and notifying main thread to start election")
                    election_requested.set()
                    receiver.send_json({'ack': True})
                    # Clear the event after notifying main thread
                    #election_requested.clear()
                    # send ok message to sender
                    sender = context.socket(zmq.REQ)
                    sender.connect(sender_id)
                    sender.send_json({'id': my_id, 'action': 'ok'})
                    sender.recv_json()
                    sender.disconnect(sender_id)
                elif action == "leader":
                    with lock:
                        current_leader = message['leader']
                    logging.info(f"{id_names[my_id]} acknowledges {id_names[current_leader]} as leader")
                    # with lock:
                    #     has_received_leader = True
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
        nonlocal current_leader, received_ok

        logging.info(f"{id_names[my_id]} is initiating an election")

        for peer in higher_nodes:
            try:
                logging.info(f"{id_names[my_id]} is sending election to {id_names[peer]}")
                sender = context.socket(zmq.REQ)
                sender.connect(peer)
                sender.send_json({'id': my_id, 'action': 'election'})
                sender.setsockopt(zmq.RCVTIMEO, 2000)  # 2 seconds timeout
                try:
                    sender.recv_json()  # Waiting for ack
                except zmq.error.Again:
                    logging.info(f"{id_names[peer]} did not respond in time, moving on")
                sender.disconnect(peer)
                sender.close()
            except Exception as e:
                logging.error(f"Error sending election to {id_names[peer]}: {e}")
                try:
                    sender.disconnect(peer)
                except Exception:
                    pass
                sender.close()

        # Wait for responses from all higher-numbered nodes
        time.sleep(5)  # Adjust as needed
        if received_ok == 0:
            with lock:
                current_leader = my_id
            send_leader()

    def send_leader():
        logging.info(f"{id_names[my_id]} is announcing itself as the leader")
        for peer in peers:
            try:
                sender = context.socket(zmq.REQ)
                sender.connect(peer)
                sender.send_json({'id': my_id, 'action': 'leader', 'leader': my_id})
                sender.setsockopt(zmq.RCVTIMEO, 500)  # 0.5 seconds timeout
                try:
                    sender.recv_json()  # Waiting for acknowledgment
                except zmq.error.Again:
                    logging.info(f"{id_names[peer]} did not respond in time, moving on")
                sender.disconnect(peer)
                sender.close()
            except Exception as e:
                logging.error(f"Error sending leader announcement to {id_names[peer]}: {e}")
                try:
                    sender.disconnect(peer)
                except Exception:
                    pass
                sender.close()
        return

    listen_thread = threading.Thread(target=receive_messages, daemon=True)
    listen_thread.start()

    time.sleep(10)  # Adjust as needed, wait for listener thread to start

    # Start election if specified or upon receiving an "election" message
    if start_election == '1':
        logging.info(f"{id_names[my_id]} is starting an election voluntarily")
        has_started_election = True
        send_election()
    else:
        while (current_leader == None) and not has_started_election:
            # Wait for election request from listener thread
            #election_requested.wait()

            if (current_leader == None) and not has_started_election and election_requested.is_set():
                has_started_election = True
                send_election()  # Start election upon receiving election request
                logging.info(f"Current leader is {current_leader}, has_started_election is {has_started_election}")

    while current_leader == None:
        pass
    

    time.sleep(15) 
    logging.info(f"The current leader is {id_names[current_leader]}")
if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python leader_selection.py <node_id> <my_id> <start_election> <peer1> <peer2> ...")
        sys.exit(1)

    node_id = sys.argv[1]
    my_id = sys.argv[2]
    start_election = sys.argv[3]
    peers = sys.argv[4::2]
    peer_ids = sys.argv[5::2]

    if random.random() < 0.5 and start_election == '0':
        sys.exit(1)

    main(node_id, my_id, start_election, peers, peer_ids)
