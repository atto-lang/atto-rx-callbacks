# rx-ores-callbacks

Standalone callback-only reactive library for Oreslang.

This variant deliberately uses synchronous callbacks rather than channels,
Future/await, or a pull subscription. It stays separate from `rx-ores` and `rx-oreslang-channels` so
the execution models can be tested and benchmarked independently.

## Source model

`src/rx.ores` is a file/code unit, not an implicit module. Namespace it at the
import site:

```ores
import * as rx_callbacks from './src/rx.ores';
import class Observable from './src/rx.ores';
```

## Callback contract

`subscribe(on_next)` pushes values synchronously. `on_next` returns `true`
to continue and `false` to stop upstream immediately. That boolean is the
callback variant's backpressure/cancellation signal, so this implementation
does not need a channel, Future, scheduler hop, or pull Subscription.

Operators are callback composition: `map`, `filter`, `take`, and
`for_each`. Oreslang does not encode borrowing with pointer-like function
types: callbacks use ordinary types such as `Fnc<A, B>` and
`Fnc<T, bool>`. Calling such a callback gives it temporary read access under
the ownership checker without changing the source type. If code needs a named
borrow that lives beyond one call expression, it uses `rt borrow value`.
Independent copying and read-only shared ownership use `rt copy` and
`rt share`.

This variant intentionally stops at the callback boundary: no `Future<T>`,
`await`, Channel-backed transport, or pull subscription is part of `src/rx.ores`.
Async/Future composition belongs in the separate pull/Future `rx-ores` variant
while we measure the callback data path independently.

## Validation and benchmark

Run the pinned compiler tests with:

```sh
python3 scripts/setup.py
source .work/env.sh
python3 scripts/test.py
```

`bench/pipeline.ores` implements the same repeated logical pipeline used by
the central harness in `rx-ores/bench/benchmark.py`.


## Compiler compatibility

This pointerless callback surface requires the current-main ownership convergence
that makes first-class `Fnc<T,...>` calls temporarily read-borrow non-Copy
arguments and provides compiler-owned `rt borrow/take/copy/share`. The pinned
compiler revision is the exact head validated by the funded exact-tree carrier.

## Compiler compatibility checkpoint (2026-10-06)

The compiler convergence and actor proofs are merged. `compiler.lock` and `compiler-tree.txt` pin the validated implementation. `Observable` is explicitly public for named imports; implementation classes stay private. Tests execute operator composition and owned mutable captures, and require rejection of nested readonly capture mutation.

CI checks out a source-only `compiler-mirror/<revision>` branch in this private repository. Setup verifies its tree identity and clean source state before building; no cross-repository token is required. The historical proposal inventory remains in [docs/compiler-pr-sync.md](docs/compiler-pr-sync.md).

## Repository ownership and migration (2026-11-08)

**AttoLang** is the public language, formerly Oreslang. The repository remains `ores-truffle-oreslang/rx-ores-callbacks` in the legacy org until approved cutover. Preserve supported `.ores` sources, old import paths and package/CLI names; don't infer backend completeness from a README.

- **Belongs here:** safe reactive callback bridges and explicit ownership tests.
- **Excluded:** passing lexical closures through isolated actor channels.
- **Organization split:** [atto-lang](https://github.com/atto-lang) owns portable core/std, compilers, language libraries, test harnesses and demos; [atto-co](https://github.com/atto-co) independently owns cloud hosting, deployment, identity, billing and managed services. Existing `atto-*` repos are not automatically migrated copies or equivalent codebases.
- **Proposed first transfer (not executed):** retain original name, repo ID and Git history in `atto-lang/rx-ores-callbacks` via approved GitHub ownership transfer. No direct source-org → `atto-co` moves are authorized currently; future product carve-outs need separate signoffs.

**Maintainer safety procedure:** coordinate exact source head, owners and rollback in [issue #26](https://github.com/ores-truffle-oreslang/.github/issues/26), then follow private [runbook draft #25](https://github.com/ores-truffle-oreslang/.github/pull/25). Obtain source/target admin and independent security approval; inventory exact SHA/tree, numeric ID, target branch protections/rulesets, access, open PRs, releases/tags, packages, consumers, Actions/runners, secrets, GitHub Apps, webhooks and Pages. Don't clone/mirror private code as transfer workaround. After transfer verify ID/tree/history/controls, update links and rerun exact-head CI; **`steps=[]`/`null` is `NOT_EXECUTED`**, and host-only/source-free checks are not native guest/compiler evidence.
