import hashlib, json, pathlib, subprocess, sys
root = pathlib.Path.cwd()
def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()
files = git('ls-files').splitlines()
records = []
for name in files:
    path = root / name
    if path.is_file():
        records.append({'path':name, 'gitBlob':git('rev-parse', 'HEAD:'+name), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
evidence = {'stage':sys.argv[1], 'headSha':git('rev-parse','HEAD'), 'status':git('status','--porcelain'), 'files':records, 'artifacts':[]}
for folder in ['dist','compat/dist','hooks/dist','debug/dist','devtools/dist','jsx-runtime/dist','test-utils/dist']:
    for path in (root/folder).glob('*'):
        if path.is_file():
            evidence['artifacts'].append({'path':str(path.relative_to(root)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
out = root.parent/'evidence'
out.mkdir(exist_ok=True)
(out/(sys.argv[1]+'.json')).write_text(json.dumps(evidence,indent=2))
print(json.dumps({'stage':evidence['stage'],'headSha':evidence['headSha'],'trackedFiles':len(records),'status':evidence['status']}))
if git('diff','--name-only','HEAD'):
    raise SystemExit('Tracked source was modified during validation')
