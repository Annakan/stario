# Vendored stario — provenance & divergence record

Upstream: `github.com/bobowski/stario` release **4.1.0**, vendored (forked) into
`packages/stario` for rAIvisor. This file is the started contract for M06's
`VENDORED.md` requirement (plan v2 §2): every patch applied on top of upstream,
with rationale and reversal hazard. **A refresh of the fork MUST re-apply or
reconsider every item below; silently importing upstream loses Python 3.13
compatibility.**

Target runtime: Python **3.13.x** (project pin `requires-python = <3.14`;
PaddlePaddle has no 3.14 wheel). Upstream stario 4.1.0 declares
`requires-python >= 3.13` but its **code and tests** were written against
3.14-only features. Every divergence below is a 3.13-compat fix that upstream
does not need once 3.14 is the floor.

## Declared dependencies for the 3.13 fallbacks (`pyproject.toml`)

```toml
"backports.zstd; python_version < '3.14'",
"uuid-utils; python_version < '3.14'",
```

Both markers deactivate on 3.14+, where the stdlib fallbacks take over. Before
these were declared directly, `uuid-utils` resolved only transitively through
litellm→pathway — pinning was required so the fork is self-contained.

## Patch inventory

| # | Divergence | Files | Why it exists |
|---|------------|-------|---------------|
| 1 | **zstd via backport on 3.13** | `src/stario/http/compression.py`, `src/stario/testing/encode.py` | Upstream does `from compression import zstd` — PEP 784 stdlib, 3.14-only. We try stdlib first, fall back to `backports.zstd` on <3.14. Same `ZstdCompressor`/`CompressionParameter` API. |
| 2 | **UUID7 shim** | new `src/stario/_uuid7.py`; rewired `telemetry/buffered.py`, `telemetry/tty.py`, `testing/encode.py`, `testing/tracer.py`, `tests/test_telemetry_tty.py` | Upstream imports `uuid.uuid7` (3.14-only). The shim tries stdlib then `uuid_utils.uuid7` (returns real `uuid.UUID` v7). All call sites import from the shim, never from `uuid`. |
| 3 | **Future-annotations across the fork** | 75 modules under `src/stario/` + 44 under `tests/` | Upstream relies on 3.14-era relaxed annotation evaluation (forward refs, subscriptable builtins like `memoryview[Any]`). Without `from __future__ import annotations`, those evaluate eagerly on 3.13 and raise `NameError`/`TypeError` at import. |
| 4 | **Parenthesized except** | `src/stario/_terminal.py`, `src/stario/http/protocol.py`, `src/stario/http/server.py`, `src/stario/telemetry/tty.py`, `tests/test_server.py` | Upstream uses PEP 758 `except A, B:` (3.14+). On 3.13 that is a `SyntaxError`; rewritten to `except (A, B):`. |
| 5 | **`BakeSlot.__hash__` guard** | `src/stario/markup/slots.py` | **Semantic fix, not just syntax.** `BakeSlot` defines `__eq__` (loud `StarioError` misuse guard) but no `__hash__` → Python sets `__hash__ = None`, so hashing a slot as a dict key leaked a bare `TypeError: unhashable type` instead of the intended `StarioError`. Upstream test `test_slot_as_attribute_name_rejected` expects the guarded error. On 3.14 upstream the same bug is masked by a different code path; on our run it is the live failure. Guard added so misuse always surfaces as the designed `StarioError`. |

## Proprietary / non-divergent assets

CSS/JS bundles pinned for the M06 UI live under `src/raivisor/ui/static/` and
follow the same pattern: pinned by version + checksum, refreshing via a
documented `curl` recipe — that half of "VENDORED" is tracked in the UI
milestone's own `VENDORED.md`, not here.

## Verification gates (must all pass after any refresh)

1. `uv sync` resolves; `python -c "import stario"` loads this package.
2. `python -c "from stario.testing import TestClient"` — exercises the zstd
   and uuid7 shims (they sit on that import path).
3. `pytest packages/stario/tests -q` → 652 passed (current green baseline).
4. `python -m compileall -q packages/stario/src` clean.
5. Root `pytest tests/ -q` (project suite) green — regression guard.
