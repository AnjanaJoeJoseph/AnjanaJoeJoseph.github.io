#!/usr/bin/env python3
import os
import re

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class_map = {}
id_map = {}

sel_regex = re.compile(r'([.#])([A-Za-z0-9_-]+)')

# collect CSS files
css_files = []
for dirpath, dirs, files in os.walk(root):
    for f in files:
        if f.endswith('.css'):
            css_files.append(os.path.join(dirpath, f))

for css in css_files:
    try:
        txt = open(css, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    matches = sel_regex.findall(txt)
    for prefix, name in matches:
        if prefix == '.':
            class_map.setdefault(name, set()).add(css)
        else:
            id_map.setdefault(name, set()).add(css)

# search for usages in HTML/JS/PHP files
search_files = []
for dirpath, dirs, files in os.walk(root):
    for f in files:
        if f.endswith(('.html', '.htm', '.js', '.php')):
            search_files.append(os.path.join(dirpath, f))

used_classes = set()
used_ids = set()

for filepath in search_files:
    try:
        content = open(filepath, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    for name in list(class_map.keys()):
        # look for class="...name..." or className usages or plain token matches
        if re.search(r'class\s*=\s*["\'][^"\']*\b' + re.escape(name) + r'\b', content) or re.search(r'\bclassName\b.*\b' + re.escape(name) + r'\b', content) or re.search(r'\b' + re.escape(name) + r'\b', content):
            used_classes.add(name)
    for name in list(id_map.keys()):
        if re.search(r'id\s*=\s*["\']' + re.escape(name) + r'["\']', content) or re.search(r'#["\']?' + re.escape(name) + r'\b', content) or re.search(r'getElementById\s*\(\s*["\']' + re.escape(name) + r'["\']\s*\)', content):
            used_ids.add(name)

unused_classes = sorted([n for n in class_map if n not in used_classes])
unused_ids = sorted([n for n in id_map if n not in used_ids])

out_lines = []
out_lines.append("Unused classes ({}):\n".format(len(unused_classes)))
for n in unused_classes:
    out_lines.append(n + "  defined in: " + ", ".join(sorted(class_map[n])) + "\n")

out_lines.append("\nUnused ids ({}):\n".format(len(unused_ids)))
for n in unused_ids:
    out_lines.append(n + "  defined in: " + ", ".join(sorted(id_map[n])) + "\n")

report_dir = os.path.join(root, 'tools')
os.makedirs(report_dir, exist_ok=True)
report_path = os.path.join(report_dir, 'unused_css_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.writelines(out_lines)

print('Report written to', report_path)
