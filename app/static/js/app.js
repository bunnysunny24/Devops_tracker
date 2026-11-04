async function fetchStats() {
    try {
        const res = await fetch('/api/stats');
        if (res.ok) {
            const data = await res.json();
            document.getElementById('cpu-stat').innerText = `${data.cpu_percent}%`;
            document.getElementById('mem-stat').innerText = `${data.memory_used_mb} MB`;
            document.getElementById('mem-total').innerText = `of ${data.memory_total_mb} MB total`;
            document.getElementById('items-stat').innerText = data.total_items;
        }
    } catch (e) {
        console.error('Failed to update stats:', e);
    }
}

async function triggerRequest(endpoint) {
    const consoleBox = document.getElementById('test-output');
    consoleBox.innerHTML = `<code>Sending request to ${endpoint}...</code>`;
    const startTime = performance.now();
    
    try {
        const res = await fetch(endpoint);
        const duration = Math.round(performance.now() - startTime);
        const text = await res.text();
        
        let formattedData;
        try {
            formattedData = JSON.stringify(JSON.parse(text), null, 2);
        } catch {
            formattedData = text;
        }

        const statusColor = res.ok ? '#7ee787' : '#ff7b72';
        consoleBox.innerHTML = `
            <div style="color: ${statusColor}; margin-bottom: 4px;">
                HTTP ${res.status} ${res.statusText} (${duration}ms)
            </div>
            <pre style="color: #c9d1d9;">${formattedData}</pre>
        `;
    } catch (err) {
        consoleBox.innerHTML = `<span style="color: #ff7b72;">Fetch Error: ${err.message}</span>`;
    }
    
    fetchStats();
}

async function handleCreateItem(event) {
    event.preventDefault();
    const title = document.getElementById('itemTitle').value;
    const description = document.getElementById('itemDesc').value;
    const status = document.getElementById('itemStatus').value;

    try {
        const res = await fetch('/api/items', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, status }),
        });
        if (res.ok) {
            closeModal();
            window.location.reload();
        } else {
            alert('Failed to save entity');
        }
    } catch (e) {
        alert('Network error: ' + e.message);
    }
}

async function deleteItem(id) {
    if (!confirm(`Delete entity #${id}?`)) return;
    try {
        const res = await fetch(`/api/items/${id}`, { method: 'DELETE' });
        if (res.ok) {
            window.location.reload();
        }
    } catch (e) {
        alert('Delete failed: ' + e.message);
    }
}

function openModal() {
    document.getElementById('addModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('addModal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('addModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
};

// Initial update & 5s interval polling for stats
fetchStats();
setInterval(fetchStats, 5000);
