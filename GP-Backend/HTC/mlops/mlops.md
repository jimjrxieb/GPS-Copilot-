Alright, Jimmie — your tree is solid. Here’s the **surgical delta** to morph GP-RAG into the **Kube PAC Copilot** without blowing up what already works. I’m giving you **full paths + real code** (security-first, deterministic) so you can paste-and-run.

---

# 0) Create new folders

```bash
mkdir -p policies/gatekeeper/templates \
         policies/gatekeeper/constraints \
         policies/conftest/policy_packs \
         data/fixtures/{positive,negative} \
         data/failures \
         src/{features,retrieve,rank,policy_gen,troubleshoot,ci,graph,api} \
         .github/workflows \
         grafana/dashboards \
         mlflow
```

---

# 1) Seed a tiny policy corpus

## `policies/index.jsonl`

```json
{"id":"deny_privileged_containers","kind":["Pod","Deployment"],"tags":["cis:1.0","no-privileged"],"features":["securityContext.privileged=true"],"reliability":"high"}
{"id":"deny_latest_tag","kind":["Pod","Deployment"],"tags":["cis:5.5.1","images"],"features":["image.tag=latest"],"reliability":"medium"}
```

## `policies/gatekeeper/templates/privileged_containers_template.rego`

```rego
package k8sdeny.privileged_containers

violation[{"msg": msg, "details": {"container": c.name}}] {
  input.review.kind.kind == "Pod"
  c := input.review.object.spec.containers[_]
  c.securityContext.privileged == true
  msg := sprintf("Privileged container %s is not allowed", [c.name])
}
```

## `policies/conftest/policy_packs/deny_latest_tag.rego`

```rego
package k8sdeny.image_tags

deny[msg] {
  input.kind == "Pod"
  c := input.spec.containers[_]
  endswith(c.image, ":latest")
  msg := sprintf("Image '%s' uses :latest tag", [c.image])
}
```

---

# 2) Minimal fixtures (truth set)

## `data/fixtures/positive/privileged_pod.json`

```json
{
  "review": {
    "kind": {"kind":"Pod"},
    "object": {"spec": {"containers":[{"name":"a","securityContext":{"privileged":true}}]}}
  }
}
```

## `data/fixtures/negative/non_privileged_pod.json`

```json
{
  "review": {
    "kind": {"kind":"Pod"},
    "object": {"spec": {"containers":[{"name":"a","securityContext":{"runAsNonRoot":true,"allowPrivilegeEscalation":false}}]}}
  }
}
```

---

# 3) Feature extraction (from K8s YAML → typed features)

