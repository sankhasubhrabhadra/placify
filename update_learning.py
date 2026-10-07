import re

with open('frontend/learning.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_logic = """
    async function loadRoadmaps() {
      try {
        const [rRes, mRes, jRes] = await Promise.all([
          fetch(API_BASE + '/api/learning/roadmaps'),
          fetch('data/skill_demand.json').catch(()=>({})),
          fetch('data/jds_model.json').catch(()=>({}))
        ]);
        const data = await rRes.json();
        
        let marketData = {};
        let jdsData = {features: [], coefficients: []};
        try { marketData = await mRes.json(); } catch(e) {}
        try { jdsData = await jRes.json(); } catch(e) {}
        
        if (data.success) {
          // Re-order roadmaps based on demand + JDS weight
          data.roadmaps.forEach(rm => {
            let demandScore = marketData[rm.title.toLowerCase()] || 0;
            let jdsWeight = 0;
            const jdsIdx = jdsData.features.findIndex(f => rm.title.toLowerCase().includes(f.replace('_',' ')));
            if (jdsIdx >= 0) jdsWeight = jdsData.coefficients[jdsIdx];
            
            rm.combinedScore = (demandScore * 0.01) + (jdsWeight * 10);
            rm.reason = `High demand (${demandScore} postings) + ${jdsWeight ? 'strong link to salary hikes' : 'essential skill'}`;
          });
          
          data.roadmaps.sort((a,b) => b.combinedScore - a.combinedScore);
          allRoadmaps = data.roadmaps;
          renderSelector();
          if (allRoadmaps.length) selectRoadmap(allRoadmaps[0].id);
        }
      } catch(e) { console.error(e); }
    }
"""

html = re.sub(r"async function loadRoadmaps\(\) \{.*?(?=function renderSelector)", new_logic, html, flags=re.DOTALL)

with open('frontend/learning.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated learning.html")
