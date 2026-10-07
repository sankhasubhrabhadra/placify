import re

with open('scripts/prepare_data.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace .to_dict(orient='records') with .replace({np.nan: None}).to_dict(orient='records')
code = code.replace(
    ".dropna(subset=['job_desig']).to_dict(orient='records')", 
    ".dropna(subset=['job_desig']).replace({np.nan: None}).to_dict(orient='records')"
)

code = code.replace(
    ".dropna(subset=['company_name', 'job_title']).to_dict(orient='records')", 
    ".dropna(subset=['company_name', 'job_title']).replace({np.nan: None}).to_dict(orient='records')"
)

with open('scripts/prepare_data.py', 'w', encoding='utf-8') as f:
    f.write(code)

with open('frontend/market.html', 'r', encoding='utf-8') as f:
    market_html = f.read()

if '<script src="script.js"></script>' not in market_html:
    market_html = market_html.replace('</body>', '  <script src="script.js"></script>\n</body>')
    with open('frontend/market.html', 'w', encoding='utf-8') as f:
        f.write(market_html)

print("Fixed NaN bug in prepare_data.py and added script.js to market.html")
