// Initialize Lucide Icons
lucide.createIcons();

// Setup Chart.js Activity Graph
const ctx = document.getElementById('activityChart').getContext('2d');

// Read computed style variables for Chart.js styling
const rootStyles = getComputedStyle(document.documentElement);
const primaryAccent = rootStyles.getPropertyValue('--primary-accent').trim();
const textSecondary = rootStyles.getPropertyValue('--text-secondary').trim();
const borderColor = rootStyles.getPropertyValue('--border-color').trim();
const cardBg = rootStyles.getPropertyValue('--card-bg').trim();
const textPrimary = rootStyles.getPropertyValue('--text-primary').trim();

const data = {
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  datasets: [{
    label: 'Problems Solved',
    data: [4, 7, 5, 10, 8, 14, 12],
    borderColor: primaryAccent,
    backgroundColor: primaryAccent,
    borderWidth: 3,
    pointRadius: 4,
    pointBackgroundColor: primaryAccent,
    pointBorderColor: 'transparent',
    fill: false,
    tension: 0.4 // curve
  }]
};

const config = {
  type: 'line',
  data: data,
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
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
      x: {
        grid: {
          display: false,
          drawBorder: false
        },
        ticks: {
          color: textSecondary,
          font: {
            size: 12
          }
        }
      },
      y: {
        grid: {
          color: borderColor,
          drawBorder: false,
          borderDash: [3, 3]
        },
        ticks: {
          color: textSecondary,
          font: {
            size: 12
          },
          stepSize: 5
        }
      }
    }
  }
};

new Chart(ctx, config);

// Simple Chat Logic
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const chatMessages = document.getElementById('chatMessages');

function sendMessage() {
  const text = chatInput.value.trim();
  if (text !== '') {
    // Append User Message
    const userBubble = document.createElement('div');
    userBubble.className = 'chat-bubble send';
    userBubble.innerHTML = `<p>${text}</p>`;
    chatMessages.appendChild(userBubble);
    chatInput.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Simulate AI Response
    setTimeout(() => {
      const aiBubble = document.createElement('div');
      aiBubble.className = 'chat-bubble receive';
      aiBubble.innerHTML = `<p>I can certainly help you with that! Let's break it down.</p>`;
      chatMessages.appendChild(aiBubble);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 1000);
  }
}

chatSendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', function (e) {
  if (e.key === 'Enter') {
    sendMessage();
  }
});

// Resume scanner: basic PDF/text extraction and parsing
(function () {
  const fileInput = document.getElementById('resumeFile');
  const parseBtn = document.getElementById('parseBtn');
  const pasteArea = document.getElementById('resumeText');
  const resultsEl = document.getElementById('scanResults');

  if (!resultsEl || !parseBtn) return; // page doesn't have scanner

  async function loadPdfJs() {
    if (window.pdfjsLib) return window.pdfjsLib;
    return new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.14.305/pdf.min.js';
      s.onload = () => resolve(window.pdfjsLib);
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  function readFileAsArrayBuffer(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsArrayBuffer(file);
    });
  }

  function readFileAsText(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsText(file);
    });
  }

  async function extractTextFromPDF(file) {
    try {
      await loadPdfJs();
      const arrayBuffer = await readFileAsArrayBuffer(file);
      const loadingTask = window.pdfjsLib.getDocument({ data: arrayBuffer });
      const pdf = await loadingTask.promise;
      let fullText = '';
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const content = await page.getTextContent();
        const strings = content.items.map(item => item.str);
        fullText += strings.join(' ') + '\n';
      }
      return fullText;
    } catch (err) {
      console.error('PDF extraction failed', err);
      return '';
    }
  }

  function parseResumeText(text) {
    const lines = text.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
    const joined = text.replace(/\n/g, ' ');

    // Email
    const emailMatch = joined.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i);
    const email = emailMatch ? emailMatch[0] : null;

    // Phone (basic)
    const phoneMatch = joined.match(/(?:\+?\d{1,3}[\s-\.]*)?(?:\(\d{3}\)|\d{3})[\s-\.]?\d{3}[\s-\.]?\d{4}/);
    const phone = phoneMatch ? phoneMatch[0] : null;

    // Name heuristic: first line with 2 words and capitalized starts
    let name = null;
    for (const l of lines.slice(0, 5)) {
      const words = l.split(/\s+/);
      if (words.length >= 2 && words.length <= 4) {
        const caps = words.filter(w => /^[A-Z][a-z]/.test(w));
        if (caps.length >= 2) { name = l; break; }
      }
    }

    // Skills: check for common keywords
    const skillKeywords = ['JavaScript','TypeScript','React','Node','Python','Java','C++','C#','SQL','AWS','Docker','Kubernetes','HTML','CSS','GraphQL','Spring','Django','Flask'];
    const foundSkills = [];
    for (const kw of skillKeywords) {
      const re = new RegExp('\\b' + kw.replace(/[.*+?^${}()|[\]\\]/g,'\\$&') + '\\b','i');
      if (re.test(joined) && !foundSkills.includes(kw)) foundSkills.push(kw);
    }

    return { name, email, phone, skills: foundSkills, excerpt: lines.slice(0,10).join('\n') };
  }

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
      <p><strong>Name:</strong> ${result.name || 'Not found'}</p>
      <p><strong>Email:</strong> ${result.email || 'Not found'}</p>
      <p><strong>Phone:</strong> ${result.phone || 'Not found'}</p>
      <p><strong>Skills:</strong> ${result.skills.length ? result.skills.join(', ') : 'None detected'}</p>
      <details style="margin-top:0.5rem;"><summary>Resume excerpt</summary><pre style="white-space:pre-wrap;">${escapeHtml(result.excerpt)}</pre></details>
    `;
    wrap.appendChild(list);
    resultsEl.appendChild(wrap);
  }

  function escapeHtml(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  parseBtn.addEventListener('click', async () => {
    resultsEl.innerHTML = '<div class="card">Scanning...</div>';
    let text = '';
    const file = fileInput && fileInput.files && fileInput.files[0];
    if (file) {
      const type = file.type || '';
      if (type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
        text = await extractTextFromPDF(file);
      } else {
        text = await readFileAsText(file);
      }
    }
    if (!text && pasteArea && pasteArea.value.trim()) {
      text = pasteArea.value;
    }

    if (!text) {
      resultsEl.innerHTML = '<div class="card">No resume provided. Upload a PDF or paste text.</div>';
      return;
    }

    const parsed = parseResumeText(text);
    renderResults(parsed);
  });
})();
