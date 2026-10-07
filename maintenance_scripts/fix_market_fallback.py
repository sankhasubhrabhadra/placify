import re

with open('frontend/market.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the json() parsing with text() parsing that replaces NaN
html = html.replace(
    'const companies = await compRes.json();',
    'const compText = await compRes.text(); const companies = JSON.parse(compText.replace(/NaN/g, "null"));'
)
html = html.replace(
    'const locations = await locRes.json();',
    'const locText = await locRes.text(); const locations = JSON.parse(locText.replace(/NaN/g, "null"));'
)
html = html.replace(
    'allRoles = await rolesRes.json();',
    'const rolesText = await rolesRes.text(); allRoles = JSON.parse(rolesText.replace(/NaN/g, "null"));'
)

# Also ensure avg_salary is cast to a number before calling .toFixed in case it is a string
html = html.replace(
    "${r.avg_salary ? r.avg_salary.toFixed(1) + 'L' : 'Undisclosed'}",
    "${r.avg_salary ? Number(r.avg_salary).toFixed(1) + 'L' : 'Undisclosed'}"
)

with open('frontend/market.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Added NaN fallback to market.html")
