#!/usr/bin/env python3
"""Fail-closed local GASP credential gate. Never print matching bytes."""
import argparse, base64, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
from urllib.parse import quote

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.DEVNULL)

def denied(name):
    parts = Path(name).parts
    return any(p in {'.yoyo', '.ssh', '.aws', '.wrangler'} for p in parts) or any(
        p in {'.env', '.dev.vars', '.yoyo.toml', 'yoyo-session.json', 'credentials.json', 'secrets.json'}
        or p.startswith(('.env.', '.dev.vars.')) or p.endswith(('.pem', '.key')) for p in parts
    ) or name.startswith(('execution/private/', '.agent/bin/'))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',default='.');ap.add_argument('--mode',choices=['staged','tree','history'],default='staged');args=ap.parse_args()
    repo=Path(git(args.repo,'rev-parse','--show-toplevel').decode().strip())
    scanner=os.environ.get('GITLEAKS_BIN') or shutil.which('gitleaks') or str(repo/'.agent/bin/gitleaks')
    if not Path(scanner).is_file():
        raise RuntimeError('Gitleaks unavailable; commit/push blocked. Install the verified scanner.')
    known=[]
    for key,value in os.environ.items():
        if re.search(r'(TOKEN|SECRET|PASSWORD|API_KEY|PRIVATE_KEY)',key,re.I) and len(value)>=8:
            known.extend([value.encode(),json.dumps(value)[1:-1].encode(),quote(value,safe='').encode(),base64.b64encode(value.encode())])
    with tempfile.TemporaryDirectory(prefix='gasp-credential-gate-') as tmp:
        root=Path(tmp);snapshot=root/'snapshot';snapshot.mkdir();report=root/'report.json';config=root/'config.toml';ignore=root/'ignore'
        config.write_text('[extend]\nuseDefault = true\n');ignore.write_text('')
        entries=git(repo,'ls-files','--stage','-z') if args.mode=='staged' else git(repo,'ls-tree','-r','-z','HEAD')
        failures=[]
        for entry in entries.split(b'\0'):
            if not entry:continue
            meta,rawname=entry.split(b'\t',1);name=rawname.decode('utf-8');fields=meta.decode().split();mode=fields[0];oid=fields[1] if args.mode=='staged' else fields[2]
            if args.mode=='staged' and fields[2]!='0':raise RuntimeError('Unmerged index; scan blocked')
            if denied(name):failures.append((name,'forbidden-local-file'));continue
            if mode not in ('100644','100755'):failures.append((name,'unsupported-file-mode'));continue
            data=git(repo,'cat-file','blob',oid)
            if any(secret in data for secret in known):failures.append((name,'runtime-credential-value'))
            target=snapshot/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        env={k:v for k,v in os.environ.items() if not k.startswith('GITLEAKS_')}
        command=[scanner,'git' if args.mode=='history' else 'dir',str(repo if args.mode=='history' else snapshot),
            '--config',str(config),'--gitleaks-ignore-path',str(ignore),'--ignore-gitleaks-allow',
            '--redact=100','--no-banner','--no-color','--max-decode-depth','5','--max-archive-depth','3',
            '--timeout','180','--report-format','json','--report-path',str(report)]
        if args.mode=='history':command+=['--log-opts=--all --full-history']
        result=subprocess.run(command,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=200)
        if result.returncode not in (0,1) or not report.exists():raise RuntimeError('Credential scanner failed; blocked (raw diagnostics suppressed)')
        for finding in json.loads(report.read_text()):
            name=finding.get('File','unknown');name=name.removeprefix(str(snapshot)+'/')
            failures.append((name,finding.get('RuleID','credential-pattern')))
        if result.returncode==1 and not failures:raise RuntimeError('Scanner rejected content; blocked')
        if failures:
            print('Credential gate BLOCKED. Values and matched lines are suppressed.',file=sys.stderr)
            for name,rule in sorted(set(failures)):print(json.dumps({'file':name,'rule':rule}),file=sys.stderr)
            return 1
    print('Credential gate passed ('+args.mode+'). Pattern scanning cannot prove absence of every possible secret.')
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except Exception:
        print('Credential gate could not complete; commit/push BLOCKED. No credential values printed.',file=sys.stderr);sys.exit(2)
