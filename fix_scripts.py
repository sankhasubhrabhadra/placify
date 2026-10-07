for file in ['frontend/simulator.html', 'frontend/jobs.html']:
    with open(file, 'r', encoding='utf-8') as f:
        html = f.read()
    if '<script src="script.js"></script>' not in html:
        html = html.replace('</body>', '  <script src="script.js"></script>\n</body>')
        with open(file, 'w', encoding='utf-8') as f:
            f.write(html)
print('Done')
