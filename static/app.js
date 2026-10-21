/**
 * CareerAI - Core Client-Side Logic
 * State management, interactive tags, Chart.js visualizations,
 * ML recommendation inference, resume parsing, and dataset explorer.
 */

// Global App State
const state = {
    allSkills: [],
    categorizedSkills: {},
    allInterests: [],
    selectedSkills: new Set(),
    selectedInterests: new Set(),
    selectedCategory: 'all',
    activeTab: 'tab-predict',
    catalogData: {},
    datasetRecords: [],
    chartsInitialized: false,
    charts: {}
};

// DOM Content Loaded Initializer
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initTabs();
    initAgeSlider();
    initResumeDrawer();
    initFormListeners();
    loadSkillsAndInterests();
    loadSampleProfiles();
    loadDatasetStats();
    loadCareerCatalog();
    loadDatasetTable();
});

/* ==========================================================================
   Theme Switcher (Dark / Light)
   ========================================================================== */
function initTheme() {
    const themeBtn = document.getElementById('theme-toggle');
    // Default to light theme as requested
    let savedTheme = localStorage.getItem('careerai-theme');
    if (!savedTheme || savedTheme === 'dark') {
        savedTheme = 'light';
        localStorage.setItem('careerai-theme', 'light');
    }
    document.documentElement.setAttribute('data-theme', savedTheme);

    themeBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('careerai-theme', newTheme);

        // Update charts theme if already rendered
        if (state.chartsInitialized) {
            updateChartsTheme(newTheme);
        }
    });
}

/* ==========================================================================
   Tab Navigation
   ========================================================================== */
function initTabs() {
    const tabButtons = document.querySelectorAll('.nav-tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');

            tabButtons.forEach(b => {
                b.classList.remove('active');
                b.setAttribute('aria-selected', 'false');
            });
            tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            btn.setAttribute('aria-selected', 'true');
            const targetPane = document.getElementById(targetTab);
            if (targetPane) {
                targetPane.classList.add('active');
            }

            state.activeTab = targetTab;

            // Trigger chart render if switching to Analytics tab
            if (targetTab === 'tab-analytics' && !state.chartsInitialized) {
                renderAllCharts();
            }
        });
    });
}

/* ==========================================================================
   Age Range Slider Sync
   ========================================================================== */
function initAgeSlider() {
    const ageInput = document.getElementById('candidate-age');
    const ageBadge = document.getElementById('age-val-badge');

    ageInput.addEventListener('input', (e) => {
        ageBadge.textContent = `${e.target.value} yrs`;
    });
}

/* ==========================================================================
   Resume & Bio Skill Extractor
   ========================================================================== */
