# Keystone

TLC reached more states than the chart budget of 500, so the chart draws only the bug paths: 4 states and 3 arrows.

## Keystone breaks
The shortest path has 3 steps:
0. Foundation holds nothing
1. the founder gives to the foundation: Foundation holds value
2. the foundation grants to an outside grantee: Foundation holds nothing, a grant is out, breaks 4945
3. the grantee pays the founder: Foundation holds nothing, breaks 4941 and 4945

## Rules not checked
TypeOK
After the first break, each TLC run stops at 100,000 distinct states. A run reached that bound before it checked this rule in every state.
