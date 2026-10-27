#!/usr/bin/env python3
"""Pin each focus site's best CLAIM raster to a commit and verify its blob via the GitHub API.

Writes evidence/focus9_sources_20261027.json (raw/blob URLs at the default-branch HEAD).
"""
import json, subprocess, sys
sys.path[:0]=['.','scripts']
claims=json.load(open('evidence/claims_matched_20261027.json'))['rows']
inv=json.load(open('.cache/registry_v3/inventory.json'))
sites=['GEMSDOE24','GEMSDOE25','GEMSDOE27','GEMSDOE28','GEMSDOE30','GEMSDOE31','GEMSDOE32','GEMSDOE33','GEMSDOE36']
out={}
for s in sites:
    rows=[r for r in claims if r['site']==s]
    best=max(rows,key=lambda r:r['claim'])
    head=subprocess.check_output(['git','ls-remote',f'https://github.com/buffedlizard55-lab/{s}.git','HEAD']).decode().split()[0]
    m=best['match']
    # verify blob at that commit
    meta=json.loads(subprocess.check_output(['gh','api',f"repos/buffedlizard55-lab/{s}/contents/{m['path']}?ref={head}",'--jq','{sha:.sha,size:.size,path:.path}']).decode())
    f=[x for r in inv['repositories'] if r['repo']==s for x in r['files'] if x['sha256']==m['sha256']][0]
    out[s]=dict(all=[(r['name'],r['claim']) for r in rows],best=best['name'],claim=best['claim'],repo=s,path=m['path'],sha256=m['sha256'],bytes=m['bytes'],
                commit=head,blob_api=meta['sha'],blob_inventory=f['git_blob_sha1'],blob_match=meta['sha']==f['git_blob_sha1'],
                raw_url=f"https://github.com/buffedlizard55-lab/{s}/raw/{head}/{m['path']}",
                blob_url=f"https://github.com/buffedlizard55-lab/{s}/blob/{head}/{m['path']}")
    print(s,best['claim'],best['name'][:50],head[:10],meta['sha']==f['git_blob_sha1'])
json.dump(out,open('evidence/focus9_sources_20261027.json','w'),indent=1)