## `src/features/extract.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deterministic feature extractor for K8s manifests.
Security-first: no network, no exec. Pure parsing.
"""
import json, sys, os, glob, yaml
from typing import Dict, Any, List

SAFE_KINDS = {"Pod","Deployment","StatefulSet","DaemonSet","Job","CronJob","ReplicaSet","Role","ClusterRole","NetworkPolicy"}

def _image_tag(image: str) -> str:
    if ":" in image:
        return image.rsplit(":",1)[1]
    return "latest-implicit"

def features_from_manifest(doc: Dict[str, Any]) -> Dict[str, Any]:
    kind = str(doc.get("kind",""))
    if kind not in SAFE_KINDS:
        return {"resource_kind": kind, "features": {}}
    f = {"resource_kind": kind, "features": {}}

    spec = None
    if kind in {"Pod"}:
        spec = doc.get("spec",{})
    elif kind in {"Deployment","ReplicaSet","StatefulSet","DaemonSet","Job","CronJob"}:
        spec = (((doc.get("spec",{}) or {}).get("template",{}) or {}).get("spec",{}) or {})
    if spec is not None:
        containers = spec.get("containers",[]) or []
        any_priv = any(bool((c.get("securityContext") or {}).get("privileged", False)) for c in containers)
        any_ape  = any(bool((c.get("securityContext") or {}).get("allowPrivilegeEscalation", False)) for c in containers)
        any_hostpath = any(v.get("hostPath") is not None for v in (spec.get("volumes") or []))
        tags = [ _image_tag(c.get("image","")) for c in containers if c.get("image") ]
        any_latest = any(t == "latest" or t == "latest-implicit" for t in tags)

        f["features"].update({
            "securityContext.privileged": any_priv,
            "securityContext.allowPrivilegeEscalation": any_ape,
            "volume.hostPath": any_hostpath,
            "image.tag_latest": any_latest
        })

    if kind in {"Role","ClusterRole"}:
        rules = doc.get("rules",[]) or []
        wildcard_verbs = any("*" in (r.get("verbs") or []) for r in rules)
        f["features"]["rbac.wildcard_verbs"] = wildcard_verbs

    if kind == "NetworkPolicy":
        f["features"]["netpol_present"] = True

    return f

def run(bundle_glob: str) -> List[Dict[str, Any]]:
    paths = glob.glob(bundle_glob, recursive=True)
    out = []
    for p in paths:
        with open(p, "r", encoding="utf-8") as fh:
            # Support multi-doc YAML
            for doc in yaml.safe_load_all(fh):
                if not isinstance(doc, dict):
                    continue
                out.append(features_from_manifest(doc))
    return out

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: extract.py '<glob/of/*.yaml>'")
        sys.exit(2)
    feats = run(sys.argv[1])
    json.dump(feats, sys.stdout, indent=2)
```

---

# 4) Retrieval (hybrid keyword + simple embedding fallback)

## `src/retrieve/index.py`

```python
#!/usr/bin/env python3
import json, re
from typing import List, Dict, Any

def load_index(path: str) -> List[Dict[str,Any]]:
    with open(path,"r",encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]

def score(policy: Dict[str,Any], feat: Dict[str,Any]) -> float:
    # heuristic: +1 for each matching feature condition, +0.5 for matching kind
    s = 0.0
    kinds = policy.get("kind",[])
    if feat.get("resource_kind") in kinds:
        s += 0.5
    conditions = policy.get("features",[])
    for cond in conditions:
        # format "key=value"
        if "=" in cond:
            k,v = cond.split("=",1)
            fv = feat.get("features",{}).get(k.replace(".","."))  # already dotted keys
            v = True if v.lower() in ("true","1","yes") else v
            if str(fv).lower() == str(v).lower():
                s += 1.0
    return s

def retrieve_top(index_path: str, feats: List[Dict[str,Any]], top_n:int=5) -> List[Dict[str,Any]]:
    idx = load_index(index_path)
    ranked = []
    for f in feats:
        best = sorted(((score(p,f), p) for p in idx), key=lambda x: x[0], reverse=True)[:top_n]
        ranked.append({"feature":f, "candidates":[b[1] for b in best if b[0] > 0]})
    return ranked

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("usage: index.py policies/index.jsonl features.json")
        sys.exit(2)
    out = retrieve_top(sys.argv[1], json.load(open(sys.argv[2])))
    print(json.dumps(out, indent=2))
```

---

# 5) Ranker (deterministic v0 wrapper)

## `src/rank/model.py`

```python
#!/usr/bin/env python3
"""
Stub ranker. Deterministic, no external deps. Upgrade to MLflow later.
"""
from typing import List, Dict, Any
from src.retrieve.index import retrieve_top

def rank(index_path: str, feature_json_path: str, top_n:int=5) -> List[Dict[str,Any]]:
    import json
    feats = json.load(open(feature_json_path))
    return retrieve_top(index_path, feats, top_n=top_n)

if __name__ == "__main__":
    import sys, json
    if len(sys.argv)<3:
        print("usage: model.py policies/index.jsonl extracted_features.json")
        sys.exit(2)
    res = rank(sys.argv[1], sys.argv[2], top_n=5)
    json.dump(res, sys.stdout, indent=2)
```

---

# 6) Draft Rego + run tests (no LLM yet, just template stitcher)

## `src/policy_gen/schemas.py`

```python
from pydantic import BaseModel
from typing import List, Dict, Any

class DraftOutput(BaseModel):
    rego_package: str
    rego_code: str
    tests: List[Dict[str, Any]]  # {"name": str, "type": "deny|allow", "input_fixture": dict}
```

## `src/policy_gen/drafter.py`

```python
#!/usr/bin/env python3
"""
Grounded drafter: for now, map candidate IDs to known templates.
Later: add LLM constrained by retrieved exemplars.
"""
import json, pathlib
from typing import Dict, Any, List
from .schemas import DraftOutput

TEMPLATES = {
    "deny_privileged_containers": "policies/gatekeeper/templates/privileged_containers_template.rego"
}

def draft(policy_id: str) -> DraftOutput:
    path = TEMPLATES.get(policy_id)
    if not path:
        raise ValueError(f"Unknown policy_id {policy_id}")
    code = pathlib.Path(path).read_text(encoding="utf-8")
    tests = [
        {"name":"denies_privileged","type":"deny","input_fixture":json.loads(pathlib.Path("data/fixtures/positive/privileged_pod.json").read_text())},
        {"name":"allows_non_privileged","type":"allow","input_fixture":json.loads(pathlib.Path("data/fixtures/negative/non_privileged_pod.json").read_text())}
    ]
    return DraftOutput(rego_package="k8sdeny.privileged_containers", rego_code=code, tests=tests)

if __name__ == "__main__":
    import sys
    if len(sys.argv)<2:
        print("usage: drafter.py policy_id")
        sys.exit(2)
    out = draft(sys.argv[1]).model_dump()
    print(json.dumps(out, indent=2))
```

## `src/policy_gen/test_runner.py`

```python
#!/usr/bin/env python3
"""
Runs OPA unit tests without writing to repo. Sandboxed temp dir.
Requires `opa` and `conftest` binaries installed in PATH.
"""
import json, os, tempfile, subprocess, shutil, sys
from typing import Dict, Any
from .schemas import DraftOutput

def _write_bundle(tmp, draft: DraftOutput):
    policy_path = os.path.join(tmp, "policy.rego")
    with open(policy_path,"w",encoding="utf-8") as fh:
        fh.write(draft.rego_code)
    # materialize tests as rego unit tests
    tests_path = os.path.join(tmp, "policy_test.rego")
    with open(tests_path,"w",encoding="utf-8") as fh:
        fh.write(f'package {draft.rego_package}_test\n\n')
        fh.write(f'import data.{draft.rego_package} as policy\n\n')
        i = 0
        for t in draft.tests:
            i += 1
            if t["type"] == "deny":
                fh.write(f"test_deny_{i} {{\n  input := {json.dumps(t['input_fixture'])}\n  some v\n  policy.violation[v] with input as input\n}}\n\n")
            else:
                fh.write(f"test_allow_{i} {{\n  input := {json.dumps(t['input_fixture'])}\n  not policy.violation[_] with input as input\n}}\n\n")
    return policy_path, tests_path

def run_opa_tests(draft: DraftOutput) -> Dict[str,Any]:
    tmp = tempfile.mkdtemp(prefix="opa_")
    try:
        _write_bundle(tmp, draft)
        proc = subprocess.run(["opa","test",tmp], capture_output=True, text=True)
        return {"rc": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    if sys.stdin.isatty():
        print("Pass DraftOutput JSON on stdin.")
        sys.exit(2)
    draft = DraftOutput.model_validate_json(sys.stdin.read())
    res = run_opa_tests(draft)
    print(json.dumps(res, indent=2))
```

---

# 7) Troubleshooter (linter + counterexample skeletons)

## `src/troubleshoot/rego_linter.py`

```python
#!/usr/bin/env python3
import re
from typing import List, Dict

ANTIPATTERNS = [
    (re.compile(r'violation\s*\[\s*.*\s*\]\s*{[^}]*input\.review[^}]*}'), "ok"),  # example hook, extend later
    (re.compile(r'contains\('), "check contains() overuse; may overmatch images"),
    (re.compile(r'foreach|every'), "comprehensions can be slow; consider early exit or indexing")
]

def lint(rego_code: str) -> List[Dict[str,str]]:
    finds = []
    for rx, msg in ANTIPATTERNS:
        if rx.search(rego_code):
            finds.append({"rule":"pattern", "message": msg})
    return finds
```

## `src/troubleshoot/counterexample.py`

```python
#!/usr/bin/env python3
"""
Minimal counterexample: flip key booleans and see if violation toggles.
(Upgrade later with `opa eval` strategies)
"""
import json, copy
from typing import Dict, Any

def toggle_privileged(inp: Dict[str,Any]) -> Dict[str,Any]:
    try:
        c = inp["review"]["object"]["spec"]["containers"][0]
        sc = c.setdefault("securityContext",{})
        sc["privileged"] = not bool(sc.get("privileged", False))
    except Exception:
        pass
    return inp

def synthesize(base_input: Dict[str,Any]) -> Dict[str,Any]:
    return toggle_privileged(copy.deepcopy(base_input))

if __name__ == "__main__":
    import sys
    data = json.load(sys.stdin)
    print(json.dumps(synthesize(data)))
```

## `src/troubleshoot/fix_recommender.py`

```python
#!/usr/bin/env python3
from typing import Dict, Any

def manifest_patch_minimal() -> str:
    return (
        "+ securityContext:\n"
        "+   runAsNonRoot: true\n"
        "+   allowPrivilegeEscalation: false\n"
    )

def policy_patch_minimal() -> str:
    return (
        "# consider allowlist for approved registries:\n"
        "# startswith(c.image, sprintf(\"%s/\", [input.params.allowed_registry]))\n"
    )

def recommend(strategy: str="auto") -> Dict[str,str]:
    if strategy == "manifest":
        return {"manifest_diff": manifest_patch_minimal(), "policy_diff": "", "rationale":"Prefer least surprise for developers"}
    if strategy == "policy":
        return {"manifest_diff":"", "policy_diff": policy_patch_minimal(), "rationale":"Tighten posture globally"}
    # auto -> default to manifest patch
    return recommend("manifest")

if __name__ == "__main__":
    print(recommend("auto"))
```

---

# 8) CI outputs (SARIF + PR comment)

## `src/ci/report_sarif.py`

```python
#!/usr/bin/env python3
import json, sys, time

def make_sarif(violations):
    return {
      "version": "2.1.0",
      "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
      "runs": [{
        "tool": {"driver": {"name": "kube-pac-copilot","informationUri":"https://example.local"}},
        "results": [{
          "ruleId": v.get("id","policy"),
          "message": {"text": v.get("msg","violation")},
          "level": "error"
        } for v in violations]
      }]
    }

if __name__ == "__main__":
    # stdin: [{"id":"deny_privileged_containers","msg":"..."}]
    violations = json.load(sys.stdin)
    sarif = make_sarif(violations)
    json.dump(sarif, sys.stdout, indent=2)
```

## `.github/workflows/policy_scan.yml`

```yaml
name: policy-scan
on:
  pull_request:
    paths: ["**/*.yaml","**/*.yml","policies/**","src/**"]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Install OPA/Conftest
        run: |
          curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
          chmod +x opa && sudo mv opa /usr/local/bin/opa
          curl -L -o conftest.tar.gz https://github.com/open-policy-agent/conftest/releases/latest/download/conftest_Linux_x86_64.tar.gz
          tar xzf conftest.tar.gz && sudo mv conftest /usr/local/bin/conftest
      - name: Install deps
        run: pip install pyyaml pydantic
      - name: Extract features
        run: |
          python src/features/extract.py "**/*.yaml" > out.features.json || echo "[]"> out.features.json
      - name: Rank policies
        run: |
          python src/rank/model.py policies/index.jsonl out.features.json > out.rank.json
      - name: Draft & test privileged policy
        run: |
          python -c 'import json,sys; r=json.load(open("out.rank.json"))[0]["candidates"]; print([c["id"] for c in r])'
          python src/policy_gen/drafter.py deny_privileged_containers > draft.json
          cat draft.json | python src/policy_gen/test_runner.py > opa_test.json
          cat opa_test.json
      - name: Build SARIF (placeholder)
        run: |
          echo '[{"id":"deny_privileged_containers","msg":"Example violation"}]' | python src/ci/report_sarif.py > report.sarif
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: report.sarif }
```

---

# 9) API skeleton (so you can curl it)

## `src/api/app.py`

```python
#!/usr/bin/env python3
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import json, tempfile, subprocess

from src.features.extract import features_from_manifest
from src.retrieve.index import retrieve_top
from src.policy_gen.drafter import draft
from src.policy_gen.test_runner import run_opa_tests

app = FastAPI(title="Kube PAC Copilot", version="0.1.0")

class AnalyzeReq(BaseModel):
    manifest: Dict[str,Any]
    top_n: int = 3

@app.post("/analyze")
def analyze(req: AnalyzeReq):
    feats = features_from_manifest(req.manifest)
    ranked = retrieve_top("policies/index.jsonl", [feats], top_n=req.top_n)
    return {"features":feats, "candidates": ranked[0]["candidates"] if ranked else []}

class ProposeReq(BaseModel):
    policy_id: str

@app.post("/propose")
def propose(req: ProposeReq):
    d = draft(req.policy_id)
    res = run_opa_tests(d)
    return {"draft": d.model_dump(), "tests": res}

@app.get("/health")
def health():
    return {"status":"ok"}
```

**Run locally:**

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8006
```

---

# 10) Grafana dashboard placeholder

## `grafana/dashboards/policy_health.json`

```json
{
  "title": "Kube PAC Copilot - Policy Health",
  "panels": [
    {"type":"stat","title":"Policy Coverage","targets":[]},
    {"type":"graph","title":"Violations Over Time","targets":[]}
  ],
  "schemaVersion": 37
}
```

---

# 11) Acceptance quick-test

**Smoke test the full path (no LLM, deterministic):**

```bash
python src/features/extract.py "**/*.yaml" > out.features.json || echo "[]"> out.features.json
python src/rank/model.py policies/index.jsonl out.features.json > out.rank.json
python src/policy_gen/drafter.py deny_privileged_containers > draft.json
cat draft.json | python src/policy_gen/test_runner.py
```

You’ll see JSON with `rc: 0` if tests pass.

---

## Why this works (and gets you hired)

* You kept your **GP-RAG brain** intact.
* You added a **policy lane** (features → retrieve → rank → draft → test) and a **troubleshooter lane** you can iterate on.
* You wired a clean **CI surface** (SARIF upload), an **API**, and **fixtures** to measure false positives.

Want me to add a **`docker-compose.yml`** that boots `uvicorn`, a Prometheus stub, and Grafana with this dashboard preloaded — all on your standard ports?
