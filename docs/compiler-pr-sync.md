# Oreslang compiler PR cross-repo checkpoint (2026-10-06)

**Repository:** `rx-ores-callbacks` — Callback-first Rx adapters.

**Status at review:** The 10 newest compiler PRs were all open, not merged into `oreslang-source.java/main`. This PR documents interoperability and gates only; it does not claim those language/runtime changes are implemented in this downstream repository.

## Source-of-truth PRs
- [oreslang-source.java #398](https://github.com/ores-truffle-oreslang/oreslang-source.java/pull/398)
- [oreslang-source.java #399](https://github.com/ores-truffle-oreslang/oreslang-source.java/pull/399)
- [oreslang-source.java #404](https://github.com/ores-truffle-oreslang/oreslang-source.java/pull/404)
- [oreslang-source.java #405](https://github.com/ores-truffle-oreslang/oreslang-source.java/pull/405)
- [oreslang-source.java #406](https://github.com/ores-truffle-oreslang/oreslang-source.java/pull/406)
- [oreslang-source.java #408](https://github.com/ores-truffle-oreslang/oreslang-source.java/pull/408)
- [oreslang-source.java #409](https://github.com/ores-truffle-oreslang/oreslang-source.java/pull/409)
- [oreslang-source.java #410](https://github.com/ores-truffle-oreslang/oreslang-source.java/pull/410)
- [oreslang-source.java #411](https://github.com/ores-truffle-oreslang/oreslang-source.java/pull/411)
- [oreslang-source.java #412](https://github.com/ores-truffle-oreslang/oreslang-source.java/pull/412)

The select dependency stack is **#405 -> #406 -> #408 -> #412**; #404 is stacked on a match feature branch; #398, #399, #409, #410 and #411 are separate work. Never treat any one PR as the full compiler feature set.

## rx-ores-callbacks migration invariants
- Function values remain valid inside local callbacks; do not infer that functions may be transported by actor mailbox or `Channel<T>` (#410/#411).
- Preserve explicit-return block lambdas and expression-bodied lambda semantics, especially captures in deferred callbacks.
- Use `do select` only when no result is needed; never suppress fatal errors or double-dispatch callbacks (#405/#406/#408/#412).
- Compare callback cancellation semantics with Future/Channel adapters without altering this library’s baseline compiler pin.

## Conformance checks
- python3 scripts/test.py
- Check callback completion exactly once and cancellation
- Negative transport test for callback-bearing actor messages

## Version policy

Keep existing `compiler.lock`, `SOURCE_REF`, config and CI default behavior unchanged where present. For new features, test against an **exact commit SHA** of a compiler branch incorporating all required dependencies, then move pins only once that build is independently verified. A GitHub Action failure with `runner_id=0` and no steps is **not** a failed test or a passed test; mirror the exact Git tree to a funded organization without sharing credentials and verify blob/tree SHAs before claiming evidence.

No `&` or `*` pointer syntax should be added to public Oreslang code: use `rt borrow`, `rt copy`, `rt share`, `rt take` and capability-checked `rt proxy` where supported. Actor mailboxes carry serialized/frozen data, never function pointers or mutable object references.
