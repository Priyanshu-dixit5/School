(function () {
    'use strict';

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    // Sidebar toggle
    document.getElementById('sidebarToggle')?.addEventListener('click', () => {
        document.getElementById('adminSidebar')?.classList.toggle('show');
    });

    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const saved = localStorage.getItem('admin-theme') || 'light';
        document.documentElement.setAttribute('data-bs-theme', saved);
        themeToggle.addEventListener('click', () => {
            const next = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-bs-theme', next);
            localStorage.setItem('admin-theme', next);
        });
    }

    // Toast notifications
    window.showToast = function (message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        const id = 'toast-' + Date.now();
        const html = `<div id="${id}" class="toast align-items-center text-bg-${type} border-0" role="alert">
            <div class="d-flex"><div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div></div>`;
        container.insertAdjacentHTML('beforeend', html);
        const toast = new bootstrap.Toast(document.getElementById(id), { delay: 5000 });
        toast.show();
    };

    // Debounced global search
    const searchInput = document.getElementById('globalSearch');
    const searchResults = document.getElementById('searchResults');
    let searchTimer;
    if (searchInput && searchResults) {
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimer);
            const q = searchInput.value.trim();
            if (q.length < 2) { searchResults.classList.remove('show'); return; }
            searchTimer = setTimeout(async () => {
                try {
                    const res = await fetch(`/admin/search?q=${encodeURIComponent(q)}`, {
                        headers: { 'X-Requested-With': 'XMLHttpRequest' }
                    });
                    const data = await res.json();
                    if (data.length) {
                        searchResults.innerHTML = data.map(r =>
                            `<a href="${r.url}"><i class="bi bi-${r.type === 'job' ? 'briefcase' : r.type === 'application' ? 'file-person' : 'chat'} me-2"></i>${r.title} <small class="text-muted">(${r.type})</small></a>`
                        ).join('');
                        searchResults.classList.add('show');
                    } else {
                        searchResults.innerHTML = '<div class="p-3 text-muted">No results</div>';
                        searchResults.classList.add('show');
                    }
                } catch (e) { /* ignore */ }
            }, 300);
        });
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.remove('show');
            }
        });
    }

    // Socket.IO real-time updates
    if (typeof io !== 'undefined' && document.querySelector('.admin-layout')) {
        const socket = io('/admin');

        socket.on('new_application', (data) => {
            showToast(`New application from ${data.name}`, 'success');
            prependApplicationRow(data);
            incrementStat('statAppsToday');
        });

        socket.on('new_query', (data) => {
            showToast(`New query from ${data.name}`, 'warning');
            prependQueryRow(data);
            incrementStat('statUnreadQueries');
        });

        socket.on('job_created', () => showToast('New job created', 'info'));
        socket.on('job_updated', () => showToast('Job updated', 'info'));
        socket.on('job_deleted', () => showToast('Job deleted', 'danger'));
        socket.on('banner_updated', () => showToast('Banner updated', 'info'));
        socket.on('image_uploaded', () => showToast('Image uploaded', 'info'));
    }

    function incrementStat(id) {
        const el = document.getElementById(id);
        if (el) el.textContent = parseInt(el.textContent || '0', 10) + 1;
    }

    function prependApplicationRow(data) {
        const table = document.querySelector('#recentAppsTable tbody, #applicationsTable tbody');
        if (!table) return;
        const empty = table.querySelector('td[colspan]');
        if (empty) empty.parentElement.remove();
        const tr = document.createElement('tr');
        tr.innerHTML = `<td><a href="/admin/applications/${data.id}">${data.name}</a></td>
            <td>${data.job_title || '—'}</td>
            <td><span class="badge status-${data.status}">${data.status}</span></td>
            <td class="text-secondary small">Just now</td>`;
        table.prepend(tr);
    }

    function prependQueryRow(data) {
        const table = document.querySelector('#recentQueriesTable tbody, #queriesTable tbody');
        if (!table) return;
        const empty = table.querySelector('td[colspan]');
        if (empty) empty.parentElement.remove();
        const tr = document.createElement('tr');
        tr.className = 'table-warning';
        tr.innerHTML = `<td><a href="/admin/queries/${data.id}">${data.name}</a></td>
            <td>${data.subject || data.query_type}</td>
            <td><span class="badge status-${data.status}">${data.status}</span></td>
            <td class="text-secondary small">Just now</td>`;
        table.prepend(tr);
    }

    // Dashboard charts
    if (window.dashboardCharts) {
        initCharts(window.dashboardCharts);
    }

    function initCharts(charts) {
        const appData = charts.application_growth || [];
        const jobsData = charts.monthly_jobs || [];

        const appCtx = document.getElementById('appGrowthChart') || document.getElementById('analyticsAppChart');
        if (appCtx && typeof Chart !== 'undefined') {
            new Chart(appCtx, {
                type: 'line',
                data: {
                    labels: appData.map(d => d.month),
                    datasets: [{
                        label: 'Applications',
                        data: appData.map(d => d.count),
                        borderColor: '#2563EB',
                        backgroundColor: 'rgba(37,99,235,0.1)',
                        fill: true,
                        tension: 0.4,
                    }]
                },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });
        }

        const jobsCtx = document.getElementById('jobsChart') || document.getElementById('analyticsJobsChart');
        if (jobsCtx && typeof Chart !== 'undefined') {
            new Chart(jobsCtx, {
                type: 'bar',
                data: {
                    labels: jobsData.map(d => d.month),
                    datasets: [{
                        label: 'Jobs',
                        data: jobsData.map(d => d.count),
                        backgroundColor: '#1E4D8C',
                        borderRadius: 6,
                    }]
                },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });
        }
    }
})();
