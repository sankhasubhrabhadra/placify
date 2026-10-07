import glob

html_files = glob.glob('frontend/*.html')
nav_item_market = '<a href="market.html" class="nav-item"><i data-lucide="bar-chart"></i><span>Job Market</span></a>\n      </nav>'

for file_path in html_files:
    # Skip if already added
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'href="market.html"' in content:
        continue
    
    # Replace the end of the nav block with the new item appended
    # Most navs end with </nav>
    content = content.replace('</nav>', nav_item_market)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Added Job Market link to all nav bars")
