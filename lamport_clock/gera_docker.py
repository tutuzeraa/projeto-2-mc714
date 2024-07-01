import yaml
import os

def generate_lamport_docker_compose(num_nodes):
    compose = {
        'version': '3.8',
        'services': {},
        'networks': {
            'lamport_net': {
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
        my_id = f"tcp://172.28.1.{i+1}:5555"
        other_peers = peers[:i] + peers[i+1:]
        
        command = ["lamport_clock.py", my_id] + other_peers
        
        service_name = f"node{i+1}"
        container_name = f"node{i+1}"
        ipv4_address = f"172.28.1.{i+1}"
        
        compose['services'][service_name] = {
            'build': '.',
            'container_name': container_name,
            'networks': {
                'lamport_net': {
                    'ipv4_address': ipv4_address
                }
            },
            'command': command,
            'restart': 'always'
        }

    return compose

num_nodes = 5  # Set the number of nodes you want to generate

docker_compose_dict = generate_lamport_docker_compose(num_nodes)

# Get current file path
cwd = os.path.dirname(os.path.realpath(__file__))

# Write docker-compose.yml file
with open(os.path.join(cwd, 'docker-compose.yml'), 'w') as f:
    yaml.dump(docker_compose_dict, f)

print("Docker Compose file generated for", num_nodes, "nodes.")
