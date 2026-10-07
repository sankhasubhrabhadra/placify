import re

with open('frontend/interviews.html', 'r', encoding='utf-8') as f:
    html = f.read()

behavioural_panel = """
        <div class="card mt-4" id="behavioural-panel" style="border: 2px solid var(--primary-accent);">
          <h3 class="card-title mb-4">Behavioural Readiness (Big Five)</h3>
          <p class="text-secondary mb-4">Self-assessment to gauge behavioral alignment with senior, client-facing data scientists (based on 2024-25 sample data). This is for self-development, not a hiring screen.</p>
          
          <div id="bigFiveQuestions" class="flex flex-col gap-4 mb-4">
            <!-- Rendered by JS -->
          </div>
          
          <button class="btn btn-primary" onclick="calculateBigFive()">Calculate Readiness</button>
          
          <div id="bigFiveResults" class="mt-6" style="display: none;">
            <div class="flex flex-col gap-2">
                <div style="font-size:1.1rem">Predicted Success Probability:</div>
                <div style="font-size:2.5rem; font-weight:700; color:var(--primary-color);" id="bfProbDisplay">0%</div>
            </div>
            <div id="bfPercentiles" class="mt-4 flex flex-col gap-2"></div>
            <div id="bfTips" class="mt-4 p-4 rounded bg-surface"></div>
          </div>
        </div>

        <script>
            const bfTraits = ['neuroticism', 'extraversion', 'openness', 'agreeableness', 'conscientiousness'];
            const bfQuestions = [
                "I worry about things frequently.",
                "I am the life of the party.",
                "I have a vivid imagination.",
                "I sympathize with others' feelings.",
                "I get chores done right away."
            ];
            
            let sdsModel = null;
            fetch('data/sds_model.json').then(r=>r.json()).then(d => {
                sdsModel = d;
                const qContainer = document.getElementById('bigFiveQuestions');
                bfTraits.forEach((t, i) => {
                    qContainer.innerHTML += `
                        <div class="flex flex-col gap-1">
                            <label class="font-bold">${bfQuestions[i]} <span class="text-secondary font-normal">(${t})</span></label>
                            <input type="range" id="bf_q_${i}" min="1" max="5" value="3" class="w-full">
                        </div>
                    `;
                });
            }).catch(e => console.error("Could not load SDS model", e));

            window.calculateBigFive = function() {
                if (!sdsModel) return;
                let logit = sdsModel.intercept;
                let percentilesHtml = "<h4>Your Percentiles vs Senior DS Sample</h4>";
                let tipsHtml = "<h4>Development Tips</h4><ul>";
                
                bfTraits.forEach((feat, i) => {
                    let rawScore = 17 + ((document.getElementById(`bf_q_${i}`).value - 1) * 12.75);
                    let standardized = (rawScore - sdsModel.means[i]) / sdsModel.stds[i];
                    logit += standardized * sdsModel.coefficients[i];
                    
                    let percArray = sdsModel.percentiles[feat];
                    let perc = 50;
                    if (rawScore < percArray[0]) perc = "<10th";
                    else if (rawScore < percArray[1]) perc = "25th";
                    else if (rawScore < percArray[2]) perc = "50th";
                    else if (rawScore < percArray[3]) perc = "75th";
                    else if (rawScore < percArray[4]) perc = "90th";
                    else perc = ">90th";
                    
                    percentilesHtml += `<div class="flex justify-between border-b pb-1"><span>${feat}</span><span class="font-bold">${perc} Percentile</span></div>`;
                    
                    if (feat === 'openness' && rawScore < sdsModel.means[i]) {
                        tipsHtml += "<li><strong>Openness:</strong> Try exploring new domains or unstructured data problems to build creative problem-solving skills.</li>";
                    }
                    if (feat === 'conscientiousness' && rawScore < sdsModel.means[i]) {
                        tipsHtml += "<li><strong>Conscientiousness:</strong> Focus on rigorous documentation, reproducibility, and structured project management in your work.</li>";
                    }
                });
                
                let prob = 1 / (1 + Math.exp(-logit));
                document.getElementById('bfProbDisplay').innerText = (prob * 100).toFixed(1) + '%';
                document.getElementById('bfPercentiles').innerHTML = percentilesHtml;
                
                tipsHtml += "</ul>";
                document.getElementById('bfTips').innerHTML = tipsHtml;
                
                document.getElementById('bigFiveResults').style.display = 'block';
            }
        </script>
"""

html = re.sub(r'(</main>)', behavioural_panel + r'\n\1', html)

with open('frontend/interviews.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated interviews.html")
