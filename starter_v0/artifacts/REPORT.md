# Day 04 Lab v2 Report - Research Agent

## Team

- Team: Nhóm 5, Zone 9
- Members: 
+ Lê Đàm Quân 2A202600930
+ Nguyễn Tiến Đạt 2A202600595
+ Trần Nguyễn Đăng Khoa 2A202600922
+ Trần Hoàng Nam 2A202600870
- Provider/model: Gemini / `gemini-3.1-flash-lite`

## Final Metrics

- Final version: `v3`
- Final artifact_version: `v3+pc37db15027c7+tb50d674754d3`
- Best base run file: `runs/v3_B_base_gemini_20260602T151429269177.json`
- Base case accuracy: `1.0`
- Base tool routing accuracy: `1.0`
- Base argument accuracy: `1.0`
- Group eval run file: `runs/v3_B_group_gemini_20260602T151301714070.json`
- Group eval accuracy: `1.0`
- Chat transcript file: `transcripts/v3_gemini_20260602T154258180252.transcript.json`

## A1. Agent này làm được gì

Research agent: tìm tin web/X, đọc URL, tìm paper arXiv, hỏi lại khi thiếu thông tin, tổng hợp digest, rút ý chính / so sánh nguồn / tạo tham chiếu / chấm độ tin cậy nguồn, và gửi Telegram khi user xác nhận.

**Link dùng thử (deploy):**

> https://movie-lace-pork-oriented.trycloudflare.com

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại user (text / yes_no / choice) | không |
| timeline | Tweet gần đây theo `screenname` | không |
| social_search | Tìm tweet theo từ khóa (Latest/Top) | không |
| lookup | Tìm web/news (`topic`, `timeframe`) | không |
| fetch | Đọc nội dung một URL | không |
| format | Format items thành markdown digest | không |
| send | Gửi Telegram (cần `confirmed`) | không |
| policy | Tìm policy nội bộ markdown | không |
| papers | Tìm paper arXiv | không |
| paper_text | Tải/extract text PDF arXiv | không |
| extract_key_points | Rút ý chính từ text/items đã có | **có** |
| compare_sources | So sánh ≥2 nguồn đã mô tả | **có** |
| reference_builder | Tạo bibliography (APA/MLA/IEEE/…) | **có** |
| source_credibility | Chấm tín hiệu độ tin cậy URL/nguồn | **có** |

## A3. Câu hỏi mẫu để thử

