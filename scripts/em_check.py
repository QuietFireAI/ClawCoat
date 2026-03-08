import os, glob

EM = '\u2014'
seen = set()
files = []
for pat in ['SECURITY.md','GLOSSARY.md','TERMS_OF_USE.md','CHANGELOG.md','README.md','CONTRIBUTING.md']:
    if os.path.exists(pat) and pat not in seen:
        seen.add(pat); files.append(pat)
for f in sorted(glob.glob('docs/**/*.md', recursive=True)):
    key = os.path.normpath(f)
    if key not in seen:
        seen.add(key); files.append(f)

old_versions = ['v10.0.0Bminus','v9.','v8.','v7.','v6.','v5.','v4.3','v4.2','v4.0','4.0.x','3.0.x']

for f in files:
    try:
        text = open(f, encoding='utf-8').read()
    except Exception:
        text = open(f, encoding='cp1252').read()
    em = text.count(EM)
    vflags = [v for v in old_versions if v in text]
    flag = ', '.join(vflags) if vflags else 'ok'
    print(f'{em:4d}  {flag:40s}  {f}')
