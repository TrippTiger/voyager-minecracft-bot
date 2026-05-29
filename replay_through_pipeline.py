"""
Replay logged Voyager prompts through a different pipeline and compare results.

Usage:
    python replay_through_pipeline.py --log-dir ckpt/experiment_logs/<session_id> --agent action
    python replay_through_pipeline.py --log-dir ckpt/experiment_logs/<session_id> --agent curriculum
    python replay_through_pipeline.py --log-dir ckpt/experiment_logs/<session_id> --agent all

Output: results saved to ckpt/experiment_logs/<session_id>/replay_results.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from openai import OpenAI


def load_logs(log_dir, agent_filter=None):
    entries = []
    for fname in sorted(os.listdir(log_dir)):
        if not fname.endswith(".json") or fname == "replay_results.json":
            continue
        if agent_filter and agent_filter != "all" and not fname.startswith(agent_filter):
            continue
        with open(os.path.join(log_dir, fname)) as f:
            entry = json.load(f)
            entry["_file"] = fname
            entries.append(entry)
    return entries


def call_your_pipeline(messages, model="gpt-4o-mini"):
    """
    Replace this function body with your ATLAS pipeline call.
    Currently just calls OpenAI directly — swap in your pipeline here.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    openai_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
    # Fix role names: "system" messages come from SystemMessage -> "system" role is correct,
    # but LangChain uses "human" not "user"
    for m in openai_messages:
        if m["role"] == "human":
            m["role"] = "user"
        elif m["role"] == "ai":
            m["role"] = "assistant"
    response = client.chat.completions.create(model=model, messages=openai_messages)
    return response.choices[0].message.content


def compare(original, replayed):
    print("\n" + "=" * 60)
    print(f"ORIGINAL ({len(original)} chars):")
    print(original[:800] + ("..." if len(original) > 800 else ""))
    print("\nREPLAYED ({} chars):".format(len(replayed)))
    print(replayed[:800] + ("..." if len(replayed) > 800 else ""))
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-dir", required=True, help="Path to session log directory")
    parser.add_argument("--agent", default="all", choices=["action", "curriculum", "critic", "all"])
    parser.add_argument("--model", default="gpt-4o-mini", help="Model to use for replay")
    parser.add_argument("--limit", type=int, default=5, help="Max number of entries to replay")
    args = parser.parse_args()

    entries = load_logs(args.log_dir, args.agent)
    print(f"Found {len(entries)} log entries for agent='{args.agent}'")

    results = []
    for i, entry in enumerate(entries[:args.limit]):
        print(f"\n[{i+1}/{min(len(entries), args.limit)}] Replaying {entry['_file']} ...")
        try:
            replayed = call_your_pipeline(entry["messages"], model=args.model)
            compare(entry["response"], replayed)
            results.append({
                "file": entry["_file"],
                "agent": entry["agent"],
                "timestamp": entry["timestamp"],
                "original_response": entry["response"],
                "replayed_response": replayed,
                "model_used": args.model,
                "replayed_at": datetime.now().isoformat(),
            })
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"file": entry["_file"], "error": str(e)})

    out_path = os.path.join(args.log_dir, "replay_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