1. Không cần tìm web — rút 5 ý chính từ đoạn text user dán sẵn (`extract_key_points`).
2. Chấm độ tin cậy: `https://arxiv.org/abs/2401.00001` (`source_credibility`).
3. So sánh hai nguồn user liệt kê title/summary/URL (`compare_sources`).
4. Tạo danh mục tham chiếu APA từ metadata paper (`reference_builder`).
5. Tin AI hôm nay + bàn trên Twitter (có thể `lookup` + `social_search`).

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Nguồn: `artifacts/version_log.csv` và `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Measure behavior before prompt/tool changes | — | 0.60 | `runs/v0_B_base_gemini_20260602T143922624263.json` |
| v1 | system_prompt.md | clarify + no tools for out-of-scope → failures drop | 0.60 | 0.95 | `runs/v1_B_base_gemini_20260602T145750394332.json` |
| v2 | system_prompt.md; tools.yaml; data/eval_group.json | Local-tool routing without chaining lookup/fetch → G01–G10 pass | 0.90 | **1.00 (group)** | `runs/v2_B_group_gemini_20260602T155229890587.json` |
| v3 | system_prompt.md | yes_no before send + Karpathy handle → R12/M03 pass | 0.90 | **1.00 (base)** | `runs/v3_B_base_gemini_20260602T150620645041.json` |

Ghi chú:

- **v2 base** (send yes_no, accuracy 0.90): `runs/v2_B_base_gemini_20260602T150406425414.json` — không ghi trong `version_log` dòng v2 (dòng v2 ghi **group eval**).
- **v2 group**: 10/10 trên `data/eval_group.json`, `case_accuracy=1.0`.

## B2. Failure Analysis

Lấy từ `results[*].result.failures` — chủ yếu **v0 baseline** (v3 base và v2 group đều 100%, không fail).

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10_missing_handle | missing_info | `timeline(screenname=sama)` | Thiếu handle nhưng model đoán `sama` | v1: bắt `clarify` khi thiếu account |
| R11_missing_url | missing_info | *(không gọi clarify)* | Thiếu URL trước `fetch` | v1: hỏi URL trước khi `fetch` |
| R12_confirm_before_send | wrong_boundary | `send` hoặc tool khác, không `clarify` yes_no | Gửi/đăng không xác nhận trước | v2/v3: `clarify` yes_no trước send |
| R08_out_of_scope | out_of_scope | Gọi tool research | Câu ngoài phạm vi vẫn gọi tool | v1: refuse / no tool |
| R09_no_tool_capability | unnecessary_tool | Gọi tool | Câu hỏi khả năng agent không cần tool | v1: no tool |
| R03_web_news_routing | wrong_tool / wrong_arg_value | `lookup` sai `topic`/`timeframe` | Tin “hôm nay” không map `news`+`day` | Prompt routing lookup args |

**Run cuối:** `v3` base và `v2` group — không còn case FAIL trong log.

## B3. Team Eval Cases

10 case trong `data/eval_group.json` (5 single-turn + 5 multi-turn). Kết quả: `runs/v2_B_group_gemini_20260602T155229890587.json`.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_extract_key_points_text | Text đã dán → rút 5 ý, không lookup/fetch | `extract_key_points`, max_points=5 | PASS |
| G02_source_credibility_url | Chấm tin cậy arXiv URL | `source_credibility` + url | PASS |
| G03_compare_sources_inline | Hai nguồn inline → so sánh | `compare_sources` | PASS |
| G04_reference_builder_apa | Bibliography APA từ metadata | `reference_builder`, style=apa | PASS |
| G05_extract_max_points_arg | Rút đúng 3 ý | `extract_key_points`, max_points=3 | PASS |
| G06_multiturn_compare_sources | 3 turns carry 2 nguồn → compare | `compare_sources` | PASS |
| G07_multiturn_credibility_url | 3 turns carry URL Nature | `source_credibility` | PASS |
| G08_multiturn_extract_limit | Carry text + max_points=2 | `extract_key_points`, max_points=2 | PASS |
| G09_multiturn_reference_ieee | Carry 2 paper → IEEE refs | `reference_builder`, style=ieee | PASS |
| G10_multiturn_switch_to_credibility | Bỏ timeline → credibility OpenAI research URL | `source_credibility` | PASS |

**Tổng:** 10/10 — `case_accuracy=1.0`, `multiturn_accuracy=1.0`.

## B4. Live Chat Evidence

> *(Chưa có — chạy `python chat.py --provider gemini --version v3` và lưu `transcripts/*.transcript.json`.)*

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| — | — | — | — | — |

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `runs/v3_B_base_gemini_...` (R12 PASS) | yes_no `clarify` trước send | Chỉ gửi khi user confirm |
| arXiv/company policy | tools `papers`, `policy` trong `tools.yaml` | Có trong declaration | Cần API/key theo TOOL-SETUP |
| UI | — | Chưa deploy | Cần Streamlit/Vercel + tunnel |

## Reflection

- **`system_prompt.md`:** clarify khi thiếu handle/URL; yes_no trước send; map tên → handle; routing lookup/fetch/social; đoạn **local tools** (một tool, không chain) cho 4 tool nhóm.
- **`tools.yaml`:** Khai báo 4 formatter/local tools; mô tả ngắn giúp model chọn đúng tên tool.
- **Manual review:** Một số case `compare_sources` / `items` — eval chỉ chấm subset args; chất lượng output so sánh cần đọc `tool_results` tay khi demo.
- **Tiếp theo:** Live chat transcript (B4), UI public link (A), có thể re-run `eval_base` với prompt hiện tại để xác nhận không regress.
