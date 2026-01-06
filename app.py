import os
import docker
from flask import Flask, render_template, jsonify, request

# Initialize Flask application
app = Flask(__name__)

# Initialize Docker client
# This looks for the Docker socket locally. On Linux, it's typically /var/run/docker.sock
# Ensure the user running this script has permissions (e.g., added to 'docker' group)
try:
    client = docker.from_env()
except Exception as e:
    print(f"Error connecting to Docker: {e}")
    print("Ensure Docker is running and you have permissions.")
    client = None

@app.route('/')
def index():
    """
    Serve the main web page.
    """
    return render_template('index.html')

@app.route('/api/containers', methods=['GET'])
def list_containers():
    """
    Get a list of all containers (running and stopped).
    Returns a JSON list of container details.
    """
    if not client:
        return jsonify({"error": "Docker not connected"}), 500

    try:
        # list all containers, including stopped ones (all=True)
        containers = client.containers.list(all=True)
        container_list = []
        
        for container in containers:
            # Get port mappings if any
            ports = container.attrs['NetworkSettings']['Ports']
            public_port = "N/A"
            # Look for port 80 mapping
            if ports and '80/tcp' in ports and ports['80/tcp']:
                public_port = ports['80/tcp'][0]['HostPort']

            container_list.append({
                "id": container.short_id,
                "name": container.name,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else "unknown",
                "port": public_port
            })
            
        return jsonify(container_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/containers', methods=['POST'])
def create_container():
    """
    Create and start a new Nginx container.
    Requirements:
    - Run nginx image
    - Mount custom index.html
    - Expose port 80 dynamically
    """
    if not client:
        return jsonify({"error": "Docker not connected"}), 500

    try:
        data = request.json
        container_name = data.get('name', 'my-nginx')

        # Absolute path to the custom nginx index.html on the HOST machine
        # We assume the 'nginx' folder is in the same directory as app.py
        base_dir = os.path.abspath(os.path.dirname(__file__))
        host_html_path = os.path.join(base_dir, 'nginx', 'index.html')

        # Verify file exists strictly to help the student debug
        if not os.path.exists(host_html_path):
            return jsonify({"error": f"Custom index.html not found at {host_html_path}"}), 400

        # Docker run configuration
        container = client.containers.run(
            "nginx:latest",
            name=container_name,
            detach=True, # Run in background
            ports={'80/tcp': None}, # Bind container port 80 to a random host port
            volumes={
                host_html_path: {
                    'bind': '/usr/share/nginx/html/index.html',
                    'mode': 'ro' # Read only
                }
            }
        )
        
        return jsonify({"message": "Container created", "id": container.short_id}), 201

    except docker.errors.ImageNotFound:
        # If nginx:latest isn't pulled yet
        return jsonify({"error": "Image 'nginx:latest' not found. Pulling it now... try again in a moment."}), 404
    except docker.errors.APIError as e:
        # Handle naming conflicts or other Docker API errors
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/containers/<container_id>/action', methods=['POST'])
def container_action(container_id):
    """
    Perform an action on a specific container.
    Actions: start, stop, delete
    """
    if not client:
        return jsonify({"error": "Docker not connected"}), 500

    data = request.json
    action = data.get('action')

    try:
        container = client.containers.get(container_id)

        if action == 'start':
            container.start()
            message = f"Container {container.name} started"
        elif action == 'stop':
            container.stop()
            message = f"Container {container.name} stopped"
        elif action == 'delete':
            # Force removal if running
            container.remove(force=True)
            message = f"Container {container.name} deleted"
        else:
            return jsonify({"error": "Invalid action"}), 400

        return jsonify({"message": message})

    except docker.errors.NotFound:
        return jsonify({"error": "Container not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Listen on all interfaces so it can be accessed from outside the VM if needed
    app.run(host='0.0.0.0', port=5000, debug=True)