function initResumeDrawer() {
    const toggleBtn = document.getElementById('toggle-resume-btn');
    const drawer = document.getElementById('resume-drawer');
    const extractBtn = document.getElementById('btn-extract-skills');
    const resumeInput = document.getElementById('resume-input');
    const msg = document.getElementById('extraction-msg');

    toggleBtn.addEventListener('click', () => {
        const isHidden = drawer.style.display === 'none';
        drawer.style.display = isHidden ? 'block' : 'none';
    });

    extractBtn.addEventListener('click', async () => {
        const text = resumeInput.value.trim();
        if (!text) {
            msg.textContent = 'Please paste some text first.';
            msg.style.color = 'var(--amber)';
            return;
        }

        extractBtn.disabled = true;
        msg.textContent = 'Analyzing text with NLP regex extractor...';
        msg.style.color = 'var(--cyan)';

        try {
            const resp = await fetch('/api/extract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            if (!resp.ok) throw new Error('Extraction failed');
            const data = await resp.json();

            let addedCount = 0;
            // Add extracted skills
            if (data.skills && data.skills.length > 0) {
                data.skills.forEach(s => {
                    state.selectedSkills.add(s);
                    addedCount++;
                });
            }

            // Add extracted interests
            if (data.interests && data.interests.length > 0) {
                data.interests.forEach(i => {
                    state.selectedInterests.add(i);
                });
            }

            updateSkillTagsUI();
            updateInterestTagsUI();

            msg.textContent = `✓ Auto-filled ${data.skills.length} skills & ${data.interests.length} interests!`;
            msg.style.color = 'var(--emerald)';
        } catch (err) {
            msg.textContent = 'Extraction failed. Please try again.';
            msg.style.color = 'var(--rose)';
        } finally {
            extractBtn.disabled = false;
        }
    });
}

/* ==========================================================================
   Load Skills and Interests from API
   ========================================================================== */
async function loadSkillsAndInterests() {
    try {
        const [skillsRes, interestsRes] = await Promise.all([
            fetch('/api/skills'),
            fetch('/api/interests')
        ]);

        const skillsData = await skillsRes.json();
        const interestsData = await interestsRes.json();

        state.allSkills = skillsData.all_skills;
        state.categorizedSkills = skillsData.categorized;
        state.allInterests = interestsData.all_interests;

        // Default selections
        ['Python', 'Machine Learning', 'Data Analysis'].forEach(s => state.selectedSkills.add(s));
        ['Technology', 'Data Science'].forEach(i => state.selectedInterests.add(i));

        initSkillCategoryFilters();
        initSkillSearch();
        initCustomSkill();
        updateSkillTagsUI();
        updateInterestTagsUI();
    } catch (err) {
        console.error('Failed to load skills or interests:', err);
    }
}

/* Category Filter for Skills */
function initSkillCategoryFilters() {
    const container = document.getElementById('skill-category-filters');
    const filterButtons = container.querySelectorAll('.filter-chip');

    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.selectedCategory = btn.getAttribute('data-cat');
            updateSkillTagsUI();
        });
    });
}

/* Search input filter for skills */
function initSkillSearch() {
    const searchInput = document.getElementById('skill-search');
    searchInput.addEventListener('input', () => {
        updateSkillTagsUI();
    });
}

/* Custom Skill Input */
function initCustomSkill() {
    const input = document.getElementById('custom-skill-input');
    const addBtn = document.getElementById('btn-add-custom-skill');

    const addSkill = () => {
        const val = input.value.trim();
        if (val) {
            state.selectedSkills.add(val);
            if (!state.allSkills.includes(val)) {
                state.allSkills.push(val);
            }
            input.value = '';
            updateSkillTagsUI();
        }
    };

    addBtn.addEventListener('click', addSkill);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addSkill();
        }
    });
}

/* Render / Update Skill Tags */
function updateSkillTagsUI() {
    const container = document.getElementById('skills-tags-cloud');
    const counterBadge = document.getElementById('skills-count-badge');
    const searchVal = document.getElementById('skill-search').value.toLowerCase().trim();

    counterBadge.textContent = `${state.selectedSkills.size} selected`;

    // Filter skills based on active category & search string
    let availableSkills = state.allSkills;
    if (state.selectedCategory !== 'all') {
        availableSkills = state.categorizedSkills[state.selectedCategory] || [];
    }

    if (searchVal) {
        availableSkills = availableSkills.filter(s => s.toLowerCase().includes(searchVal));
    }

    container.innerHTML = '';
    availableSkills.forEach(skill => {
        const isSelected = state.selectedSkills.has(skill);
        const chip = document.createElement('span');
        chip.className = `tag-chip ${isSelected ? 'active' : ''}`;
        chip.textContent = skill;
        chip.title = isSelected ? 'Click to deselect' : 'Click to select';

        chip.addEventListener('click', () => {
            if (state.selectedSkills.has(skill)) {
                state.selectedSkills.delete(skill);
            } else {
                state.selectedSkills.add(skill);
            }
            updateSkillTagsUI();
        });

        container.appendChild(chip);
    });
}

