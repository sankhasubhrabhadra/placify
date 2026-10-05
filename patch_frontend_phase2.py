import os
import glob
import re

html_files = glob.glob(os.path.join('frontend', '*.html'))

sidebar_link = '        <a href="simulator.html" class="nav-item">\n          <i data-lucide="sparkles"></i>\n          <span>Skill Simulator</span>\n        </a>'

# 1. Add nav link to all pages
for html_file in html_files:
    if html_file.endswith('login.html') or html_file.endswith('signup.html'):
        continue
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has simulator
    if 'href="simulator.html"' not in content:
        # Find where jobs.html is in the nav, append after it
        jobs_nav = re.search(r'<a href="jobs\.html".*?</a>', content, re.DOTALL)
        if jobs_nav:
            content = content[:jobs_nav.end()] + '\n' + sidebar_link + content[jobs_nav.end():]
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)

# 2. Update jobs.html to add simulator button
jobs_path = os.path.join('frontend', 'jobs.html')
with open(jobs_path, 'r', encoding='utf-8') as f:
    jobs_content = f.read()

# I need to add the button in the `renderResults` function defined at the bottom of jobs.html
old_render = """            <div>
              <h5 class="mb-2" style="font-weight: 600;">Notes</h5>
              <ul class="text-secondary" style="margin-left: 1.25rem;">
                ${result.explanation.reasons.map(reason => `<li style="margin-bottom:0.25rem;">${reason}</li>`).join('')}
              </ul>
            </div>
          </div>
        `;"""

new_render = """            <div>
              <h5 class="mb-2" style="font-weight: 600;">Notes</h5>
              <ul class="text-secondary" style="margin-left: 1.25rem;">
                ${result.explanation.reasons.map(reason => `<li style="margin-bottom:0.25rem;">${reason}</li>`).join('')}
              </ul>
            </div>
            
            <div style="margin-top: 1.5rem; text-align: right;">
              <a href="simulator.html?candidate_id=${result.candidate_id}" class="btn btn-primary" style="display: inline-flex; align-items: center; text-decoration: none;">
                <i data-lucide="sparkles" style="width: 18px; height: 18px; margin-right: 0.5rem;"></i>
                See what skills would improve your match
              </a>
            </div>
          </div>
        `;"""

if "See what skills would improve your match" not in jobs_content:
    jobs_content = jobs_content.replace(old_render, new_render)
    with open(jobs_path, 'w', encoding='utf-8') as f:
        f.write(jobs_content)

# 3. Update simulator.html to read candidate_id from URL
sim_path = os.path.join('frontend', 'simulator.html')
with open(sim_path, 'r', encoding='utf-8') as f:
    sim_content = f.read()

old_candidate_id = "    let candidateId = 1;"
new_candidate_id = "    const urlParams = new URLSearchParams(window.location.search);\n    let candidateId = urlParams.get('candidate_id') || 1;"

if new_candidate_id not in sim_content:
    sim_content = sim_content.replace(old_candidate_id, new_candidate_id)
    with open(sim_path, 'w', encoding='utf-8') as f:
        f.write(sim_content)

print("Frontend patched!")
