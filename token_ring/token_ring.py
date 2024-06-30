import os
import sys
import time
import zmq
import random
import threading


def main(node_ip):
    node_id = int(os.environ['NODE_ID'])
    next_node_ip = os.environ['NEXT_NODE_IP']
    
    context = zmq.Context()
    # socket = context.socket(zmq.REP)
    # socket.bind(f"tcp://*:5555")
    
    receiver = context.socket(zmq.REP)
    receiver.bind(f"tcp://{node_ip}:5555")

    def receive_token(node_id, next_node_ip):
        while True:
            message = receiver.recv_json()
            if message.get("token") is not None:
                print(f"Node {node_id} received the token")
                
                # Simulate critical section usage
                time.sleep(random.uniform(3, 10))
                print(f"Node {node_id} releasing the token")
                
                # Send token to the next node
                context = zmq.Context()
                next_socket = context.socket(zmq.REQ)
                next_socket.connect(f"tcp://{next_node_ip}:5555")
                next_socket.send_json({"token": True})
                next_socket.close()
    

    # Start the receiver thread
    receiver_thread = threading.Thread(target=receive_token, args=(node_id, next_node_ip))
    receiver_thread.start()
   

    # Node 1 initializes the token
    if node_id == 1:
        time.sleep(5)  # Wait for all nodes to be up
        print(f"Node {node_id} initializing the token")
        next_socket = context.socket(zmq.REQ)
        next_socket.connect(f"tcp://{next_node_ip}:5555")
        next_socket.send_json({"token": True})
        next_socket.close()
    
    receiver_thread.join()

if __name__ == "__main__":
    node_ip = sys.argv[1]
    main(node_ip)
