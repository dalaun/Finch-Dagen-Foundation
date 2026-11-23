# Keystone

TLC reached more states than the chart budget of 500, so the chart draws only the bug paths: 4 states and 3 arrows.

## Keystone breaks
The shortest path has 3 steps:
0. Foundation holds nothing
1. the founder gives to the foundation: Foundation holds value
2. the foundation buys the equipment: Foundation holds nothing, owns the equipment
3. the foundation leases the equipment to the management company: Foundation holds nothing, equipment used by the management company, breaks 4941

## Rules not checked
TypeOK, NoTaxableGrant
After the first break, each TLC run stops at 100,000 distinct states. A run reached that bound before it checked these rules in every state.
