// Initialize Lucide Icons
lucide.createIcons();

// Setup Chart.js Activity Graph
async function initDashboard() {
  const statsRow = document.getElementById('stats-row');
  const activityChartEl = document.getElementById('activityChart');
  const progressContainer = document.getElementById('progress-container');
  const topSkillsContainer = document.getElementById('top-skills-container');
  const timelineContainer = document.getElementById('timeline-container');

  if (statsRow) {
    try {
      const res = await fetch('/api/dashboard/stats');
      const data = await res.json();
      if (data.success) {
        statsRow.innerHTML = `
          <div class="card stat-card">
            <div class="stat-header">
              <span class="stat-title">Problems Solved</span>
              <i data-lucide="check-circle-2" class="text-secondary"></i>
            </div>
            <div class="stat-value">${data.stats.problems_solved}</div>
            <div class="stat-trend trend-up">
              <i data-lucide="trending-up"></i>
              <span>${data.stats.solved_trend}% from last week</span>
            </div>
          </div>
          <div class="card stat-card">
            <div class="stat-header">
              <span class="stat-title">Current Streak</span>
              <i data-lucide="flame" class="text-secondary"></i>
            </div>
            <div class="stat-value">${data.stats.streak} Days</div>
            <div class="stat-trend trend-up">
              <i data-lucide="trending-up"></i>
              <span>Keep it up!</span>
            </div>
          </div>
          <div class="card stat-card">
            <div class="stat-header">
              <span class="stat-title">Global Rank</span>
              <i data-lucide="globe" class="text-secondary"></i>
            </div>
            <div class="stat-value">#${data.stats.global_rank.toLocaleString()}</div>
            <div class="stat-trend trend-up">
              <i data-lucide="trending-up"></i>
              <span>Top 5%</span>
            </div>
          </div>
          <div class="card stat-card">
            <div class="stat-header">
              <span class="stat-title">Mock Interviews</span>
              <i data-lucide="message-square" class="text-secondary"></i>
            </div>
            <div class="stat-value">${data.stats.mock_interviews}</div>
            <div class="stat-trend trend-down">
              <i data-lucide="trending-down"></i>
              <span>Schedule next</span>
            </div>
          </div>
        `;
        lucide.createIcons();
      }
    } catch (e) {
      console.error(e);
    }
  }

  if (activityChartEl) {
    try {
      const res = await fetch('/api/dashboard/chart');
      const data = await res.json();
      if (data.success) {
        const ctx = activityChartEl.getContext('2d');
        const rootStyles = getComputedStyle(document.documentElement);
        const primaryAccent = rootStyles.getPropertyValue('--primary-accent').trim();
        const textSecondary = rootStyles.getPropertyValue('--text-secondary').trim();
        const borderColor = rootStyles.getPropertyValue('--border-color').trim();
        const cardBg = rootStyles.getPropertyValue('--card-bg').trim();
        const textPrimary = rootStyles.getPropertyValue('--text-primary').trim();

        new Chart(ctx, {
          type: 'line',
          data: {
            labels: data.labels,
            datasets: [{
              label: 'Problems Solved',
              data: data.data,
              borderColor: primaryAccent,
              backgroundColor: primaryAccent,
              borderWidth: 3,
              pointRadius: 4,
              pointBackgroundColor: primaryAccent,
              pointBorderColor: 'transparent',
              fill: false,
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                backgroundColor: cardBg,
                titleColor: textPrimary,
                bodyColor: textPrimary,
                borderColor: borderColor,
                borderWidth: 1,
                displayColors: false,
              }
            },
            scales: {
              x: { grid: { display: false, drawBorder: false }, ticks: { color: textSecondary, font: { size: 12 } } },
              y: { grid: { color: borderColor, drawBorder: false, borderDash: [3, 3] }, ticks: { color: textSecondary, font: { size: 12 }, stepSize: 5 } }
            }
          }
        });
      }
    } catch (e) {
      console.error(e);
    }
  }

  if (progressContainer && topSkillsContainer) {
    try {
      const res = await fetch('/api/dashboard/progress');
      const data = await res.json();
      if (data.success) {
        progressContainer.innerHTML = data.progress.map(p => `
          <div class="progress-wrapper mb-3">
            <div class="progress-header">
              <span>${p.title}</span>
              <span class="text-${p.color}">${p.completed} / ${p.total}</span>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar-fill" style="width: ${(p.completed/p.total)*100}%; background-color: ${p.color_hex}"></div>
            </div>
          </div>
        `).join('');

        const skillIcons = { 'React': 'code', 'TypeScript': 'terminal', 'Node.js': 'terminal', 'PostgreSQL': 'database', 'AWS': 'cloud', 'System Design': 'code' };
        topSkillsContainer.innerHTML = data.top_skills.map(s => `
          <span class="badge"><i data-lucide="${skillIcons[s] || 'code'}" class="text-primary badge-icon"></i> ${s}</span>
        `).join('');
        lucide.createIcons();
      }
    } catch(e) { console.error(e); }
  }

  if (timelineContainer) {
    try {
      const res = await fetch('/api/dashboard/activity');
      const data = await res.json();
      if (data.success) {
        timelineContainer.innerHTML = data.activities.map(a => `
          <div class="timeline-item">
            <div class="timeline-icon text-${a.color} border-${a.color}">
              <i data-lucide="${a.icon}"></i>
            </div>
            <div class="timeline-content">
              <span class="timeline-title">${a.title}</span>
              <span class="timeline-date">${a.time}</span>
            </div>
          </div>
        `).join('');
        lucide.createIcons();
      }
    } catch(e) { console.error(e); }
  }
}
initDashboard();

