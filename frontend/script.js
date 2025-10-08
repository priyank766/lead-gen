document.addEventListener('DOMContentLoaded', () => {
    const scrapeButton = document.getElementById('scrape-button');
    const urlInput = document.getElementById('url-input');
    const loadingDiv = document.getElementById('loading');
    const resultsContainer = document.getElementById('results-container');
    const resultsTableBody = document.querySelector('#results-table tbody');
    const exportButton = document.getElementById('export-button');
    const modal = document.getElementById('details-modal');
    const modalJson = document.getElementById('modal-json');
    const modalClose = document.getElementById('modal-close');
    const metricsBar = document.getElementById('metrics');
    const mCount = document.getElementById('m-count');
    const mEmail = document.getElementById('m-email');
    const mPhone = document.getElementById('m-phone');
    const mAvg = document.getElementById('m-avg');
    const themeToggle = document.getElementById('theme-toggle');

    let leadsData = [];

    scrapeButton.addEventListener('click', async () => {
        const url = urlInput.value;
        if (!url) {
            showToast('Please enter a URL.');
            return;
        }

        setLoading(scrapeButton, true);
        loadingDiv.classList.remove('hidden');
        resultsContainer.classList.add('hidden');
        resultsTableBody.innerHTML = '';
        leadsData = [];

        try {
            // 1. Scrape and extract
            const extractResponse = await fetch('http://127.0.0.1:8000/api/extract/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url }),
            });

            if (!extractResponse.ok) throw new Error('Failed to extract data.');

            const extractedData = await extractResponse.json();
            if (!extractedData || !extractedData.data) {
                const msg = extractedData && extractedData.error ? extractedData.error : 'No data extracted.';
                throw new Error(msg);
            }
            const lead = { ...(extractedData.data || {}), source_urls: [url] };

            // 2. Process (deduplicate and score)
            const processResponse = await fetch('http://127.0.0.1:8000/api/process_leads/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ leads: [lead] }),
            });

            if (!processResponse.ok) throw new Error('Failed to process leads.');

            const processedData = await processResponse.json();
            leadsData = processedData.processed_leads;

            // 3. Display results and metrics
            displayResults(leadsData);
            displayMetrics(leadsData);

        } catch (error) {
            showToast(error.message || 'Something went wrong');
        } finally {
            setLoading(scrapeButton, false);
            loadingDiv.classList.add('hidden');
        }
    });

    exportButton.addEventListener('click', async () => {
        if (leadsData.length === 0) return showToast('No leads to export.');

        try {
            const response = await fetch('http://127.0.0.1:8000/api/export_leads/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ leads: leadsData }),
            });

            if (!response.ok) throw new Error('Failed to export leads.');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'leads.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);

        } catch (error) {
            showToast(error.message || 'Export failed');
        }
    });

    function displayResults(leads) {
        console.log(leads);
        resultsTableBody.innerHTML = ''; // Clear existing rows
        resultsContainer.classList.remove('hidden');
        leads.forEach(lead => {
            const row = document.createElement('tr');
            const justification = lead.justification ? lead.justification.replace(/\n/g, '<br>') : '';
            const validationHtml = renderValidationBadges(lead);
            row.innerHTML = `
                <td>${lead.company_name || ''}</td>
                <td>${lead.domain || ''}</td>
                <td>${(lead.emails || []).join(', ')}</td>
                <td>${(lead.phones || []).join(', ')}</td>
                <td>${lead.linkedin || ''}</td>
                <td>${lead.has_contact_page ? 'Yes' : 'No'}</td>
                <td>${lead.has_pricing ? 'Yes' : 'No'}</td>
                <td>${validationHtml}</td>
                <td>${lead.score || ''}</td>
                <td>${justification}</td>
                <td><button class="details-btn">Details</button></td>
            `;
            row.querySelector('.details-btn').addEventListener('click', () => {
                const toShow = {
                    company_name: lead.company_name,
                    domain: lead.domain,
                    emails: lead.emails,
                    phones: lead.phones,
                    linkedin: lead.linkedin,
                    has_contact_page: lead.has_contact_page,
                    has_pricing: lead.has_pricing,
                    score: lead.score,
                    score_breakdown: lead.score_breakdown,
                    industry: lead.industry,
                    tech_stack: lead.tech_stack,
                    title: lead.title,
                    intent_phrases: lead.intent_phrases,
                    source_urls: lead.source_urls,
                };
                modalJson.textContent = JSON.stringify(toShow, null, 2);
                modal.classList.remove('hidden');
            });
            resultsTableBody.appendChild(row);
        });
    }

    function displayMetrics(leads) {
        if (!leads || leads.length === 0) {
            metricsBar.classList.add('hidden');
            return;
        }
        const total = leads.length;
        const emailCov = (100 * leads.filter(l => (l.emails || []).length > 0).length / total) | 0;
        const phoneCov = (100 * leads.filter(l => (l.phones || []).length > 0).length / total) | 0;
        const avgScore = (leads.reduce((s, l) => s + (l.score || 0), 0) / total).toFixed(1);
        mCount.textContent = total;
        mEmail.textContent = emailCov + '%';
        mPhone.textContent = phoneCov + '%';
        mAvg.textContent = avgScore;
        metricsBar.classList.remove('hidden');
    }

    function renderValidationBadges(lead) {
        const badges = [];
        badges.push(badge((lead.emails || []).length > 0, 'Email'));
        badges.push(badge((lead.phones || []).length > 0, 'Phone'));
        badges.push(badge(!!lead.linkedin, 'LinkedIn'));
        badges.push(badge(!!lead.has_contact_page, 'Contact'));
        badges.push(badge(!!lead.has_pricing, 'Pricing'));
        return badges.join(' ');
    }

    function badge(ok, label) {
        const cls = ok ? 'ok' : 'warn';
        return `<span class="badge ${cls}">${label}</span>`;
    }

    modalClose.addEventListener('click', () => modal.classList.add('hidden'));
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.add('hidden');
    });

    function showToast(msg) {
        const toast = document.getElementById('toast');
        toast.textContent = msg;
        toast.classList.remove('hidden');
        setTimeout(() => toast.classList.add('hidden'), 2500);
    }

    function setLoading(button, isLoading) {
        const label = button.querySelector('.btn-label');
        const spinner = button.querySelector('.btn-spinner');
        if (isLoading) {
            button.setAttribute('disabled', 'true');
            if (spinner) spinner.classList.remove('hidden');
        } else {
            button.removeAttribute('disabled');
            if (spinner) spinner.classList.add('hidden');
        }
    }

    // Theme management
    initTheme();
    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme') || 'light';
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        themeToggle.textContent = next === 'dark' ? '☀️' : '🌙';
    });

    function initTheme() {
        const saved = localStorage.getItem('theme');
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        const theme = saved || (prefersDark ? 'dark' : 'light');
        document.documentElement.setAttribute('data-theme', theme);
        if (themeToggle) themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
});
