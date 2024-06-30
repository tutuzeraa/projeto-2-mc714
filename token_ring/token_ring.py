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
    fail_probability = 1

    logging.info(f"Hello from node {node_id}")
    
    context = zmq.Context()
    
    receiver = context.socket(zmq.REP)
    receiver.bind(f"tcp://{node_ip}:5555")

    token_received_event = threading.Event()
    token_timeout = 30 # tempo de tolerância para receber o token


    def receive_token():
        while True:
            print(f"Node {node_id} waiting to receive token")
            try:
                receiver.setsockopt(zmq.RCVTIMEO, token_timeout * 1000)
                message = receiver.recv_json()
                if message.get("token") is True:
                    logging.info(f"Node {node_id} received the token")
                    token_received_event.set()
                    
                    # Simula uso por recursos
                    time.sleep(random.uniform(2, 5))
                    logging.info(f"Node {node_id} releasing the token")

                    # probabilidade do processo falhar e o token se perder
                    if random.uniform(0,10) < fail_probability:
                        logging.info(f"Oh no! Node {node_id} is failing")
                        receiver.send_json({"status": "failed to deliver token"})
                        continue
                    
                    # Envia token para o próximo nó
                    next_socket = context.socket(zmq.REQ)
                    next_socket.connect(f"tcp://{next_node_ip}:5555")
                    next_socket.send_json({"token": True})
                    next_socket.close()
                    
                    receiver.send_json({"status": "token passed"})
                    print(f"Node {node_id} passed the token to {next_node_ip}")

            except zmq.Again:
                logging.info(f"Node {node_id} did not receive the token within {token_timeout} seconds")

    # funcão para monitorar quanto tempo não recebe o token
    def token_monitor():
        while True:
            token_received_event.clear()
            if not token_received_event.wait(token_timeout):
                logging.info(f"Node {node_id} assuming token is lost and regenerating token")
                if node_id == 1:  # Nó 1 é o responsável por recriar o token
                    next_socket = context.socket(zmq.REQ)
                    next_socket.connect(f"tcp://{next_node_ip}:5555")
                    next_socket.send_json({"token": True})
                    next_socket.close()



    # Comeca a thread responsável por receber o token
    receiver_thread = threading.Thread(target=receive_token)
    receiver_thread.start()
    
    # Comeca a thread responsável por monitorar a quanto tempo não recebe o token
    monitor_thread = threading.Thread(target=token_monitor)
    monitor_thread.start()
    
    
    # Nó 1 é responsável por iniciar o token
    if node_id == 1:
        time.sleep(5)  # Espera os nós iniciarem 
        logging.info(f"Node {node_id} initializing the token")
        next_socket = context.socket(zmq.REQ)
        next_socket.connect(f"tcp://{next_node_ip}:5555")
        next_socket.send_json({"token": True})
        next_socket.close()
    
    receiver_thread.join()
    monitor_thread.join()

if __name__ == "__main__":
    node_ip = sys.argv[1] 
    main(node_ip)
