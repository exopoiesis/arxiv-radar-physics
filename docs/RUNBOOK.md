# Physics arxiv-radar Runbook

Operational checklist for bootstrapping and refreshing the physics corpus.
Run commands from the repository root.

## Environment

Use the local virtual environment and keep temporary artifacts under `tmp/`.

```powershell
$env:TEMP = (Resolve-Path tmp).Path
$env:TMP = $env:TEMP
$env:PIP_CACHE_DIR = Join-Path $env:TEMP "pip-cache"

python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt -r requirements-tag-analysis.txt
```

## Historical Backfill

Backfill is idempotent and resumable. Progress is stored in
`data/backfill_checkpoint.json`; partial runs can be restarted with the same
command.

```powershell
$env:TEMP = (Resolve-Path tmp).Path
$env:TMP = $env:TEMP
.venv\Scripts\python.exe tools\backfill.py --from-date 2024-05-01 --to-date 2026-05-03
```

Outputs:

- `data/papers-YYYY-MM.json` monthly shards
- `data/backfill_checkpoint.json` resumable checkpoint
- `docs/abstracts/<arxiv-id>.html` popup fragments for Pages

The fetch topics come from `config.yaml`. Generic AI phrases should be written
as `RAW:` expressions with physics/scientific context if they start pulling too
many broad ML papers.

## Render Derived Pages

After backfill, regenerate all derived public views.

```powershell
$env:TEMP = (Resolve-Path tmp).Path
$env:TMP = $env:TEMP
.venv\Scripts\python.exe tools\render_abstracts.py
.venv\Scripts\python.exe tools\render_readme.py
.venv\Scripts\python.exe tools\render_tag_pages.py
.venv\Scripts\python.exe tools\render_index.py
```

Outputs:

- `README.md`
- `abstracts/<arxiv-id>.md` only for papers linked from README
- `docs/tag/<tag>-<window>.md`
- `docs/index.md`
- `docs/_data/tag_index.yml`

## Tag Candidate Analysis

Run candidate extraction after the first complete backfill, or after a major
query/filter change. Write intermediate candidate files to `tmp/` first so the
curated tag vocabulary stays clean.

```powershell
$env:TEMP = (Resolve-Path tmp).Path
$env:TMP = $env:TEMP
.venv\Scripts\python.exe tools\tag_analysis.py --out-dir tmp\tag-candidates --top-n 300
```

Review:

- `tmp/tag-candidates/candidates_tfidf.json`
- `tmp/tag-candidates/candidates_yake.json`
- `tmp/tag-candidates/comparison.md`

Promote useful terms manually into `tags/canonical.yaml` as canonical tags and
synonyms. Keep generic terms out unless they distinguish physics subdomains.

## Retag Existing Corpus

After editing `tags/canonical.yaml`, re-tag all paper records and regenerate
derived views.

```powershell
$env:TEMP = (Resolve-Path tmp).Path
$env:TMP = $env:TEMP
.venv\Scripts\python.exe tools\retag_corpus.py
.venv\Scripts\python.exe tools\render_abstracts.py --force
.venv\Scripts\python.exe tools\render_readme.py
.venv\Scripts\python.exe tools\render_tag_pages.py
.venv\Scripts\python.exe tools\render_index.py
```

## Optional Corpus Re-filter

If `tools/data_io.py` physics-context filtering is tightened, re-apply it to
the existing corpus in a scratch folder first.

```powershell
$env:TEMP = (Resolve-Path tmp).Path
$env:TMP = $env:TEMP
.venv\Scripts\python.exe tools\filter_corpus.py --out-dir tmp\data-filtered
```

Inspect the reported kept/dropped counts per topic. If the result looks good,
replace `data/` from the filtered output, then run the retag/render sequence.

## Verification

```powershell
$env:TEMP = (Resolve-Path tmp).Path
$env:TMP = $env:TEMP
$stamp = Get-Date -Format yyyyMMddHHmmss
.venv\Scripts\python.exe -m pytest tests -q --basetemp "tmp\pytest-run-$stamp" -o "cache_dir=tmp\pytest-cache-$stamp"
```
