import re

with open('frontend/market.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove maintainAspectRatio: false which collapses the doughnut chart
html = html.replace('options: { responsive: true, maintainAspectRatio: false }', 'options: { responsive: true }')

with open('frontend/market.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Fixed doughnut chart layout")