// Interviews Page
async function initInterviews() {
  const upcomingContainer = document.getElementById('upcoming-container');
  const pastContainer = document.getElementById('past-container');
  
  if (upcomingContainer && pastContainer) {
    try {
      const res = await fetch('/api/interviews');
      const data = await res.json();
      if (data.success) {
        upcomingContainer.innerHTML = data.upcoming.map(u => `
          <div class="card" style="background-color: var(--surface-color); border-color: var(--primary-accent);">
            <div class="flex justify-between items-center mb-2">
              <span class="font-medium">${u.topic}</span>
              <span class="tag tag-medium text-primary" style="background-color: rgba(255,161,22,0.1);">${u.time_until}</span>
            </div>
            <div class="flex items-center gap-2 text-secondary" style="font-size: 0.875rem;">
              <i data-lucide="clock" size="14"></i>
              <span>${u.date}</span>
            </div>
            <div class="flex items-center gap-2 text-secondary mt-2" style="font-size: 0.875rem;">
              <i data-lucide="user" size="14"></i>
              <span>Interviewer: ${u.interviewer}</span>
            </div>
            <div class="mt-4 flex gap-2">
              <a href="interview_room.html?topic=${encodeURIComponent(u.topic)}" class="btn btn-primary" style="flex: 1; text-align: center; text-decoration: none;">Join Room</a>
              <button class="btn btn-outline" style="flex: 1;">Reschedule</button>
            </div>
          </div>
        `).join('');

        pastContainer.innerHTML = data.past.map(p => `
          <div class="flex justify-between items-center pb-3 border-b">
            <div class="flex-col gap-1">
              <span class="font-medium">${p.topic}</span>
              <span class="text-secondary" style="font-size: 0.75rem;">${p.date} • Rating: ${p.rating}</span>
            </div>
            <button class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">View Feedback</button>
          </div>
        `).join('');
        lucide.createIcons();
      }
    } catch(e) { console.error(e); }
  }
}
initInterviews();

// Learning Paths Page
async function initLearningPaths() {
  const pathsContainer = document.getElementById('paths-container');
  if (pathsContainer) {
    try {
      const res = await fetch('/api/learning/paths');
      const data = await res.json();
      if (data.success) {
        pathsContainer.innerHTML = data.paths.map(p => `
          <div class="card flex-col gap-4">
            <div class="flex justify-between items-start">
              <div class="company-logo" style="background-color: ${p.bg_color};">
                <i data-lucide="${p.icon}" class="text-${p.color}"></i>
              </div>
              <span class="tag ${p.tag_class}">${p.level}</span>
            </div>
            <div>
              <h3 class="stat-title" style="font-size: 1.125rem; color: var(--text-primary); font-weight: 600;">${p.title}</h3>
              <p class="mt-2" style="font-size: 0.875rem;">${p.description}</p>
            </div>
            <div class="progress-wrapper mt-auto pt-4">
              <div class="progress-header">
                <span>${p.total > 0 ? Math.round((p.completed/p.total)*100) : 0}% Completed</span>
                <span class="text-${p.color}">${p.completed} / ${p.total}</span>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar-fill" style="width: ${p.total > 0 ? (p.completed/p.total)*100 : 0}%; background-color: var(--${p.color}-color, var(--primary-accent))"></div>
              </div>
            </div>
            <button class="btn ${p.completed === 0 ? 'btn-primary' : 'btn-outline'} btn-block mt-2">${p.completed === 0 ? 'Start Course' : 'Continue Learning'}</button>
          </div>
        `).join('');
        lucide.createIcons();
      }
    } catch(e) { console.error(e); }
  }
}
initLearningPaths();

// Chat Logic
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const chatMessages = document.getElementById('chatMessages');

async function sendMessage() {
  const text = chatInput.value.trim();
  if (text !== '') {
    const userBubble = document.createElement('div');
    userBubble.className = 'chat-bubble send';
    userBubble.innerHTML = `<p>${text}</p>`;
    chatMessages.appendChild(userBubble);
    chatInput.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      if (data.success) {
        const aiBubble = document.createElement('div');
        aiBubble.className = 'chat-bubble receive';
        aiBubble.innerHTML = `<p>${data.response}</p>`;
        chatMessages.appendChild(aiBubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }
    } catch(e) { console.error(e); }
  }
}

