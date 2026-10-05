import os

file_path = 'frontend/interview_room.html'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Fix the broken button HTML
broken_btn = """<button class="btn-end" onclick="endInterview()">
 id="btnEnd"><i data-lucide="square" style="width:14px;height:14px;"></i> End Interview</button>"""
fixed_btn = """<button class="btn-end" id="btnEnd" onclick="endInterview()"><i data-lucide="square" style="width:14px;height:14px;"></i> End Interview</button>"""
code = code.replace(broken_btn, fixed_btn)

# We also need to inject the JavaScript properly.
# Let's find the </script> tag and inject before it.
js_code = """
  let visionContext = "";
  let interviewDuration = 300; // 5 minutes
  let timerInterval = null;
  let frameInterval = null;

  async function initCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      document.getElementById('interviewCam').srcObject = stream;
      frameInterval = setInterval(captureAndAnalyzeFrame, 20000);
    } catch (err) {
      console.error("Camera access denied:", err);
    }
  }

  function startTimer() {
    const display = document.getElementById('timerDisplay');
    timerInterval = setInterval(() => {
      interviewDuration--;
      let m = Math.floor(interviewDuration / 60);
      let s = interviewDuration % 60;
      display.textContent = (m < 10 ? '0'+m : m) + ':' + (s < 10 ? '0'+s : s);
      if (interviewDuration <= 0) {
        clearInterval(timerInterval);
        endInterview();
      }
    }, 1000);
  }

  async function captureAndAnalyzeFrame() {
    const video = document.getElementById('interviewCam');
    const canvas = document.getElementById('captureCanvas');
    if (!video.videoWidth) return;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.5);
    
    try {
      const res = await fetch('/api/interviews/session/analyze_frame', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: dataUrl })
      });
      const data = await res.json();
      if (data.success) {
        visionContext = data.observation;
      }
    } catch (e) {}
  }

  async function endInterview() {
    clearInterval(timerInterval);
    clearInterval(frameInterval);
    document.getElementById('chatInput').disabled = true;
    document.getElementById('btnSend').disabled = true;
    
    const video = document.getElementById('interviewCam');
    if (video.srcObject) {
      video.srcObject.getTracks().forEach(track => track.stop());
    }

    document.getElementById('reviewModal').style.display = 'flex';
    document.getElementById('reviewContent').innerHTML = "Generating comprehensive feedback on your technical skills, body language, and expressions... Please wait.";

    try {
      const res = await fetch('/api/interviews/session/end', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: chatMessages })
      });
      const data = await res.json();
      if (data.success) {
        let html = data.review.replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>').replace(/\\n/g, '<br>');
        document.getElementById('reviewContent').innerHTML = html;
      } else {
        document.getElementById('reviewContent').innerHTML = "Failed to generate review. " + data.error;
      }
    } catch (e) {
      document.getElementById('reviewContent').innerHTML = "Error generating review.";
    }
  }

  window.addEventListener('load', () => {
    initCamera();
    startTimer();
  });
"""

# Replace the payload in sendMessage
old_fetch = """        body: JSON.stringify({
          topic: topic,
          messages: chatMessages,
          code: '' // No code in pure chat
        })"""
new_fetch = """        body: JSON.stringify({
          topic: topic,
          messages: chatMessages,
          code: '',
          vision_context: visionContext
        })"""
code = code.replace(old_fetch, new_fetch)

# Also remove the old broken end button event listener if it exists
old_btn_listener = """  /* â”€â”€ End Interview â”€â”€ */
  document.getElementById('btnEnd').addEventListener('click', () => {
    document.getElementById('endModal').classList.add('open');
  });"""
code = code.replace(old_btn_listener, "")

# Insert the js_code just before the end of the script
script_end_tag = "</script>"
if "async function initCamera" not in code:
    code = code.replace(script_end_tag, js_code + "\n" + script_end_tag)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Frontend completely fixed!")
