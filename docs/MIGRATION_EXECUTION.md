# Migration and executed subset — 2026-11-10

Destination `atto-lang/atto-rx-callbacks` was verified **private** before copying private
source. Its existing main `678cd8e22a0b228977bd322d92599c7466046944` and ownership-doc
PR #1 `127160bd9c7f604598b97e3318905176484ab189` are
ancestors of this integration branch. Existing destination README content remains;
source README is preserved as `docs/legacy-readme.md`. No repository was transferred,
deleted or force-pushed. Source main `8ef861478a5c2a593084414888cb9b951b9114cd` (tree
`243eefe8697f1672960a2a84a61c20c21496dad1`) and proposal histories are retained by
ordinary merge parents. Source PRs and origin merge checks remain unchanged.

Reconciled proposals:
- https://github.com/ores-truffle-oreslang/rx-ores-callbacks/pull/9 — `3b3ba8688733ad5917eab622849d77e6ba8ed12e`
- https://github.com/ores-truffle-oreslang/rx-ores-callbacks/pull/13 — `0b950960f6db36db4cae2bf0a87d36ed7b05b1ac`

The pull proposals' duplicate disposal helpers were reconciled into one claimed
cleanup path. Subscription failure now propagates the original exception through
`finally`, rather than converting it to an uncatchable panic via Result.expect.
The fixture/bootstrap security proposals are retained; admission extends to .atto
and rejects duplicate .atto/.ores fixture stems and symlinks before execution.

## Working profile

Substantive stream/app code is guest source. `src/rx.atto` is canonical;
`src/rx.ores` is a byte-identical legacy entry, verified before execution. Keep
imports within either entry for a given object graph: two explicitly distinct
source units are not asserted to share nominal type identity. Existing relative
.ores imports and directory-independent launch scripts continue to execute.

Both models run the same map/filter/skip/take numeric workload and incremental
stdin line app. Pull is synchronous demand-driven; callbacks are synchronous
cooperative push with no Future, Channel, scheduler or invented async engine.
Pull `using` creates an owned Reader for each subscription; callback
`from_producer` invokes a new synchronous producer activation. Producers own their
try/finally resource scope. The CLI borrows process-owned stdin and never closes it.

Java compiler fix https://github.com/ores-truffle-oreslang/oreslang-source.java/pull/2810
is pinned by full commit and tree in compiler.lock/compiler-tree.txt. It corrects
the stdin Option type and explicitly admits System.in only for a capable CLI.
Existing embedding defaults retain empty input. No Rx/application policy is Java.

## Repeatable execution

Use JDK25 and Maven. Setup fetches the exact private compiler using the developer's
existing Git access; no CI secret or cross-organization token is added.

```sh
python3 scripts/setup.py
source .work/env.sh
python3 -m unittest discover -s tests -p 'test_*.py' -q
python3 -m unittest discover -s scripts -p 'test_verify_ci_run.py' -q
python3 scripts/test.py
python3 scripts/test_cli.py
# Real app, from this checkout:
printf '\nalpha\n\nbeta\ngamma\ndelta\n' | java \
  --enable-native-access=ALL-UNNAMED -Dpolyglot.engine.WarnInterpreterOnly=false \
  -cp "$ORES_CLASSPATH" dev.oreslang.launcher.OresMain examples/process-lines.atto
```

Expected app stdout: `beta!\ngamma!\n`, exit 0. test_cli.py also withholds EOF and
a sixth line while waiting for process completion: this verifies incremental
termination without consuming another line. Empty input and short EOF are tested.

`tests/lifecycle.atto` has an explicit golden trace for take(0) (no reads),
five reads for two selected items, independent subscriptions, transform/sink
failure cleanup, and (pull) throwing cleanup followed by repeated cancel/read.
Both models avoid upstream acquisition entirely for take(0): pull does not
open a Reader and callbacks do not invoke their producer.

Host tests use fake Java/Maven only for admission/security; they are labeled
separately from real guest execution. Run receipts record actual commands,
exit status, expected/actual stdout and compiler/application commits/trees.

## Benchmarks

Use `bench/compare.py --peer /absolute/path/to/peer --compiler-root
/absolute/path/to/compiler --warmups 1 --runs 3 --output /outside/checkout/result.json`
with ORES_CLASSPATH from that clean built compiler. Both clean source checkouts
must pin the same exact compiler commit/tree. This executes `bench/common.atto`:
200 pipelines, each map(*2), filter(>4), skip(1), take(2), sum(8,10); expected
stdout `3600\n` and exit 0. Samples rotate process order, assert every checksum,
and report wall time and peak process RSS (bytes on macOS; normalized from KiB
on Linux). Logs preserve commands, Java version, stderr, warmups and all samples.

Measurements include JVM startup, parsing/checking and execution. The local
GraalVM 25 update does not match Truffle 25.3.4.1; the runtime falls back to its interpreter (no version checks are disabled).
These are repeatable interpreter process measurements, not optimized steady-state
throughput, per-operator allocation counts or a cross-backend performance claim.
The historical three-model driver is not this two-model benchmark; channels/tasks
are separate work packages and are neither changed nor certified here.

## Concrete limits and retained compiler repros

- FutureSubscription's mutable receiver cannot cross `await` on this compiler.
  Legacy adapter is isolated in `src/future.ores`, with
  `tests/unsupported/future.ores`. Future suspension/cancel-while-pending is NOT
  supported or certified by the synchronous pull milestone.
- Imported subclass methods fail eager callable-slot linking (unresolved imported
  parent); pull `tests/unsupported/dispose_once.ores` retains that minimal use.
  The executed lifecycle test proves the same cleanup properties by composition.
- `ores.std/testing` currently returns a Future where its TestOutcome is expected;
  native framework tests remain under `tests/unsupported`, not counted as passes.
  The same behavior contracts are exercised by golden guest programs.
- A named synchronous callback in a source unit with imports can be routed through
  a scheduler task, then escape as OresFuture via the generic Invokable path.
  `examples/io.atto` and test producer helpers contain no imports, keeping their
  primitive I/O/callback execution synchronous. This is a module-layout workaround,
  not a new async engine. General callbacks that suspend remain unsupported.
- Local instance-method extraction is rejected while imported class method
  callbacks execute; benchmark sink support uses the executed imported-class path.
  This is not a full callable parity claim.
- Standalone --check lacks some linked import/ownership facts. The guest runner
  executes the real linked compiler/checker before evaluation and compares output;
  it does not replace execution with static acceptance or skip ownership checks.

Other backends, Native Image, actor isolation/races, full scheduler behavior and
formal security certification are NOT EXECUTED for this workload. Source branches
remain drafts and origin merge/review gates remain applicable.

## CI boundaries

Destination workflows run source-free host contracts with their own GITHUB_TOKEN
and contents:read. They do not fetch a sibling private compiler or use legacy
ORES_COMPILER_READ_TOKEN. Genuine guest evidence here is local. No budget-fallback
mirror was needed; standing user authorization would apply if later required.
Historical documents claiming no fallback authorization are dated records, not
current permission rules. Zero-step source-org Actions failures prove neither
language success nor failure. No release, deployment or merge is authorized here.