if (chatSendBtn) { chatSendBtn.addEventListener('click', sendMessage); }
if (chatInput) {
  chatInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') sendMessage();
  });
}

// Settings Page
async function initSettings() {
  const profileForm = document.getElementById('profile-form');
  const preferencesForm = document.getElementById('preferences-form');

  if (profileForm && preferencesForm) {
    try {
      const res = await fetch('/api/user/profile');
      const data = await res.json();
      if (data.success) {
        document.getElementById('profile-name').value = data.profile.name;
        document.getElementById('profile-email').value = data.profile.email;
        document.getElementById('profile-title').value = data.profile.title;
        
        document.getElementById('pref-email').checked = data.preferences.email_notifications;
        document.getElementById('pref-public').checked = data.preferences.public_profile;
      }
    } catch(e) { console.error(e); }

    profileForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        const res = await fetch('/api/user/profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: document.getElementById('profile-name').value,
            email: document.getElementById('profile-email').value,
            title: document.getElementById('profile-title').value
          })
        });
        const data = await res.json();
        if (data.success) alert(data.message);
      } catch(e) { console.error(e); }
    });
  }
}
initSettings();

// Login Page
async function initLogin() {
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value;
      const password = document.getElementById('login-password').value;
      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (data.success) {
          localStorage.setItem('token', data.token);
          window.location.href = 'index.html';
        } else {
          alert(data.error || 'Login failed');
        }
      } catch(e) { console.error(e); }
    });
  }
}
initLogin();

// Resume scanner using Flask API
(function () {
  const fileInput = document.getElementById('resumeFile');
  const parseBtn = document.getElementById('parseBtn');
  const pasteArea = document.getElementById('resumeText');
  const resultsEl = document.getElementById('scanResults');

  if (!resultsEl || !parseBtn) return; // page doesn't have scanner

  function renderResults(result) {
    resultsEl.innerHTML = '';
    const wrap = document.createElement('div');
    wrap.className = 'card';
    wrap.style.padding = '1rem';

    const title = document.createElement('h4');
    title.textContent = 'Scan Results';
    wrap.appendChild(title);

    const list = document.createElement('div');
    list.innerHTML = `
      <p><strong>Skills:</strong> ${result.skills.length ? result.skills.join(', ') : 'None detected'}</p>
      <p><strong>Experience:</strong> ${result.experience} years</p>
      <p><strong>Projects:</strong> ${result.projects}</p>
      <p><strong>Score:</strong> ${result.score}/100</p>
      <div style="margin-top:1rem;">
        <h5>Decision: ${result.explanation.decision}</h5>
        <ul style="margin-top:0.5rem;">
          ${result.explanation.reasons.map(reason => `<li>${reason}</li>`).join('')}
        </ul>
      </div>
    `;
    wrap.appendChild(list);
    resultsEl.appendChild(wrap);
  }

  function escapeHtml(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  parseBtn.addEventListener('click', async () => {
    resultsEl.innerHTML = '<div class="card">Scanning...</div>';
    
    const formData = new FormData();
    const file = fileInput && fileInput.files && fileInput.files[0];
    if (file) {
      formData.append('resume', file);
    } else if (pasteArea && pasteArea.value.trim()) {
      formData.append('text', pasteArea.value);
    }

    if (!file && (!pasteArea || !pasteArea.value.trim())) {
      resultsEl.innerHTML = '<div class="card">No resume provided. Upload a PDF or paste text.</div>';
      return;
    }

    try {
      const response = await fetch('/api/resume/scan', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      
      if (data.success) {
        renderResults(data);
      } else {
        resultsEl.innerHTML = `<div class="card" style="color: var(--error-color);">Error: ${data.error || 'Unknown error'}</div>`;
      }
    } catch (err) {
      console.error('Scan failed', err);
      resultsEl.innerHTML = `<div class="card" style="color: var(--error-color);">Failed to connect to server. Make sure the backend is running on port 5000.</div>`;
    }
  });
})();

// Automatically call the correct init function based on the current page
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  
  if (path.includes('index.html') || path === '/' || path === '') {
    if (typeof initDashboard === 'function') initDashboard();
  } else if (path.includes('interviews.html')) {
    if (typeof initInterviews === 'function') initInterviews();
  } else if (path.includes('learning.html')) {
    if (typeof initLearningPaths === 'function') initLearningPaths();
  } else if (path.includes('settings.html')) {
    if (typeof initSettings === 'function') initSettings();
  } else if (path.includes('login.html')) {
    if (typeof initLogin === 'function') initLogin();
  }
});
