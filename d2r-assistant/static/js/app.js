/**
 * D2R Inventory Assistant - Global JavaScript
 */

// ── Toast Notifications ──────────────────────────────────────────────

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const bgClass = {
        success: 'bg-success',
        danger: 'bg-danger',
        warning: 'bg-warning text-dark',
        info: 'bg-info text-dark',
    }[type] || 'bg-secondary';

    const toast = document.createElement('div');
    toast.className = `toast show ${bgClass}`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    container.appendChild(toast);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}


// ── Global Search ────────────────────────────────────────────────────

async function globalSearch(event) {
    event.preventDefault();
    const query = document.getElementById('globalSearchInput').value;
    if (!query) return;

    const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const data = await res.json();

    const container = document.getElementById('searchResults');
    let html = '';

    // Inventory matches
    if (data.inventory_matches && data.inventory_matches.length > 0) {
        html += '<h6 class="text-muted">In Your Inventory</h6>';
        for (const match of data.inventory_matches) {
            html += `
                <div class="inventory-item mb-2">
                    <div class="d-flex justify-content-between">
                        <strong class="quality-unique">${match.item.name}</strong>
                        <span class="text-muted small">${match.location}</span>
                    </div>
                </div>
            `;
        }
    }

    // Database matches
    if (data.database_matches && data.database_matches.length > 0) {
        html += '<h6 class="text-muted mt-3">Database Results</h6>';
        for (const match of data.database_matches) {
            html += `
                <div class="inventory-item mb-2">
                    <div class="d-flex justify-content-between">
                        <strong class="quality-unique">${match.name}</strong>
                        <span class="badge bg-secondary">${match.category}</span>
                    </div>
                    ${match.data.tier ? `<span class="tier-badge tier-${match.data.tier.toLowerCase()}">${match.data.tier}</span>` : ''}
                    ${match.data.est_fg ? `<span class="price-range ms-2">${match.data.est_fg} FG</span>` : ''}
                </div>
            `;
        }
    }

    if (!html) {
        html = '<div class="text-muted text-center py-3">No results found.</div>';
    }

    container.innerHTML = html;
    new bootstrap.Modal(document.getElementById('searchModal')).show();
}


// ── Utility Functions ────────────────────────────────────────────────

function formatDate(isoString) {
    if (!isoString) return '-';
    const d = new Date(isoString);
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function truncate(str, len) {
    if (!str) return '';
    return str.length > len ? str.substring(0, len) + '...' : str;
}


// ── API Helper ───────────────────────────────────────────────────────

async function apiCall(url, method = 'GET', body = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' },
    };
    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const res = await fetch(url, options);
        return await res.json();
    } catch (err) {
        showToast(`API Error: ${err.message}`, 'danger');
        return { error: err.message };
    }
}


// ── Keyboard Shortcuts ───────────────────────────────────────────────

document.addEventListener('keydown', (e) => {
    // Ctrl+K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('globalSearchInput').focus();
    }
});
