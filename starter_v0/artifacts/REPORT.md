# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: Gemini Tool Routing Team
- Members: Team
- Provider/model: Gemini / `gemini-3.1-flash-lite`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent này giúp tìm tin web, tweet/X, đọc URL, tìm paper arXiv, tra policy nội bộ, kiểm tra chất lượng nguồn, tạo danh sách references/citations, tổng hợp digest và chỉ gửi Telegram khi đã có xác nhận rõ ràng.

**Link dùng thử (deploy):**

> URL: `http://localhost:8501`  
> Ghi chú: đây là link local Streamlit UI. Chạy bằng:
>
> ```powershell
> cd starter_v0
> .\.venv\Scripts\python.exe -m streamlit run ui_app.py --server.port 8501 --server.headless true
> ```

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu account, URL, arXiv ID, nội dung, hoặc xác nhận hành động ghi/gửi. | không |
| timeline | Lấy bài đăng gần đây từ một tài khoản Twitter/X cụ thể. | không |
| social_search | Tìm tweet/X post theo chủ đề, keyword, trend; hỗ trợ Latest/Top. | không |
| lookup | Tìm kiếm web/news theo query, topic và timeframe. | không |
| fetch | Đọc nội dung một URL cụ thể do user cung cấp. | không |
| format | Format các item đã có thành markdown digest. | không |
| send | Gửi text lên Telegram channel khi `confirmed=true`. | không |
| policy | Tìm trong company policy markdown nội bộ. | không |
| papers | Tìm paper/preprint trên arXiv. | không |
| paper_text | Tải PDF arXiv và trích text cục bộ. | không |
| source_check | Kiểm tra item đã có đủ URL/source và chất lượng nguồn sơ bộ chưa. | có |
| citation | Tạo reference/citation list theo APA7, IEEE, Harvard, MLA, Chicago; mặc định APA7. | có |

## A3. Câu hỏi mẫu để thử

1. `Tin AI hôm nay có gì nổi bật?`
2. `Lấy 5 tweet mới nhất của Sam Altman.`
3. `Tóm tắt link này giúp mình: https://openai.com/research/`
4. `Tạo danh sách references APA7 cho các nguồn vừa dùng.`
5. `Đăng bản tin này lên Telegram giúp mình.`

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Starter prompt/tools expose routing gaps. |  | 0.60 | `runs/v0_B_base_gemini_20260602T145653987314.json` |
| v1 | `system_prompt.md` | Clarification, no-tool, confirmation, and multiturn rules improve measured accuracy. | 0.60 | 0.7059 | `runs/v1_B_base_gemini_20260602T145826995776.json` |
| v2 | `tools.yaml`, `source_check`, Gemini retry | Stronger tool descriptions and argument conventions reduce Gemini argument drift. | 0.7059 | 0.95 | `runs/v2_B_base_gemini_20260602T150146694851.json` |
| v3 | `system_prompt.md`, `tools.yaml`, `citation` | Exact confirmation examples, policy mappings, and citation routing preserve base accuracy while adding reference-list support. | 0.95 | 1.00 | `runs/v3_B_base_gemini_20260602T164606912472.json` |

