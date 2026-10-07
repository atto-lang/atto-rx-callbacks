# Callback RX ownership and binding contract

Follow [compiler PR #411](https://github.com/ores-truffle-oreslang/oreslang-source.java/pull/411). Four independent modes:

- `const x`: fixed binding, read-only access to referent;
- `val x`: fixed binding, mutable referent (`const mut x` alias);
- `let x`: rebindable binding, read-only referent;
- `let mut x`: rebindable binding, mutable referent.

A `val Fnc<...> callback` stores an immutable binding to a callable; this does not automatically authorize arbitrary mutation of its captured state. Closures must carry checked capture effects/ownership, including when called by `subscribe`, `map`, `filter`, or `take`. A callback receiving `const`/read-only view must not mutate nested values by member methods or index operations. `rt borrow` is an explicitly scoped read view; `rt take` transfers ownership; `rt copy` and `rt share` respect copy/share authority. Never expose source-level pointer sigils.

If callbacks are ever passed through *local* channels, prove capture lifetime, confinement and no conflicting alias; actor mailbox payloads are serialized data and **never contain functions**. Add compiler-backed tests before enabling local callable-channel transport.
