# Huong Dan Su Dung Repo

Repo nay la lab Day 04 ve research agent co tool-calling. Agent co the tim tin web, tim tweet, doc URL, tim paper arXiv, doc text paper, format digest, kiem tra/cham nguon, tao reference, va gui Telegram sau khi user xac nhan.

## 1. Cau Truc Quan Trong

```text
starter_v0/
  ui_app.py                  # UI Streamlit
  chat.py                    # Chat CLI, luu transcript JSON
  run_eval.py                # Chay eval, luu run JSON
  artifacts/
    system_prompt.md         # System prompt hien tai
    tools.yaml               # Khai bao tool cho model
    version_log.csv          # Log v0, v1, v2, v3
    REPORT.md                # Bao cao nop bai
  data/
    eval_base.json           # Base eval cua de
    eval_group.json          # 10 case nhom tu viet: 5 single + 5 multi
  runs/                      # Ket qua eval JSON
  transcripts/               # Transcript chat JSON
  tools/                     # Code cac tool
```

## 2. Setup Moi Truong

Chay tu root repo:

```powershell
cd starter_v0
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Tao file `.env` trong `starter_v0/`. Khong commit file nay len GitHub.

Toi thieu de chay provider Gemini:

```env
GEMINI_API_KEY=...
```

Neu muon dung day du tool web, X/Twitter, Telegram:

```env
TAVILY_API_KEY=...
FIRECRAWL_API_KEY=...
RAPIDAPI_KEY=...
RAPIDAPI_TWITTER_HOST=twitter-api45.p.rapidapi.com
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Kiem tra provider:

```powershell
python scripts/preflight_provider.py --provider gemini
```

## 3. Chay UI

Tu folder `starter_v0`:

```powershell
streamlit run ui_app.py
```

Mo trinh duyet tai:

```text
http://localhost:8501
```

UI co cac tab chinh:

- `Chat`: chat voi agent bang provider Gemini.
- `Eval`: chay base/group eval truc tiep.
- `Runs`: xem cac file JSON trong `runs/`.
- `Artifacts`: xem prompt, tools, report, version log.

## 4. Public UI Bang Cloudflare Tunnel

Chay UI local truoc:

```powershell
streamlit run ui_app.py
```

Mo terminal khac:

```powershell
cloudflared tunnel --url http://localhost:8501
```

Lenh nay tra ve link dang:

```text
https://<random>.trycloudflare.com
```

Link nay chi song khi lenh `cloudflared` con dang chay.

## 5. Chay Chat CLI

Tu folder `starter_v0`:

```powershell
python chat.py --provider gemini --version v3
```

Moi phien chat se tao transcript trong:

```text
transcripts/*.transcript.json
```

Vi du cau hoi de demo:

```text
Tin AI hom nay co gi noi bat?
Tom tat 5 tweet moi nhat ve AI agents.
Tao danh muc tham chieu APA tu metadata paper nay...
Dang ban tin nay len Telegram giup minh.
```

Voi yeu cau dang/gui Telegram, agent phai hoi xac nhan yes/no truoc. Chi khi user xac nhan ro, tool `send` moi duoc goi voi `confirmed=true`.

## 6. Chay Eval

Chay base eval:

```powershell
python run_eval.py --provider gemini --version v3 --suite base --eval-cases data/eval_base.json
```

Chay group eval 10 case tu viet:

```powershell
python run_eval.py --provider gemini --version v3 --suite group --eval-cases data/eval_group.json
```

Ket qua se nam trong:

```text
runs/*.json
```

Trong run JSON, can xem cac field:

- `summary.case_accuracy`
- `summary.tool_routing_accuracy`
- `summary.argument_accuracy`
- `summary.multiturn_accuracy`
- `results[*].result.failures`
- `results[*].tool_results`

## 7. Tool Hien Co

Core/bonus tools:

- `clarify`: hoi lai user khi thieu thong tin hoac can confirmation.
- `timeline`: lay tweet gan day cua mot account X/Twitter.
- `social_search`: tim tweet theo tu khoa.
- `lookup`: tim web/news.
- `fetch`: doc noi dung URL.
- `format`: format item thanh markdown digest.
- `send`: gui Telegram, bat buoc co confirmation.
- `policy`: tim company policy noi bo.
- `papers`: tim paper arXiv.
- `paper_text`: lay text tu paper arXiv.
- `source_check`: kiem tra chat luong nguon cua item da co.

4 tool moi cua nhom:

- `extract_key_points`: rut y chinh tu text/items da co.
- `compare_sources`: so sanh hai hoac nhieu nguon da co.
- `reference_builder`: tao reference/bibliography theo APA, MLA, Chicago, IEEE, BibTeX, plain.
- `source_credibility`: cham tin hieu do tin cay cua URL/nguon.

Moi tool moi co folder rieng trong `starter_v0/tools/<tool_name>/`, co `TOOL.md` va `tool.py`, va da duoc dang ky trong:

```text
starter_v0/tools/__init__.py
starter_v0/artifacts/tools.yaml
```

## 8. Test Nhanh 4 Tool Moi

Tu folder `starter_v0`, co the smoke test registry va `reference_builder`:

```powershell
python -c "from pathlib import Path; from tools import TOOL_FUNCTIONS, load_tool_declarations; names=[t['name'] for t in load_tool_declarations(Path('artifacts/tools.yaml'))]; print({n:(n in names and n in TOOL_FUNCTIONS) for n in ['extract_key_points','compare_sources','reference_builder','source_credibility']}); print(TOOL_FUNCTIONS['reference_builder'](items=[{'title':'Attention Is All You Need','authors':['Vaswani','Shazeer'],'year':'2017','source':'NeurIPS','url':'https://arxiv.org/abs/1706.03762'}], style='apa')['references'][0])"
```

Neu tra ve `True` cho ca 4 tool va in ra reference APA, registry dang dung.

## 9. Bao Cao Va File Nop

Cac file bang chung chinh:

```text
starter_v0/artifacts/REPORT.md
starter_v0/artifacts/version_log.csv
starter_v0/data/eval_group.json
starter_v0/runs/*.json
starter_v0/transcripts/*.transcript.json
```

`REPORT.md` da co:

- Phan A: gioi thieu agent, tool, cau hoi mau, link UI.
- Phan B: version evidence, failure analysis, team eval cases, live chat evidence, bonus evidence.

## 10. Luu Y Khi Lam Tiep

- Khong commit `.env`, API key, token Telegram.
- Neu doi ten tool, phai dong bo `tools.yaml`, `tools/__init__.py`, va eval case.
- Neu chay lai eval bang provider mien phi ma gap quota/rate limit, doi mot luc roi chay lai.
- Link Cloudflare Tunnel la tam thoi; tat tunnel la link mat.
- Khi them tool moi, moi tool can co `TOOL.md`, `tool.py`, dang ky trong `tools/__init__.py`, va khai bao trong `artifacts/tools.yaml`.