/* Render / Update Interest Tags */
function updateInterestTagsUI() {
    const container = document.getElementById('interests-tags-cloud');
    const counterBadge = document.getElementById('interests-count-badge');

    counterBadge.textContent = `${state.selectedInterests.size} selected`;
    container.innerHTML = '';

    state.allInterests.forEach(interest => {
        const isSelected = state.selectedInterests.has(interest);
        const chip = document.createElement('span');
        chip.className = `tag-chip ${isSelected ? 'active' : ''}`;
        chip.textContent = interest;

        chip.addEventListener('click', () => {
            if (state.selectedInterests.has(interest)) {
                state.selectedInterests.delete(interest);
            } else {
                state.selectedInterests.add(interest);
            }
            updateInterestTagsUI();
        });

        container.appendChild(chip);
    });
}

/* ==========================================================================
   Quick Test Profiles
   ========================================================================== */
async function loadSampleProfiles() {
    try {
        const res = await fetch('/api/samples');
        const profiles = await res.json();
        const container = document.getElementById('samples-container');

        container.innerHTML = '';
        profiles.forEach(p => {
            const pill = document.createElement('button');
            pill.type = 'button';
            pill.className = 'sample-pill';
            pill.textContent = `${p.title} (${p.badge})`;

            pill.addEventListener('click', () => {
                // Populate inputs
                document.getElementById('candidate-name').value = p.name;
                document.getElementById('candidate-age').value = p.age;
                document.getElementById('age-val-badge').textContent = `${p.age} yrs`;

                // Set education radio
                const eduRadio = document.querySelector(`input[name="education"][value="${p.education}"]`);
                if (eduRadio) eduRadio.checked = true;

                // Set skills
                state.selectedSkills.clear();
                p.skills.forEach(s => state.selectedSkills.add(s));

                // Set interests
                state.selectedInterests.clear();
                p.interests.forEach(i => state.selectedInterests.add(i));

                updateSkillTagsUI();
                updateInterestTagsUI();

                // Trigger prediction
                document.getElementById('prediction-form').dispatchEvent(new Event('submit'));
            });

            container.appendChild(pill);
        });
    } catch (err) {
        console.error('Failed to load sample profiles:', err);
    }
}

/* ==========================================================================
   Form Submission & Career Prediction
   ========================================================================== */
function initFormListeners() {
    const form = document.getElementById('prediction-form');
    const submitBtn = document.getElementById('btn-predict-submit');
    const printBtn = document.getElementById('btn-print-report');
    const resetBtn = document.getElementById('btn-reset-form');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('candidate-name').value.trim() || 'Candidate';
        const age = parseInt(document.getElementById('candidate-age').value);
        const education = document.querySelector('input[name="education"]:checked').value;
        const skills = Array.from(state.selectedSkills);
        const interests = Array.from(state.selectedInterests);

        if (skills.length === 0) {
            alert('Please select or enter at least one technical skill.');
            return;
        }

        // Loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 1s linear infinite; width: 18px; height: 18px;">
                <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
                <path d="M12 2a10 10 0 0 1 10 10"></path>
            </svg>
            <span>Analyzing Profile with Random Forest...</span>
        `;

        try {
            const res = await fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, age, education, skills, interests })
            });

            if (!res.ok) throw new Error('Prediction API call failed');
            const data = await res.json();

            displayPredictionResults(data);
        } catch (err) {
            console.error('Prediction error:', err);
            alert('Prediction failed. Please ensure the backend server is running.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"></path></svg>
                <span>Generate AI Recommendation & Skill Gap</span>
            `;
        }
    });

    printBtn.addEventListener('click', () => {
        window.print();
    });

    resetBtn.addEventListener('click', () => {
        state.selectedSkills.clear();
        state.selectedInterests.clear();
        updateSkillTagsUI();
        updateInterestTagsUI();
        document.getElementById('results-active-card').style.display = 'none';
        document.getElementById('results-empty-state').style.display = 'flex';
    });
}

