# usage: python3 -I extract.py <run-name> -> writes risks_<anon>.md ; anon id given as argv[2]
import json,sys,pathlib
run,anon=sys.argv[1],sys.argv[2]; B=pathlib.Path.home()/'scratch-relai/bench'
res=''
for l in open(B/'logs'/f'{run}.jsonl'):
    try:e=json.loads(l)
    except Exception: continue
    if e.get('type')=='result': res=e.get('result','')
parts=['# Final answer to the user\n\n'+res]
rd=B/run/'relai/wiki/risks'
if rd.is_dir():
    for p in sorted(rd.glob('*.md')): parts.append(f'# Risk page {p.name}\n\n'+p.read_text())
(B/'scoring'/f'risks_{anon}.md').write_text('\n\n---\n\n'.join(parts))
