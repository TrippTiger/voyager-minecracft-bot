import json
import os
from datetime import datetime


_log_dir = None
_session_id = None


def init_logger(log_dir="experiment_logs"):
    global _log_dir, _session_id
    _log_dir = log_dir
    _session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(os.path.join(_log_dir, _session_id), exist_ok=True)
    print(f"\033[36mExperiment logs: {_log_dir}/{_session_id}/\033[0m")


def log_llm_exchange(agent_name, messages, response, extra=None):
    if _log_dir is None:
        return
    entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "messages": [
            {"role": m.__class__.__name__.replace("Message", "").lower(), "content": m.content}
            for m in messages
        ],
        "response": response,
    }
    if extra:
        entry.update(extra)
    fname = f"{agent_name}_{datetime.now().strftime('%H%M%S_%f')}.json"
    path = os.path.join(_log_dir, _session_id, fname)
    with open(path, "w") as f:
        json.dump(entry, f, indent=2)


class LLMLoggerMixin:
    def _log_llm_exchange(self, agent_name, messages, response, extra=None):
        log_llm_exchange(agent_name, messages, response, extra)