/* ==========================================================================
   Render Prediction Results
   ========================================================================== */
function displayPredictionResults(data) {
    const emptyState = document.getElementById('results-empty-state');
    const activeCard = document.getElementById('results-active-card');

    emptyState.style.display = 'none';
    activeCard.style.display = 'flex';

    const rec = data.recommendation;
    const gap = data.skill_gap;
    const cand = data.candidate;

    // Hero details
    document.getElementById('rec-category').textContent = rec.category;
    document.getElementById('rec-demand').textContent = `🔥 ${rec.demand}`;
    document.getElementById('rec-career-title').textContent = rec.career;
    document.getElementById('rec-description').textContent = rec.description;
    document.getElementById('rec-salary').textContent = rec.salary_range;
    document.getElementById('rec-candidate-name').textContent = `${cand.name} (Age ${cand.age}, ${cand.education})`;

    // Circular Score Gauge Animation
    const scorePct = rec.score_percent;
    document.getElementById('rec-score-pct').textContent = `${Math.round(scorePct)}%`;

    const circleBar = document.getElementById('score-circle-bar');
    const circumference = 2 * Math.PI * 50; // r = 50 -> ~314.16
    const offset = circumference - (scorePct / 100) * circumference;
    circleBar.style.strokeDasharray = `${circumference}`;
    circleBar.style.strokeDashoffset = `${offset}`;

    // Skill Gap Analysis
    document.getElementById('skill-coverage-rate').textContent = `${gap.match_rate}%`;

    const matchedContainer = document.getElementById('matched-skills-chips');
    matchedContainer.innerHTML = '';
    if (gap.matched_skills && gap.matched_skills.length > 0) {
        gap.matched_skills.forEach(s => {
            const chip = document.createElement('span');
            chip.className = 'skill-chip possessed';
            chip.textContent = `✓ ${s}`;
            matchedContainer.appendChild(chip);
        });
    } else {
        matchedContainer.innerHTML = '<span class="text-dim">No direct match</span>';
    }

    const missingContainer = document.getElementById('missing-skills-chips');
    missingContainer.innerHTML = '';
    if (gap.missing_skills && gap.missing_skills.length > 0) {
        gap.missing_skills.forEach(s => {
            const chip = document.createElement('span');
            chip.className = 'skill-chip missing';
            chip.textContent = `+ ${s}`;
            missingContainer.appendChild(chip);
        });
    } else {
        missingContainer.innerHTML = '<span class="skill-chip possessed">✓ All core skills covered!</span>';
    }

    // Top 5 Alternatives
    const altsContainer = document.getElementById('alternatives-container');
    altsContainer.innerHTML = '';
    data.top_alternatives.forEach(alt => {
        const item = document.createElement('div');
        item.className = 'alt-career-item';
        item.innerHTML = `
            <div class="alt-left">
                <span class="alt-title">${alt.career}</span>
                <span class="alt-cat">${alt.category} • Core: ${alt.top_skills.join(', ')}</span>
            </div>
            <div class="alt-right">
                <div class="progress-bar-wrap">
                    <div class="progress-bar-fill" style="width: ${alt.score}%;"></div>
                </div>
                <span class="alt-pct">${alt.score}%</span>
            </div>
        `;
        altsContainer.appendChild(item);
    });

    // Roadmap Steps
    const roadmapContainer = document.getElementById('roadmap-container');
    roadmapContainer.innerHTML = '';
    data.roadmap.forEach(step => {
        const stepItem = document.createElement('div');
        stepItem.className = 'roadmap-step-item';
        stepItem.innerHTML = `
            <div class="step-num">${step.step}</div>
            <div class="step-content">
                <strong class="step-title">${step.title}</strong>
                <p class="step-desc">${step.detail}</p>
            </div>
        `;
        roadmapContainer.appendChild(stepItem);
    });

    // Smooth scroll into results view on mobile
    if (window.innerWidth < 1100) {
        activeCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/* ==========================================================================
   Tab 2: EDA & Dataset Analytics Charts (Chart.js)
   ========================================================================== */
let statsDataCache = null;

async function loadDatasetStats() {
    try {
        const res = await fetch('/api/stats');
        statsDataCache = await res.json();

        // Populate KPI Counters
        document.getElementById('kpi-candidates').textContent = statsDataCache.total_candidates;
        document.getElementById('kpi-careers').textContent = statsDataCache.total_careers;
        document.getElementById('kpi-age').textContent = `${statsDataCache.avg_age} yrs`;
        document.getElementById('kpi-score').textContent = statsDataCache.avg_score;

        // Model Tab Metrics
        const m = statsDataCache.model_metrics;
        document.getElementById('metric-top1').textContent = `${m.top1_acc}%`;
        document.getElementById('metric-top3').textContent = `${m.top3_acc}%`;
        document.getElementById('metric-top5').textContent = `${m.top5_acc}%`;
    } catch (err) {
        console.error('Failed to load dataset stats:', err);
    }
}

function renderAllCharts() {
    if (!statsDataCache || state.chartsInitialized) return;

    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    const textColor = isDark ? '#cbd5e1' : '#334155';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)';

    // Chart 1: Distribution of Recommended Careers (Horizontal Bar)
    const ctxCareers = document.getElementById('chart-career-dist').getContext('2d');
    const careerLabels = Object.keys(statsDataCache.career_distribution);
    const careerCounts = Object.values(statsDataCache.career_distribution);

    state.charts.careers = new Chart(ctxCareers, {
        type: 'bar',
        data: {
            labels: careerLabels,
            datasets: [{
                label: 'Candidate Count',
                data: careerCounts,
                backgroundColor: 'rgba(99, 102, 241, 0.75)',
                borderColor: '#6366f1',
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: gridColor },
                    ticks: { color: textColor }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: textColor, font: { weight: '600' } }
                }
            }
        }
    });

    // Chart 2: Top Skills Distribution
    const ctxSkills = document.getElementById('chart-skills-dist').getContext('2d');
    const skillLabels = Object.keys(statsDataCache.top_skills);
    const skillCounts = Object.values(statsDataCache.top_skills);

    state.charts.skills = new Chart(ctxSkills, {
        type: 'bar',
        data: {
            labels: skillLabels,
            datasets: [{
                label: 'Skill Mentions',
                data: skillCounts,
                backgroundColor: 'rgba(6, 182, 212, 0.75)',
                borderColor: '#06b6d4',
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: textColor, maxRotation: 45, minRotation: 45 }
                },
                y: {
                    grid: { color: gridColor },
                    ticks: { color: textColor }
                }
            }
        }
    });

    // Chart 3: Education Level Breakdown (Donut)
    const ctxEdu = document.getElementById('chart-edu-dist').getContext('2d');
    const eduLabels = Object.keys(statsDataCache.education_distribution);
    const eduCounts = Object.values(statsDataCache.education_distribution);

    state.charts.edu = new Chart(ctxEdu, {
        type: 'doughnut',
        data: {
            labels: eduLabels,
            datasets: [{
                data: eduCounts,
                backgroundColor: [
                    '#6366f1',
                    '#06b6d4',
                    '#10b981'
                ],
                borderColor: isDark ? '#0f172a' : '#ffffff',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: textColor, font: { weight: '600' } }
                }
            }
        }
    });

    // Chart 4: Age Distribution (Bar/Histogram)
    const ctxAge = document.getElementById('chart-age-dist').getContext('2d');
    const ageLabels = Object.keys(statsDataCache.age_distribution);
    const ageCounts = Object.values(statsDataCache.age_distribution);

    state.charts.age = new Chart(ctxAge, {
        type: 'bar',
        data: {
            labels: ageLabels,
            datasets: [{
                label: 'Candidates',
                data: ageCounts,
                backgroundColor: 'rgba(16, 185, 129, 0.75)',
                borderColor: '#10b981',
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: textColor }
                },
                y: {
                    grid: { color: gridColor },
                    ticks: { color: textColor }
                }
            }
        }
    });

    // Chart 5: Top Interests Distribution
    const ctxInterests = document.getElementById('chart-interests-dist').getContext('2d');
    const interestLabels = Object.keys(statsDataCache.top_interests);
    const interestCounts = Object.values(statsDataCache.top_interests);

    state.charts.interests = new Chart(ctxInterests, {
        type: 'bar',
        data: {
            labels: interestLabels,
            datasets: [{
                label: 'Interests Count',
                data: interestCounts,
                backgroundColor: 'rgba(245, 158, 11, 0.75)',
                borderColor: '#f59e0b',
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: textColor, maxRotation: 45, minRotation: 45 }
                },
                y: {
                    grid: { color: gridColor },
                    ticks: { color: textColor }
                }
            }
        }
    });

    state.chartsInitialized = true;
}

