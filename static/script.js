document.addEventListener('DOMContentLoaded', () => {
    fetchContainers();
});

// Fetch and display containers
async function fetchContainers() {
    try {
        const response = await fetch('/api/containers');
        const data = await response.json();

        if (data.error) {
            showMessage(data.error, 'error');
            return;
        }

        const tbody = document.querySelector('#containersTable tbody');
        tbody.innerHTML = ''; // Clear table

        data.forEach(container => {
            const tr = document.createElement('tr');

            // Format status badge
            const statusClass = container.status === 'running' ? 'status-running' : 'status-exited';

            // Prepare actions
            let actionButtons = '';
            if (container.status === 'running') {
                actionButtons += `<button class="btn-danger" style="margin-right: 5px;" onclick="performAction('${container.id}', 'stop')">Stop</button>`;
            } else {
                actionButtons += `<button class="btn-success" style="margin-right: 5px;" onclick="performAction('${container.id}', 'start')">Start</button>`;
            }
            actionButtons += `<button class="btn-danger" onclick="performAction('${container.id}', 'delete')">Delete</button>`;

            // Display Port link if running
            let portDisplay = 'None';
            if (container.port && container.port !== 'N/A') {
                portDisplay = `<a href="http://${window.location.hostname}:${container.port}" target="_blank">${container.port} (Open)</a>`;
            }

            tr.innerHTML = `
                <td><strong>${container.name}</strong><br><small style="color:#888">${container.id.substring(0, 12)}</small></td>
                <td><span class="status-badge ${statusClass}">${container.status}</span></td>
                <td>${container.image}</td>
                <td>${portDisplay}</td>
                <td>${actionButtons}</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (error) {
        console.error('Error fetching containers:', error);
        showMessage('Failed to load container list.', 'error');
    }
}

// Create a new container
async function createContainer() {
    const nameInput = document.getElementById('containerName');
    const name = nameInput.value.trim();

    if (!name) {
        showMessage('Please enter a container name.', 'error');
        return;
    }

    showMessage('Creating container...', 'loading');

    try {
        const response = await fetch('/api/containers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(`Container '${name}' created successfully!`, 'success');
            nameInput.value = ''; // Reset input
            fetchContainers(); // Refresh list
        } else {
            showMessage(`Error: ${data.error}`, 'error');
        }

    } catch (error) {
        console.error('Error creating container:', error);
        showMessage('Network error while creating container.', 'error');
    }
}

// Perform Start/Stop/Delete actions
async function performAction(containerId, action) {
    showMessage(`${action.charAt(0).toUpperCase() + action.slice(1)}ing container...`, 'loading');

    try {
        const response = await fetch(`/api/containers/${containerId}/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: action })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(data.message, 'success');
            fetchContainers(); // Refresh list
        } else {
            showMessage(`Error: ${data.error}`, 'error');
        }

    } catch (error) {
        console.error(`Error performing ${action}:`, error);
        showMessage('Network error.', 'error');
    }
}

// Helper to show status messages
function showMessage(msg, type) {
    const el = document.getElementById('statusMessage');
    el.textContent = msg;
    el.className = ''; // reset classes
    el.classList.add(`msg-${type}`);

    // Auto clear after 3 seconds for success
    if (type === 'success') {
        setTimeout(() => {
            el.className = 'hidden';
        }, 3000);
    }
}
