> **AI agent instructions (organization-wide):** Before working on code, issues, or pull requests, read and follow the [organization `AGENTS.md`](https://github.com/ores-truffle-oreslang/.github/blob/main/AGENTS.md), including its **merge-first stealth-development policy**. Honor any repository-local `AGENTS.md`, explicit holds, and GitHub-enforced rules.

# rx-ores-callbacks

## Oreslang to AttoLang migration (2026-11-18)

**AttoLang** (formerly **Oreslang**) is the current public language identity. This `ores-truffle-oreslang/rx-ores-callbacks` checkout retains old naming. Its AttoLang counterpart for new contributions is [atto-lang/atto-rx-callbacks](https://github.com/atto-lang/atto-rx-callbacks); this link **does not imply an in-place transfer, identical history, migrated issues/PRs or feature parity**. The old source and commands below remain useful as historical checkout documentation, not a guarantee of current language conformance.

**[atto-lang/atto-spec](https://github.com/atto-lang/atto-spec)** is the canonical language specification. The portable library source belongs in [atto-common-source](https://github.com/atto-lang/atto-common-source), shared positive/negative guest tests in [atto-platform-conformance](https://github.com/atto-lang/atto-platform-conformance), and compiler-specific implementations in `atto-source.*`. The language's current proposed direction includes canonical `.atto`, `snake_case`, `borrow!`/`take!`/`share!`/`copy!`/`copy!!`, [implicit borrow defaults](https://github.com/atto-lang/atto-spec/blob/main/language/implicit-argument-borrow-v1.md), [`define const` including permitted `os.read_env`](https://github.com/atto-lang/atto-spec/blob/main/language/file-module-const-v1.md), and [`<<<`/`>>>`/`ashr` shifts vs. `<<`/`>>` streams](https://github.com/atto-lang/atto-spec/blob/main/language/bitwise-and-stream-operators-v1.md). Check individual spec admission status; **a design target is not proof of execution**.

Keep legacy `.ores` fixtures, CLI/package/ABI names, and version-pinned commands where they document code still in this tree. Avoid Python in new AttoLang tooling/tests/CI; Rust support tools are preferred. Only claim cross-backend support with exact SHA/tree, target/toolchain, real executed positive and negative guest tests; report failed, unsupported and not-executed explicitly. Empty-step/host-only CI is not guest conformance.

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
