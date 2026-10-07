import re

with open('frontend/market.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace chart.js script tag
html = html.replace(
    '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>',
    '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>'
)

with open('frontend/market.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Fixed Chart.js CDN link")