function updateChartsTheme(theme) {
    const isDark = theme !== 'light';
    const textColor = isDark ? '#cbd5e1' : '#334155';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)';

    Object.values(state.charts).forEach(chart => {
        if (!chart) return;
        if (chart.options.scales) {
            if (chart.options.scales.x) {
                chart.options.scales.x.ticks.color = textColor;
                if (chart.options.scales.x.grid) chart.options.scales.x.grid.color = gridColor;
            }
            if (chart.options.scales.y) {
                chart.options.scales.y.ticks.color = textColor;
                if (chart.options.scales.y.grid) chart.options.scales.y.grid.color = gridColor;
            }
        }
        if (chart.options.plugins && chart.options.plugins.legend) {
            chart.options.plugins.legend.labels.color = textColor;
        }
        chart.update();
    });
}

/* ==========================================================================
   Tab 4: Career Catalog Directory
   ========================================================================== */
async function loadCareerCatalog() {
    try {
        const res = await fetch('/api/catalog');
        state.catalogData = await res.json();
        renderCatalogCards();

        // Search input
        document.getElementById('catalog-search').addEventListener('input', () => {
            renderCatalogCards();
        });

        // Domain filters
        const filterChips = document.querySelectorAll('#catalog-domain-filters .filter-chip');
        filterChips.forEach(chip => {
            chip.addEventListener('click', () => {
                filterChips.forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                renderCatalogCards();
            });
        });
    } catch (err) {
        console.error('Failed to load career catalog:', err);
    }
}

