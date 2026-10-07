import re

with open('frontend/jobs.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Resume Scanner - Placify</title>
  <link rel="stylesheet" href="style.css" />
  <link rel="stylesheet" href="style-additions.css" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/lucide@latest"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
  <style>
    .results-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1.5rem; }
    .skill-badge { padding: 4px 8px; border-radius: 4px; font-size: 0.85rem; display: inline-block; margin: 2px; }
    .skill-match { background: var(--success-color); color: white; }
    .skill-miss { background: var(--warning-color); color: white; }
  </style>
</head>
<body>
  <div class="layout-wrapper">
    <aside class="sidebar">
      <div class="sidebar-header"><i data-lucide="code-2" class="text-primary mr-2"></i>Placify</div>
      <nav class="sidebar-nav">
        <a href="index.html" class="nav-item"><i data-lucide="layout-dashboard"></i><span>Dashboard</span></a>
        <a href="placement_session.html" class="nav-item"><i data-lucide="briefcase"></i><span>Final Placement Prep</span></a>
        <a href="jobs.html" class="nav-item active"><i data-lucide="file-search"></i><span>Resume Scanner</span></a>
        <a href="learning.html" class="nav-item"><i data-lucide="book-open"></i><span>Learning Paths</span></a>
        <a href="interviews.html" class="nav-item"><i data-lucide="users"></i><span>Mock Interviews</span></a>
        <a href="simulator.html" class="nav-item"><i data-lucide="trending-up"></i><span>Skill Simulator</span></a>
        <a href="market.html" class="nav-item"><i data-lucide="bar-chart"></i><span>Job Market</span></a>
      </nav>
    </aside>

    <div class="main-content">
      <main class="content-area">
        <h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem;">Market-Driven Resume Scanner</h2>
        <p class="text-secondary" style="margin-bottom: 1.5rem;">Matches your resume against 17,000+ real job postings (2024-25).</p>

        <div class="card">
            <div class="mb-4">
                <label class="block mb-2 font-bold">Target Role Family</label>
                <select id="targetRole" class="input" style="width: 100%; max-width: 300px;">
                    <option value="data scientist">Data Scientist</option>
                    <option value="data analyst">Data Analyst</option>
                    <option value="business analyst">Business Analyst</option>
                    <option value="data engineer">Data Engineer</option>
                    <option value="machine learning">Machine Learning Engineer</option>
                </select>
            </div>
            
            <div class="mb-4">
                <label class="block mb-2 font-bold">Upload Resume (PDF)</label>
                <input type="file" id="resumeFile" accept=".pdf" class="input" style="width: 100%; max-width: 300px;">
            </div>
            
            <div class="mb-4">
                <label class="block mb-2 font-bold">Or Paste Text</label>
                <textarea id="resumeText" class="input" rows="5" style="width: 100%;"></textarea>
            </div>
            
            <button class="btn btn-primary" onclick="scanResume()" id="scanBtn">Scan Resume</button>
            <div id="scanStatus" class="mt-2 text-secondary"></div>
        </div>

        <div id="resultsArea" style="display: none;">
            <div class="results-grid">
                <div class="card" style="border: 2px solid var(--primary-color);">
                    <h3>Fit Score</h3>
                    <div id="fitScore" style="font-size: 3rem; font-weight: 800; color: var(--primary-color);">0%</div>
                    <p class="text-secondary" id="fitSubtitle"></p>
                </div>
                <div class="card">
                    <h3>Market Estimates</h3>
                    <p><strong>Est. Salary:</strong> <span id="estSalary" class="text-success font-bold">--</span></p>
                    <p><strong>Top Cities:</strong> <span id="estCities">--</span></p>
                    <p><strong>Exp. Range:</strong> <span id="estExp">--</span></p>
                </div>
                <div class="card" style="grid-column: 1/-1;">
                    <h3>Skill Analysis</h3>
                    <div class="mb-4">
                        <h4 class="text-success mb-2">Matched In-Demand Skills</h4>
                        <div id="matchedSkills"></div>
                    </div>
                    <div>
                        <h4 class="text-error mb-2">Missing High-Demand Skills</h4>
                        <div id="missingSkills"></div>
                    </div>
                </div>
            </div>
        </div>
      </main>
    </div>
  </div>

  <script>
    lucide.createIcons();
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

    let jobsIndex = [];
    let globalSkills = [];

    async function loadJobs() {
        try {
            const res = await fetch('data/jobs_index.json');
            jobsIndex = await res.json();
            
            const sr = await fetch('data/skill_demand.json');
            globalSkills = Object.keys(await sr.json());
        } catch(e) { console.error("Failed to load jobs index", e); }
    }
    loadJobs();

    async function extractTextFromPDF(file) {
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument({data: arrayBuffer}).promise;
        let text = "";
        for(let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const content = await page.getTextContent();
            text += content.items.map(item => item.str).join(" ") + " ";
        }
        return text;
    }

    async function scanResume() {
        const btn = document.getElementById('scanBtn');
        const status = document.getElementById('scanStatus');
        btn.disabled = true;
        status.innerText = "Scanning...";
        
        try {
            let text = document.getElementById('resumeText').value;
            const fileInput = document.getElementById('resumeFile');
            
            if(fileInput.files.length > 0) {
                text += " " + await extractTextFromPDF(fileInput.files[0]);
            }
            
            text = text.toLowerCase();
            
            if(!text.trim()) {
                status.innerText = "Please provide resume text or PDF.";
                btn.disabled = false;
                return;
            }

            const targetRole = document.getElementById('targetRole').value;
            
            // Extract skills
            const mySkills = globalSkills.filter(s => text.includes(s));
            
            // Filter jobs
            const roleJobs = jobsIndex.filter(j => j.job_desig.toLowerCase().includes(targetRole));
            if(roleJobs.length === 0) {
                status.innerText = "No market data found for this role.";
                btn.disabled = false; return;
            }

            // Calculate match
            let topMatches = [];
            roleJobs.forEach(job => {
                const required = job.skills_list || [];
                if(required.length === 0) return;
                const overlap = required.filter(s => mySkills.includes(s));
                const score = overlap.length / required.length;
                topMatches.push({job, score, required, overlap});
            });
            
            topMatches.sort((a,b) => b.score - a.score);
            const bestMatches = topMatches.slice(0, 50);
            
            if(bestMatches.length === 0) {
                status.innerText = "Could not calculate fit.";
                btn.disabled = false; return;
            }
            
            const avgScore = bestMatches.reduce((sum, m) => sum + m.score, 0) / bestMatches.length;
            
            // Get missing skills
            const allRequired = {};
            bestMatches.forEach(m => {
                m.required.forEach(s => {
                    allRequired[s] = (allRequired[s] || 0) + 1;
                });
            });
            const missing = Object.keys(allRequired).filter(s => !mySkills.includes(s)).sort((a,b) => allRequired[b] - allRequired[a]).slice(0, 10);
            
            // Averages
            const salaries = bestMatches.map(m => m.job.salary_mid).filter(s => s);
            const avgSal = salaries.length ? salaries.reduce((a,b)=>a+b,0)/salaries.length : 0;
            
            // UI
            document.getElementById('resultsArea').style.display = 'block';
            document.getElementById('fitScore').innerText = Math.round(avgScore * 100) + '%';
            document.getElementById('fitSubtitle').innerText = `Against top ${bestMatches.length} ${targetRole} postings`;
            
            document.getElementById('estSalary').innerText = avgSal ? avgSal.toFixed(1) + ' LPA' : 'N/A';
            document.getElementById('estCities').innerText = bestMatches[0].job.locations_list.slice(0,2).join(', ');
            document.getElementById('estExp').innerText = `${bestMatches[0].job.exp_min || 0}-${bestMatches[0].job.exp_max || 2} yrs`;
            
            document.getElementById('matchedSkills').innerHTML = mySkills.map(s => `<span class="skill-badge skill-match">${s}</span>`).join('');
            document.getElementById('missingSkills').innerHTML = missing.map(s => `<span class="skill-badge skill-miss">${s}</span>`).join('');
            
            status.innerText = "";
        } catch(e) {
            console.error(e);
            status.innerText = "Error scanning resume.";
        }
        btn.disabled = false;
    }
  </script>
</body>
</html>"""

with open('frontend/jobs.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Updated jobs.html")
