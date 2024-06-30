import os
import time
import zmq
import random
import threading

def receive_token(socket, node_id, next_node_ip):
    while True:
        message = socket.recv_json()
        if message.get("token") is not None:
            print(f"Node {node_id} received the token")
            
            # Simulate critical section usage
            time.sleep(random.uniform(1, 3))
            print(f"Node {node_id} releasing the token")
            
            # Send token to the next node
            context = zmq.Context()
            next_socket = context.socket(zmq.REQ)
            next_socket.connect(f"tcp://{next_node_ip}:5555")
            next_socket.send_json({"token": True})
            next_socket.close()

def main():
    node_id = int(os.environ['NODE_ID'])
    next_node_ip = os.environ['NEXT_NODE_IP']
    
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:5555")
    
    # Start the receiver thread
    receiver_thread = threading.Thread(target=receive_token, args=(socket, node_id, next_node_ip))
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
    main()