function renderCatalogCards() {
    const container = document.getElementById('catalog-cards-container');
    const searchVal = document.getElementById('catalog-search').value.toLowerCase().trim();
    const activeDomainChip = document.querySelector('#catalog-domain-filters .filter-chip.active');
    const selectedDomain = activeDomainChip ? activeDomainChip.getAttribute('data-domain') : 'all';

    container.innerHTML = '';
    const careers = Object.values(state.catalogData);

    let filtered = careers.filter(c => {
        // Domain match
        const matchesDomain = (selectedDomain === 'all') || 
            (c.category && c.category.toLowerCase().includes(selectedDomain.toLowerCase()));

        // Search match
        const matchesSearch = !searchVal || 
            c.name.toLowerCase().includes(searchVal) ||
            (c.top_skills && c.top_skills.some(s => s.toLowerCase().includes(searchVal))) ||
            (c.description && c.description.toLowerCase().includes(searchVal));

        return matchesDomain && matchesSearch;
    });

    filtered.forEach(c => {
        const card = document.createElement('div');
        card.className = 'catalog-card';
        card.innerHTML = `
            <div class="cat-header">
                <div>
                    <h3 class="cat-title">${c.name}</h3>
                    <span class="cat-domain">${c.category || 'General'}</span>
                </div>
                <span class="cat-demand">${c.demand || 'High Demand'}</span>
            </div>
            <p class="cat-desc">${c.description || 'Dynamic profession with wide opportunities.'}</p>
            <div>
                <strong style="font-size: 0.76rem; color: var(--text-muted); display: block; margin-bottom: 4px;">Top Skills:</strong>
                <div class="cat-skills-box">
                    ${(c.top_skills || []).map(s => `<span class="cat-skill-chip">${s}</span>`).join('')}
                </div>
            </div>
            <div class="cat-footer">
                <span class="cat-salary">${c.salary_range}</span>
                <span>Avg Age: ${c.avg_age} yrs</span>
            </div>
        `;
        container.appendChild(card);
    });
}

