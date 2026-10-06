# rx-ores-callbacks

Standalone callback-only reactive library for Oreslang.

This variant deliberately uses synchronous callbacks rather than channels or
Future/await. It stays separate from `rx-ores` and `rx-oreslang-channels` so
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
`for_each`. The map callback receives a borrow (`Fnc<&A, B>`) so the push
pipeline does not imply ownership transfer merely to inspect an element.

This variant intentionally does **not** adapt asynchronous producers yet. Doing
so by invoking guest callbacks from an arbitrary completion thread would violate
the scheduler-domain contract. Async callback delivery should only be added once
it has an explicit Ores scheduler/actor continuation boundary.

## Validation and benchmark

Run the pinned compiler tests with:

```sh
python3 scripts/setup.py
source .work/env.sh
python3 scripts/test.py
```

`bench/pipeline.ores` implements the same repeated logical pipeline used by
the central harness in `rx-ores/bench/benchmark.py`.
