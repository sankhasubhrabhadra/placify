import re

with open('frontend/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the y axis config to include min: 0 and suggestedMax: 5
js = js.replace(
    'y: { grid: { color: borderColor, drawBorder: false, borderDash: [3, 3] }, ticks: { color: textSecondary, font: { size: 12 }, stepSize: 5 } }',
    'y: { min: 0, suggestedMax: 5, grid: { color: borderColor, drawBorder: false, borderDash: [3, 3] }, ticks: { color: textSecondary, font: { size: 12 }, stepSize: 1 } }'
)

with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Fixed Activity Chart y-axis")
