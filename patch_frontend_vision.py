import os

file_path = 'frontend/interview_room.html'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add Camera and Timer UI
# Find the topbar-right to add the timer display
camera_html = """
      <div class="topbar-right">
        <div id="timerDisplay" style="font-weight: 700; color: var(--warning); background: rgba(255, 200, 87, 0.1); padding: 6px 12px; border-radius: var(--radius); font-variant-numeric: tabular-nums;">05:00</div>
        <button class="btn-end" onclick="endInterview()">
"""
code = code.replace('<div class="topbar-right">\n        <button class="btn-end"', camera_html)

# Add Video element floating on the right side of the chat panel
video_html = """
    <div class="panel-chat" style="position:relative;">
      <!-- Camera Widget -->
      <div id="cameraWidget" style="position: absolute; top: 16px; right: 16px; width: 180px; height: 135px; background: #000; border: 2px solid var(--border); border-radius: var(--radius); overflow: hidden; z-index: 10; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
        <video id="interviewCam" autoplay muted playsinline style="width: 100%; height: 100%; object-fit: cover;"></video>
        <canvas id="captureCanvas" style="display:none;"></canvas>
      </div>
"""
code = code.replace('<div class="panel-chat">', video_html)

# Add Modal for the End Review
modal_html = """
  <!-- Review Modal -->
  <div id="reviewModal" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.8); z-index:9999; justify-content:center; align-items:center; padding: 20px;">
    <div style="background:var(--surface); width:100%; max-width:700px; max-height:80vh; border-radius:var(--radius); border:1px solid var(--border); display:flex; flex-direction:column; overflow:hidden;">
      <div style="padding: 20px; border-bottom: 1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h2 style="color:var(--txt); margin:0;">Interview Review</h2>
        <button onclick="window.location.href='interviews.html'" style="background:var(--accent); color:#000; border:none; padding:8px 16px; border-radius:var(--radius); font-weight:600; cursor:pointer;">Return to Dashboard</button>
      </div>
      <div id="reviewContent" style="padding: 20px; overflow-y:auto; line-height:1.6; color:var(--txt2); white-space:pre-wrap;">
        Analyzing interview performance...
      </div>
    </div>
  </div>
"""
if "reviewModal" not in code:
    code = code.replace('</body>', modal_html + '\n</body>')

# 2. Update JavaScript
js_additions = """
    let visionContext = "";
    let interviewDuration = 300; // 5 minutes in seconds
    let timerInterval = null;
    let frameInterval = null;

    async function initCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        document.getElementById('interviewCam').srcObject = stream;
        
        // Capture frame every 20 seconds
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
      const dataUrl = canvas.toDataURL('image/jpeg', 0.5); // compress
      
      try {
        const res = await fetch('/api/interviews/session/analyze_frame', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: dataUrl })
        });
        const data = await res.json();
        if (data.success) {
          visionContext = data.observation;
          console.log("Vision context updated:", visionContext);
        }
      } catch (e) { console.error(e); }
    }

    async function endInterview() {
      clearInterval(timerInterval);
      clearInterval(frameInterval);
      document.getElementById('chatInput').disabled = true;
      document.querySelector('.chat-input button').disabled = true;
      
      // Stop camera
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
          body: JSON.stringify({ messages: chatHistory })
        });
        const data = await res.json();
        if (data.success) {
          // simple markdown to html
          let html = data.review.replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>').replace(/\\n/g, '<br>');
          document.getElementById('reviewContent').innerHTML = html;
        } else {
          document.getElementById('reviewContent').innerHTML = "Failed to generate review. " + data.error;
        }
      } catch (e) {
        document.getElementById('reviewContent').innerHTML = "Error generating review.";
      }
    }

    // Call initCamera and startTimer on load
    window.addEventListener('load', () => {
      initCamera();
      startTimer();
    });
"""

# Inject the payload modification inside sendMessage()
old_fetch = """        body: JSON.stringify({
          topic: currentTopic,
          messages: chatHistory
        })"""
new_fetch = """        body: JSON.stringify({
          topic: currentTopic,
          messages: chatHistory,
          vision_context: visionContext
        })"""
code = code.replace(old_fetch, new_fetch)

# Inject the js_additions before the closing </script>
code = code.replace('</script>\n</body>', js_additions + '\n</script>\n</body>')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Frontend patched for camera and timer.")
