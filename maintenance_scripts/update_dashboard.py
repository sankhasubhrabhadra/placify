import re

with open('frontend/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

new_logic = """
  // Load real market skills for dashboard
  if (topSkillsContainer) {
    try {
      const sRes = await fetch('data/skill_demand.json');
      const sData = await sRes.json();
      const top10 = Object.keys(sData).slice(0, 10);
      topSkillsContainer.innerHTML = top10.map(s => `<span class="badge"><i data-lucide="code" class="text-primary badge-icon"></i>${s} <span style="opacity:0.6;font-size:0.75rem;margin-left:4px;">(${sData[s]})</span></span>`).join('');
      
      const locRes = await fetch('data/location_demand.json');
      const locData = await locRes.json();
      const topLocs = Object.keys(locData).slice(0, 2).join(', ');
      
      const roleRes = await fetch('data/salary_by_role.json');
      const roleData = await roleRes.json();
      const avgSal = roleData.reduce((acc, curr) => acc + (curr.avg_salary || 0), 0) / roleData.length;
      
      const marketCitiesEl = document.getElementById('marketCities');
      const marketSalaryEl = document.getElementById('marketSalary');
      if (marketCitiesEl) marketCitiesEl.innerText = topLocs;
      if (marketSalaryEl) marketSalaryEl.innerText = avgSal.toFixed(1) + ' LPA';
      
      lucide.createIcons();
    } catch(e) { console.error("Could not load market skills", e); }
  }
"""

js = re.sub(
    r"topSkillsContainer\.innerHTML = data\.top_skills\.map.*?join\(''\);", 
    "// Replaced by real market data logic below", 
    js, flags=re.DOTALL
)

js = re.sub(
    r"(if \(timelineContainer\) \{)", 
    new_logic + r"\n  \1", 
    js
)

with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

market_panel = """
            <div class="card mt-4" style="border: 1px solid var(--primary-accent);">
              <h3 class="card-title mb-3">Market Intelligence</h3>
              <div class="flex flex-col gap-2">
                <div class="flex justify-between items-center pb-2 border-b" style="border-color: var(--border-color);">
                  <span class="text-secondary">Top Hiring Cities</span>
                  <span id="marketCities" class="font-bold text-primary">Loading...</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-secondary">Avg Market Salary</span>
                  <span id="marketSalary" class="font-bold text-success">Loading...</span>
                </div>
              </div>
            </div>
"""
html = re.sub(r'(<div class="badges-container" id="top-skills-container">\s*<!-- Top skills will be populated by JS -->\s*</div>\s*</div>)', r'\1\n' + market_panel, html)
html = re.sub(r'(<div class="badges-container" id="top-skills-container">\s*</div>\s*</div>)', r'\1\n' + market_panel, html)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated script.js and index.html")
