import os
import sys
import time
import zmq
import random
import threading
import logging

def main(node_ip):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    node_id = int(os.environ['NODE_ID'])
    next_node_ip = os.environ['NEXT_NODE_IP']

    logging.info(f"Hello from node {node_id}")
    
    context = zmq.Context()
    
    logging.info("Here 1")
    receiver = context.socket(zmq.REP)
    receiver.bind(f"tcp://{node_ip}:5555")

    def receive_token():
        logging.info("Here 3")
        while True:
            message = receiver.recv_json()
            if message.get("token") is True:
                logging.info(f"Node {node_id} received the token")
                
                # Simulate critical section usage
                time.sleep(random.uniform(3, 10))
                logging.info(f"Node {node_id} releasing the token")

                receiver.send_json({"status": "token passed"})
                
                # Send token to the next node
                next_socket = context.socket(zmq.REQ)
                next_socket.connect(f"tcp://{next_node_ip}:5555")
                next_socket.send_json({"token": True})
                next_socket.close()
                
                # Send a dummy reply to complete the REP socket cycle

    logging.info("Here 2")
    # Start the receiver thread
    receiver_thread = threading.Thread(target=receive_token)
    receiver_thread.start()
    
    # Node 1 initializes the token
    if node_id == 1:
        time.sleep(5)  # Wait for all nodes to be up
        logging.info(f"Node {node_id} initializing the token")
        next_socket = context.socket(zmq.REQ)
        next_socket.connect(f"tcp://{next_node_ip}:5555")
        next_socket.send_json({"token": True})
        next_socket.close()
    
    receiver_thread.join()

if __name__ == "__main__":
    node_ip = sys.argv[1]
    main(node_ip)
