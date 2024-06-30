import yaml

def generate_docker_compose(num_nodes, election_nodes):
    compose = {
        'version': '3.8',
        'services': {},
        'networks': {
            'zeromq_net': {
                'driver': 'bridge',
                'ipam': {
                    'config': [
                        {'subnet': '172.28.0.0/16'}
                    ]
                }
            }
        }
    }

    peers = [f"tcp://172.28.1.{i+1}:5555" for i in range(num_nodes)]
    for i in range(num_nodes):
        node_id = i + 1
        my_id = f"tcp://172.28.1.{node_id}:5555"
        other_peers = peers[:i] + peers[i+1:]
        peer_ids = [str(j + 1) for j in range(num_nodes) if j != i]
        command = ["leader_selection.py", str(node_id), my_id]

        if node_id in election_nodes:
            command.append("1")
        else:
            command.append("0")

        command += sum([[peer, peer_id] for peer, peer_id in zip(other_peers, peer_ids)], [])
        
        service_name = f"node{node_id}"
        container_name = f"node{node_id}"
        ipv4_address = f"172.28.1.{node_id}"
        
        compose['services'][service_name] = {
            'build': '.',
            'container_name': container_name,
            'networks': {
                'zeromq_net': {
                    'ipv4_address': ipv4_address
                }
            },
            'command': command
        }

    return compose

num_nodes = 5 # Set the number of nodes you want to generate
election_nodes = [1, 9, 12, 50]  # Nodes 1, 3, and 4 will start elections

docker_compose_dict = generate_docker_compose(num_nodes, election_nodes)

# get current file path
import os
cwd = os.path.dirname(os.path.realpath(__file__))


# write docker-compose.yml file
with open(os.path.join(cwd, 'docker-compose.yml'), 'w') as f:
    yaml.dump(docker_compose_dict, f)

print("Docker Compose file generated for", num_nodes, "nodes.")
