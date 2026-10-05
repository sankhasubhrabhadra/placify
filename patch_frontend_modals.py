import os

file_path = 'frontend/interviews.html'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Add Modals to interviews.html
modals = """
  <!-- Schedule Interview Modal -->
  <div id="scheduleModal" class="modal-overlay">
    <div class="modal-content" style="text-align: left;">
      <h2 style="color:var(--txt); margin-bottom: 20px;">Schedule Interview</h2>
      <div style="margin-bottom: 16px;">
        <label style="display:block; margin-bottom: 8px; color:var(--txt2);">Select Topic</label>
        <select id="scheduleTopic" class="chat-input" style="width:100%; border-radius: 8px; background:var(--bg);">
          <option>System Design</option>
          <option>Data Structures & Algorithms</option>
          <option>Frontend Architecture</option>
          <option>Behavioral</option>
        </select>
      </div>
      <div style="display:flex; justify-content:flex-end; gap:12px;">
        <button class="btn btn-outline" onclick="closeScheduleModal()">Cancel</button>
        <button class="btn btn-primary" onclick="submitSchedule()">Schedule</button>
      </div>
    </div>
  </div>

  <!-- Feedback Modal -->
  <div id="feedbackModal" class="modal-overlay">
    <div class="modal-content" style="text-align: left; max-width: 700px; max-height: 80vh; display:flex; flex-direction:column;">
      <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 16px;">
        <h2 style="color:var(--txt); margin:0;">Interview Feedback</h2>
        <button onclick="closeFeedbackModal()" style="background:none; border:none; color:var(--txt2); cursor:pointer;"><i data-lucide="x"></i></button>
      </div>
      <div id="feedbackContent" style="overflow-y:auto; line-height:1.6; color:var(--txt2); white-space:pre-wrap;">
        Loading...
      </div>
    </div>
  </div>
"""
if "scheduleModal" not in code:
    code = code.replace('</body>', modals + '\n</body>')

# Change Schedule Interview button
old_schedule_btn = '<button class="btn btn-primary">Schedule Interview</button>'
new_schedule_btn = '<button class="btn btn-primary" onclick="openScheduleModal()">Schedule Interview</button>'
code = code.replace(old_schedule_btn, new_schedule_btn)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

file_path = 'frontend/script.js'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Fix past container rendering in script.js to add onclick
old_past_html = """              <button class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">View 
Feedback</button>"""
new_past_html = """              <button class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;" onclick="viewFeedback(${p.id})">View Feedback</button>"""
code = code.replace(old_past_html.replace('\n', ''), new_past_html)

# And add the JS functions
js_functions = """
window.openScheduleModal = function() {
  document.getElementById('scheduleModal').classList.add('open');
};
window.closeScheduleModal = function() {
  document.getElementById('scheduleModal').classList.remove('open');
};
window.submitSchedule = async function() {
  const topic = document.getElementById('scheduleTopic').value;
  try {
    const res = await fetch('/api/interviews/schedule', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: topic })
    });
    const data = await res.json();
    if(data.success) {
      window.location.reload();
    }
  } catch(e) { console.error(e); }
};

window.viewFeedback = async function(id) {
  document.getElementById('feedbackModal').classList.add('open');
  document.getElementById('feedbackContent').innerHTML = "Loading feedback...";
  lucide.createIcons();
  
  try {
    const res = await fetch('/api/interviews/' + id + '/feedback');
    const data = await res.json();
    if(data.success && data.feedback) {
      let html = data.feedback.replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>').replace(/\\n/g, '<br>');
      document.getElementById('feedbackContent').innerHTML = html;
    } else {
      document.getElementById('feedbackContent').innerHTML = "No feedback generated for this interview yet.";
    }
  } catch(e) {
    document.getElementById('feedbackContent').innerHTML = "Error loading feedback.";
  }
};
window.closeFeedbackModal = function() {
  document.getElementById('feedbackModal').classList.remove('open');
};
"""
if "openScheduleModal" not in code:
    code = code + "\n" + js_functions

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("interviews.html and script.js patched!")
