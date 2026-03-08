import os, glob

EM = '\u2014'
REPL = '-'

seen = set()
files = []
for pat in ['SECURITY.md','GLOSSARY.md','TERMS_OF_USE.md','CHANGELOG.md','README.md','CONTRIBUTING.md']:
    if os.path.exists(pat) and pat not in seen:
        seen.add(pat); files.append(pat)
for f in sorted(glob.glob('docs/**/*.md', recursive=True)):
    key = os.path.normpath(f)
    if key not in seen:
        seen.add(key); files.append(f)
for f in sorted(glob.glob('proof_sheets/**/*.md', recursive=True)):
    key = os.path.normpath(f)
    if key not in seen:
        seen.add(key); files.append(f)

total = 0
for f in files:
    try:
        text = open(f, encoding='utf-8').read()
    except Exception:
        text = open(f, encoding='cp1252').read()
    count = text.count(EM)
    if count > 0:
        new_text = text.replace(' ' + EM + ' ', ' - ').replace(EM, '-')
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(new_text)
        print(f'REMOVED {count:4d}  {f}')
        total += count
    else:
        print(f'       0  {f}')

print(f'\nTotal em dashes removed: {total}')
