# Keystone

TLC reached more states than the chart budget of 500, so the chart draws only the bug paths: 3 states and 2 arrows.

## Keystone breaks
The shortest path has 2 steps:
0. Foundation holds nothing
1. an unrelated vendor gives to the foundation: Foundation holds value
2. the foundation buys from an unrelated vendor: Foundation holds nothing, breaks 4941

## Rules not checked
TypeOK, NoTaxableGrant
After the first break, each TLC run stops at 100,000 distinct states. A run reached that bound before it checked these rules in every state.
