import os
import sys
import time
import zmq
import random
import threading

def main(node_ip):
    print("Hi!")
    node_id = int(os.environ['NODE_ID'])
    next_node_ip = os.environ['NEXT_NODE_IP']
    
    context = zmq.Context()
    
    print("Here 1")
    receiver = context.socket(zmq.REP)
    receiver.bind(f"tcp://{node_ip}:5555")

    print("Here 2")
    def receive_token():
        while True:
            message = receiver.recv_json()
            if message.get("token") is True:
                print(f"Node {node_id} received the token")
                
                # Simulate critical section usage
                time.sleep(random.uniform(3, 10))
                print(f"Node {node_id} releasing the token")
                
                # Send token to the next node
                next_socket = context.socket(zmq.REQ)
                next_socket.connect(f"tcp://{next_node_ip}:5555")
                next_socket.send_json({"token": True})
                next_socket.close()
                
                # Send a dummy reply to complete the REP socket cycle
                receiver.send_json({"status": "token passed"})

    print("Here 3")
    # Start the receiver thread
    receiver_thread = threading.Thread(target=receive_token)
    receiver_thread.start()
    
    print("Here 4")
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
