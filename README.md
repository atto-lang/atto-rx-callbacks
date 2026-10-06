# rx-ores-callbacks

Standalone callback-only reactive library for Oreslang.

This variant deliberately uses synchronous callbacks rather than channels or
Future/await. It stays separate from rx-ores and rx-oreslang-channels so the
three execution models can be tested and benchmarked independently.
