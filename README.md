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

The synchronous Observable path remains callback-only, but asynchronous callback
composition is now available through the native Ores `Future<T>` surface:

```ores
val Future<int> mapped = rx_callbacks.future_map(source, transform);
val Future<string> chained = rx_callbacks.future_compose(mapped, next_async);
val Future<string> observed = rx_callbacks.future_on_success(chained, observer);
```

`future_map`, `future_compose` / `future_flat_map`, and
`future_on_success` delegate to Oreslang's native Future combinators. Guest
callbacks execute as Ores scheduler/actor turns; producer completion threads only
settle Futures and never execute the guest callback inline. This keeps the
callback variant compatible with asynchronous sources without introducing a
Java `CompletableFuture` callback surface or a Channel-backed data path.

## Validation and benchmark

Run the pinned compiler tests with:

```sh
python3 scripts/setup.py
source .work/env.sh
python3 scripts/test.py
```

`bench/pipeline.ores` implements the same repeated logical pipeline used by
the central harness in `rx-ores/bench/benchmark.py`.
