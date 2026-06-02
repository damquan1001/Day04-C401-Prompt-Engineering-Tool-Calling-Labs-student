from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import streamlit as st

from chat import execute_tool_call, run_model_tool_loop
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
RUNS_DIR = ROOT / "runs"
DATA_DIR = ROOT / "data"
DEFAULT_MODEL = "gemini-3.1-flash-lite"


st.set_page_config(page_title="Research Agent Lab", layout="wide")
load_lab_env(ROOT)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=900,
        check=False,
    )


def official_runs() -> list[Path]:
    return sorted(RUNS_DIR.glob("*_gemini_*.json"), key=lambda path: path.stat().st_mtime, reverse=True)


def run_summary_table(path: Path) -> None:
    payload = read_json(path)
    summary = payload.get("summary", {})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Case Accuracy", summary.get("case_accuracy", 0))
    c2.metric("Routing", summary.get("tool_routing_accuracy", 0))
    c3.metric("Arguments", summary.get("argument_accuracy", 0))
    c4.metric("Measured", summary.get("measured_cases", 0))
    st.caption(f"{payload.get('provider')} / {payload.get('model')} / {payload.get('artifact_version')}")

    rows = []
    for item in payload.get("results", []):
        result = item.get("result", {})
        rows.append({
            "case": item.get("id"),
            "passed": result.get("passed"),
            "mismatch": result.get("observed_mismatch"),
            "expected": item.get("expect"),
            "actual": result.get("actual_tool_calls"),
            "failures": "; ".join(result.get("failures") or []),
        })
    st.dataframe(rows, width="stretch", hide_index=True)


with st.sidebar:
    st.title("Research Agent")
    provider_name = st.selectbox("Provider", ["gemini"], index=0)
    model = st.text_input("Model", DEFAULT_MODEL)
    version = st.text_input("Version", "v3")
    prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    artifact_version = build_artifact_version(version, prompt_path, tools_path)
    st.caption(artifact_version.artifact_version)
    st.caption(f"Prompt {artifact_version.prompt_hash[:12]}")
    st.caption(f"Tools {artifact_version.tools_hash[:12]}")


chat_tab, eval_tab, runs_tab, artifacts_tab = st.tabs(["Chat", "Eval", "Runs", "Artifacts"])

with chat_tab:
    st.subheader("Live Chat")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "tool_events" not in st.session_state:
        st.session_state.tool_events = []

    user_text = st.chat_input("Ask for research, tweets, policy, papers, or source checks")
    if user_text:
        st.session_state.messages.append({"role": "user", "content": user_text})
        system_prompt = prompt_path.read_text(encoding="utf-8")
        tools = to_openai_tools(load_tool_declarations(tools_path))
        provider = make_provider(provider_name)
        messages = [{"role": "system", "content": system_prompt}, *st.session_state.messages[-8:]]
        with st.spinner("Calling model and tools..."):
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=tools,
                model=model,
                max_tool_rounds=4,
            )
        st.session_state.messages.append({"role": "assistant", "content": result["assistant_text"]})
        st.session_state.tool_events.extend(result.get("tool_events", []))

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if st.session_state.tool_events:
        with st.expander("Tool Events", expanded=True):
            st.json(st.session_state.tool_events)

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.tool_events = []
        st.rerun()

with eval_tab:
    st.subheader("Run Eval")
    suite = st.segmented_control("Suite", ["base", "group"], default="base")
    eval_file = DATA_DIR / ("eval_base.json" if suite == "base" else "eval_group.json")
    if st.button("Run Gemini Eval"):
        args = [
            sys.executable,
            "run_eval.py",
            "--provider",
            provider_name,
            "--model",
            model,
            "--version",
            version,
            "--suite",
            suite,
            "--eval-cases",
            str(eval_file),
        ]
        with st.spinner("Running eval..."):
            completed = run_command(args)
        st.code(completed.stdout or completed.stderr)
        if completed.returncode != 0:
            st.error("Eval failed")
    if st.button("Parse Official Gemini Runs"):
        files = [str(path) for path in official_runs()]
        output = ROOT / "analysis" / ("group_runs.csv" if suite == "group" else "base_runs.csv")
        completed = run_command([sys.executable, "scripts/parse_runs.py", *files, "--output", str(output)])
        st.code(completed.stdout or completed.stderr)

with runs_tab:
    st.subheader("Run Inspector")
    runs = official_runs()
    if not runs:
        st.info("No Gemini run JSON files found.")
    else:
        selected = st.selectbox("Run", runs, format_func=lambda path: path.name)
        run_summary_table(selected)

with artifacts_tab:
    st.subheader("Artifacts")
    artifact_choice = st.selectbox(
        "Artifact",
        [
            ARTIFACTS_DIR / "system_prompt.md",
            ARTIFACTS_DIR / "tools.yaml",
            ARTIFACTS_DIR / "version_log.csv",
            ARTIFACTS_DIR / "REPORT.md",
            DATA_DIR / "eval_group.json",
        ],
        format_func=lambda path: str(path.relative_to(ROOT)),
    )
    st.code(artifact_choice.read_text(encoding="utf-8"), language="markdown" if artifact_choice.suffix == ".md" else "text")

    with st.expander("Manual Tool Smoke Test"):
        sample_items = [{"title": "OpenAI research", "url": "https://openai.com/research/", "source": "openai.com"}]
        if st.button("Run source_check"):
            st.json(execute_tool_call(type("Call", (), {"name": "source_check", "args": {"items": sample_items}})()))
