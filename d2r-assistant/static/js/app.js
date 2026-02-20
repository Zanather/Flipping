/**
 * D2R Inventory Assistant - Global JavaScript
 */

// ── Sidebar Toggle (mobile) ─────────────────────────────────────────

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    sidebar.classList.toggle('open');
    overlay.classList.toggle('show');
}

// Close sidebar on link click (mobile)
document.addEventListener('DOMContentLoaded', () => {
    if (window.innerWidth <= 991) {
        document.querySelectorAll('.sidebar-link').forEach(link => {
            link.addEventListener('click', () => {
                const sidebar = document.getElementById('sidebar');
                const overlay = document.getElementById('sidebarOverlay');
                sidebar.classList.remove('open');
                overlay.classList.remove('show');
            });
        });
    }
});


// ── Toast Notifications ─────────────────────────────────────────────

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const icons = {
        success: 'bi-check-circle-fill',
        danger: 'bi-exclamation-triangle-fill',
        warning: 'bi-exclamation-circle-fill',
        info: 'bi-info-circle-fill',
    };

    const colors = {
        success: '#22c55e',
        danger: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6',
    };

    const icon = icons[type] || icons.info;
    const color = colors[type] || colors.info;

    const toast = document.createElement('div');
    toast.className = 'toast show';
    toast.style.cssText = `
        background: rgba(16, 19, 32, 0.95);
        backdrop-filter: blur(12px);
        border-left: 3px solid ${color};
        min-width: 280px;
    `;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex align-items-center p-2">
            <i class="bi ${icon} me-2" style="color:${color}; font-size: 1rem;"></i>
            <div class="toast-body p-0 flex-grow-1">${message}</div>
            <button type="button" class="btn-close btn-close-white ms-2" style="font-size:0.6rem"
                    data-bs-dismiss="toast"></button>
        </div>
    `;

    container.appendChild(toast);

    // Slide in
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    toast.style.transition = 'all 0.3s ease';
    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    });

    // Auto-remove after 3.5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}


// ── Global Search ───────────────────────────────────────────────────

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
        html += '<div class="mb-3"><h6 style="color:var(--text-muted); font-size:0.75rem; text-transform:uppercase; letter-spacing:0.08em;">In Your Inventory</h6>';
        for (const match of data.inventory_matches) {
            html += `
                <div class="inventory-item mb-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <strong class="quality-unique">${match.item.name}</strong>
                        <span class="badge bg-secondary">${match.location}</span>
                    </div>
                </div>
            `;
        }
        html += '</div>';
    }

    // Database matches
    if (data.database_matches && data.database_matches.length > 0) {
        html += '<div><h6 style="color:var(--text-muted); font-size:0.75rem; text-transform:uppercase; letter-spacing:0.08em;">Database Results</h6>';
        for (const match of data.database_matches) {
            html += `
                <div class="inventory-item mb-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <strong class="quality-unique">${match.name}</strong>
                        <div class="d-flex align-items-center gap-2">
                            ${match.data.tier ? `<span class="tier-badge tier-${match.data.tier.toLowerCase()}">${match.data.tier}</span>` : ''}
                            <span class="badge bg-secondary">${match.category}</span>
                        </div>
                    </div>
                    ${match.data.est_fg ? `<div class="price-range mt-1">${match.data.est_fg} FG</div>` : ''}
                </div>
            `;
        }
        html += '</div>';
    }

    if (!html) {
        html = `
            <div class="empty-state">
                <div class="empty-state-icon"><i class="bi bi-search"></i></div>
                <div class="empty-state-text">No results found for "${query}"</div>
            </div>
        `;
    }

    container.innerHTML = html;
    new bootstrap.Modal(document.getElementById('searchModal')).show();
}


// ── Utility Functions ───────────────────────────────────────────────

function formatDate(isoString) {
    if (!isoString) return '-';
    const d = new Date(isoString);
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function truncate(str, len) {
    if (!str) return '';
    return str.length > len ? str.substring(0, len) + '...' : str;
}

// Class icon mapping for D2R
function getClassIcon(charClass) {
    const icons = {
        'Amazon': 'bi-bullseye',
        'Necromancer': 'bi-moon-stars',
        'Barbarian': 'bi-shield-shaded',
        'Sorceress': 'bi-stars',
        'Paladin': 'bi-shield-check',
        'Druid': 'bi-tree',
        'Assassin': 'bi-lightning-charge',
    };
    return icons[charClass] || 'bi-person';
}


// ── API Helper ──────────────────────────────────────────────────────

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


// ── Keyboard Shortcuts ──────────────────────────────────────────────

document.addEventListener('keydown', (e) => {
    // Ctrl+K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const input = document.getElementById('globalSearchInput');
        if (input) {
            input.focus();
            input.select();
        }
    }

    // Escape to close sidebar on mobile
    if (e.key === 'Escape') {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        if (sidebar && sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
            overlay.classList.remove('show');
        }
    }
});
