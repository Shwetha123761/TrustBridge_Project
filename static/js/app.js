document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileSelectedName = document.getElementById('file-selected-name');
    const uploadForm = document.getElementById('upload-form');
    const submitBtn = document.getElementById('submit-btn');
    const loader = document.getElementById('loader');
    const resultsDashboard = document.getElementById('results-dashboard');
    let selectedFile = null;

    themeToggle.addEventListener('click', () => {
        const isDark = document.body.getAttribute('data-theme') === 'dark';
        document.body.setAttribute('data-theme', isDark ? 'light' : 'dark');
    });

    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => { if(e.target.files.length) handleFile(e.target.files[0]); });
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); });
    dropZone.addEventListener('drop', (e) => { e.preventDefault(); if(e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]); });

    function handleFile(file) {
        selectedFile = file;
        fileSelectedName.textContent = `Selected: ${file.name}`;
        submitBtn.disabled = false;
    }

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('file', selectedFile);
        loader.style.display = 'block';
        resultsDashboard.style.display = 'none';

        try {
            const res = await fetch('/verify', { method: 'POST', body: formData });
            const data = await res.json();
            if(!res.ok) throw new Error(data.error);
            renderDashboard(data);
        } catch(err) { alert(err.message); }
        finally { loader.style.display = 'none'; }
    });

    function renderDashboard(data) {
        document.getElementById('score-num').textContent = data.trust_score;
        const badge = document.getElementById('risk-badge');
        badge.textContent = data.risk_level;
        badge.className = 'risk-badge ' + (data.risk_level === 'LOW' ? 'bg-safe' : data.risk_level === 'MEDIUM' ? 'bg-warning' : 'bg-danger');
        document.getElementById('ai-summary').textContent = data.ai_analysis;

        const grid = document.getElementById('entities-grid');
        grid.innerHTML = '';
        for(const [k, v] of Object.entries(data.entities)) {
            grid.innerHTML += `<div class="entity-item"><div class="entity-label">${k}</div><div class="entity-val">${v}</div></div>`;
        }

        const rList = document.getElementById('rule-list');
        rList.innerHTML = '';
        data.rule_results.forEach(r => {
            rList.innerHTML += `<li><strong>${r.name}</strong>: ${r.description} (${r.points})</li>`;
        });

        const hRows = document.getElementById('history-rows');
        hRows.innerHTML = `<tr><td style="padding:10px;">${data.entities.company || 'Unknown'}</td><td style="padding:10px;">${data.entities.role || 'Unknown'}</td><td style="padding:10px;">${data.trust_score}/100</td></tr>` + hRows.innerHTML;
        resultsDashboard.style.display = 'block';
    }
});
