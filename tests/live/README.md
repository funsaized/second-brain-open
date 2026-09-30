# Live harnesses

Opt-in evidence harnesses, kept apart from the offline suite in `tests/`. None
of them runs under `python3 -m unittest discover -s tests`; each needs OpenCode
and states what it needs in its docstring.

| File | What it does | Model calls |
|---|---|---|
| `runtime_read_probe.py` | Read and tool boundaries for a deny-by-default role, in Bubblewrap with a fake provider | None |
| `runtime_roles_probe.py` | Installs the worker roles and skills in an isolated profile and checks they load and refuse | None |
| `runtime_search_probe.py` | What grep and glob can reach from a staged copy | None |
| `researcher_eval.py` | Scores the researcher's answers on a staged copy of a wiki | Yes, with `--live` |
| `semantic_probe.py`, `ingest_rehearsal.py` | Early driver-applied semantic rehearsals | Yes, with `--live` |
| `native_chat_proposal.py`, `native_chat_handoff.py`, `native_acceptance_trials.py` | The recorded native acceptance trials for the selected chat handoff | Yes, with `--live` |

The native-trial drivers are frozen evidence: their scenario-specific modes
replay recorded trials and get no new features. New operator behaviour is
tested through `scripts/sb_operator.py` and its offline tests. Results are in
[the trial report](../../docs/native-acceptance-trials.md).