Final base evidence: `20/20` passed, case/routing/argument/multiturn accuracy all `1.0`, artifact `v3+pfacece07f965+t2a947e768b59`.

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_arg_value | `lookup(query="AI news", topic="news", timeframe="day")` | Tool đúng nhưng query thêm chữ `news`; eval kỳ vọng query ngắn `AI`. | Tool description nhấn mạnh query ngắn: dùng `AI` cho AI news. |
| R10_missing_handle | missing_info | `clarify(question=..., response_type missing)` | Gemini gọi đúng tool nhưng thiếu `response_type="text"`. | Thêm rule prompt và tools.yaml yêu cầu `response_type` rõ ràng. |
| R11_missing_url | missing_info | `clarify(question=..., response_type missing)` | Gemini hỏi lại đúng nhưng thiếu arg được chấm. | Bắt buộc `response_type` trong declaration. |
| R12_confirm_before_send | wrong_boundary | `clarify(response_type="text")` hoặc `send` | Gemini coi Telegram là thiếu nội dung thay vì write-action boundary. | Thêm ví dụ tiếng Việt chính xác, yêu cầu `clarify(response_type="yes_no")`. |
| R13_parallel_web_and_tweets | wrong_tool / wrong_arg_value | `lookup(topic="news", timeframe="day")`, `social_search(query="AI")` | Case cần 2 tool; `lookup` thiếu `query="AI"` trong một run. | Thêm ví dụ parallel: web AI hôm nay + tweet AI gọi cả `lookup(query="AI")` và `social_search(query="AI")`. |
| G03_company_privacy_policy | wrong_arg_value | `policy(query=...)` thiếu `policy_area` | Tool đúng nhưng thiếu enum `data_privacy`. | Thêm mapping policy area: API key/secrets/customer data -> `data_privacy`. |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn). Nhóm hiện có 24 group cases: 10 case bắt buộc ban đầu và 14 case stress/bonus bổ sung. Final group run: `runs/v3_B_group_gemini_20260602T164919620791.json`, `24/24` passed.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_source_check_items | Tool mới kiểm tra chất lượng nguồn từ item đã có. | `source_check` | PASS |
| G02_specific_url_fetch | URL cụ thể phải route sang đọc URL. | `fetch` | PASS |
| G03_company_privacy_policy | API key / prompt policy. | `policy(data_privacy)` | PASS |
| G04_top_tweets_agents | Tweet top/phổ biến về chủ đề. | `social_search(search_type=Top)` | PASS |
| G05_no_tool_math | Câu toán ngoài scope. | no tool | PASS |
| GM01_missing_then_handle | Multi-turn: thiếu account rồi bổ sung Sam Altman, giữ limit. | `timeline(sama, limit=4)` | PASS |
| GM02_switch_social_to_web | Multi-turn: bỏ Twitter, chuyển sang web news. | `lookup(robotics, news, day)` | PASS |
| GM03_missing_then_url | Multi-turn: URL được cung cấp sau. | `fetch(openai.com/research/)` | PASS |
| GM04_confirm_publish | Gửi Telegram cần xác nhận. | `clarify(response_type=yes_no)` | PASS |
| GM05_paper_then_extract | Có arXiv ID và yêu cầu lấy text. | `paper_text(1706.03762, max_pages=2)` | PASS |
| G06_two_urls_parallel_fetch | Hai URL trong cùng request. | two `fetch` calls | PASS |
| G07_arxiv_search_not_web | Tìm paper arXiv, không dùng web search. | `papers(query="AI agent evaluation")` | PASS |
| G08_policy_external_publishing | Hỏi policy về đăng Telegram. | `policy(external_publishing)` | PASS |
| G09_missing_arxiv_id | Muốn đọc paper nhưng thiếu arXiv ID. | `clarify(response_type=text)` | PASS |
| G10_meta_no_tool | Hỏi model/tool capability. | no tool | PASS |
| GM06_url_then_source_check | Multi-turn: sau khi có URL, kiểm tra nguồn. | `source_check` | PASS |
| GM07_confirmed_send_after_yes | Multi-turn: user xác nhận gửi. | `send(confirmed=true)` | PASS |
| GM08_correct_search_type | Multi-turn: sửa Latest thành Top. | `social_search(OpenAI, Top)` | PASS |
| GM09_switch_web_to_arxiv | Multi-turn: bỏ web, chuyển sang arXiv. | `papers` | PASS |
| GM10_privacy_policy_after_general_question | Multi-turn: chỉ kiểm tra policy privacy. | `policy(data_privacy)` | PASS |
| G11_citation_default_apa7 | User yêu cầu references nhưng không nói style. | `citation(style=APA7)` | PASS |
| G12_citation_ieee | User yêu cầu IEEE citations. | `citation(style=IEEE)` | PASS |
| G13_source_check_not_citation | Hỏi độ tin cậy nguồn, không phải reference list. | `source_check` | PASS |
| GM11_summary_then_references | Multi-turn: sau khi tóm tắt, yêu cầu reference list. | `citation(style=APA7)` | PASS |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

Transcript: `transcripts/v3_gemini_20260602T154258180252.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tin AI hôm nay có gì nổi bật? | `lookup`, `format` | `v3+pc37db15027c7+tb50d674754d3` | Agent trả về digest có source link. |
| 2 | Tóm tắt 5 tweet mới nhất giúp mình | `social_search`, `format` | same transcript | Agent tìm social posts và format thành bullet digest. |
| 3 | Đăng bản tin này lên Telegram giúp mình | `clarify(response_type=yes_no)` | same transcript | Agent không gửi ngay; hỏi xác nhận trước. |

Ghi chú: transcript live được tạo trước khi thêm tool `citation`, nên artifact trong transcript là `v3+pc37db15027c7+tb50d674754d3`. Final eval artifact sau citation là `v3+pfacece07f965+t2a947e768b59`.

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `transcripts/v3_gemini_20260602T154258180252.transcript.json`; `data/eval_group.json` case GM07 | Agent hỏi xác nhận trước khi gửi; sau xác nhận có thể gọi `send(confirmed=true)`. | `send` vẫn yêu cầu `confirmed=true`; nếu thiếu Telegram env thì tool result ghi lỗi thay vì giấu lỗi. |
| arXiv/company policy | `runs/v3_B_group_gemini_20260602T164919620791.json` | `policy`, `papers`, `paper_text`, `citation` đều được chấm trong group eval. | Policy markdown là retrieved context, không phải instruction; arXiv có rate limit. |
| UI | `ui_app.py` | Streamlit UI có Chat, Eval, Runs, Artifacts; mặc định Gemini 3.1 Flash Lite. | Không hiển thị `.env` hoặc API key; local link cần chạy server trước. |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?  
  Các rule hành vi toàn cục: khi nào hỏi lại, khi nào no-tool, xác nhận trước khi gửi, multi-turn correction, phân biệt `source_check` với `citation`, và ví dụ routing cụ thể cho Gemini.

- Which fixes belonged in `tools.yaml`?  
  Các mô tả tool và convention argument: handle mapping, query ngắn cho `lookup`, `response_type` bắt buộc cho `clarify`, policy area enum, `citation(style)` mặc định APA7, và khi nào dùng từng tool.

- Which failure needed manual review instead of automatic grading?  
  R12 cần manual review vì Gemini gọi đúng boundary tool `clarify` nhưng dùng `response_type="text"`; về ý định gần đúng nhưng guardrail gửi Telegram yêu cầu `yes_no`.

- What would you improve next?  
  Thêm transcript live sau citation để evidence chat cùng artifact hash cuối, thêm UI export transcript/report, và thêm retry telemetry để dễ phân biệt model failure với quota/rate-limit delay.