/* ==========================================================================
   Tab 5: Raw Dataset Explorer
   ========================================================================== */
async function loadDatasetTable() {
    const searchInput = document.getElementById('dataset-search-input');
    const countBadge = document.getElementById('dataset-count-badge');
    const tbody = document.getElementById('dataset-tbody');

    const fetchRecords = async (query = '') => {
        try {
            const url = query ? `/api/dataset?search=${encodeURIComponent(query)}&limit=200` : '/api/dataset?limit=200';
            const res = await fetch(url);
            const data = await res.json();

            countBadge.textContent = `Showing ${data.returned} of ${data.total} candidates`;
            tbody.innerHTML = '';

            data.records.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>#${row.CandidateID}</strong></td>
                    <td>${row.Name}</td>
                    <td>${row.Age}</td>
                    <td><span class="skill-chip possessed">${row.Education}</span></td>
                    <td style="max-width: 200px; font-size: 0.78rem;">${row.Skills}</td>
                    <td style="max-width: 180px; font-size: 0.78rem; color: var(--text-muted);">${row.Interests}</td>
                    <td><strong style="color: var(--cyan);">${row.Recommended_Career}</strong></td>
                    <td><strong>${row.Recommendation_Score}</strong></td>
                    <td>
                        <button type="button" class="action-load-btn" data-id="${row.CandidateID}">
                            Load Profile
                        </button>
                    </td>
                `;

                // Load row profile into predictor tab
                tr.querySelector('.action-load-btn').addEventListener('click', () => {
                    loadCandidateRowIntoPredictor(row);
                });

                tbody.appendChild(tr);
            });
        } catch (err) {
            console.error('Failed to load dataset rows:', err);
        }
    };

    fetchRecords();

    // Debounced search
    let timer = null;
    searchInput.addEventListener('input', () => {
        clearTimeout(timer);
        timer = setTimeout(() => {
            fetchRecords(searchInput.value.trim());
        }, 300);
    });
}

function loadCandidateRowIntoPredictor(row) {
    document.getElementById('candidate-name').value = row.Name;
    document.getElementById('candidate-age').value = row.Age;
    document.getElementById('age-val-badge').textContent = `${row.Age} yrs`;

    const eduRadio = document.querySelector(`input[name="education"][value="${row.Education}"]`);
    if (eduRadio) eduRadio.checked = true;

    // Parse and set skills
    state.selectedSkills.clear();
    if (row.Skills) {
        row.Skills.split(';').map(s => s.trim()).filter(Boolean).forEach(s => state.selectedSkills.add(s));
    }

    // Parse and set interests
    state.selectedInterests.clear();
    if (row.Interests) {
        row.Interests.split(';').map(i => i.trim()).filter(Boolean).forEach(i => state.selectedInterests.add(i));
    }

    updateSkillTagsUI();
    updateInterestTagsUI();

    // Switch to predict tab
    document.getElementById('nav-predict-tab').click();

    // Trigger recommendation
    document.getElementById('prediction-form').dispatchEvent(new Event('submit'));
}
