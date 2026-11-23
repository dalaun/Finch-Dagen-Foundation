// Plain-words labels for /statechart (pstack). States say what a reader cares
// about: whether the foundation holds value, where the equipment is, who has
// been paid. Steps say what happens, in everyday words.
const who = {
  Founder: "the founder", Relative: "a relative", FamilyTrust: "the family trust",
  BusinessTrust: "the business trust", ManagementCo: "the management company",
  Foundation: "the foundation", Vendor: "an unrelated vendor", Grantee: "an outside grantee",
  PublicCharity: "a public charity", Spent: "spent",
};
const tokens = (v) => Object.values(v.owner);
export const title = "Foundation moves, as the checker walked them";
export const state = (v) => {
  const parts = [];
  const held = tokens(v).filter((o) => o === "Foundation").length;
  parts.push(held ? "Foundation holds value" : "Foundation holds nothing");
  if (v.eqOwner === "Foundation")
    parts.push(v.eqUser === "Foundation" ? "owns the equipment" : `equipment used by ${who[v.eqUser]}`);
  if (v.stock === "Foundation") parts.push(v.deadline ? "still holds the stock, period over" : "holds the stock");
  if (Object.entries(v.owner).some(([t, o]) => o === "Grantee" && v.fdn[t])) parts.push("a grant is out");
  if (v.broke.length) parts.push(`breaks ${v.broke.join(" and ")}`);
  return parts.join(", ");
};
export const group = (v) => (v.broke.length ? "broken" : "ok");
export const colors = { broken: "orange", ok: "teal" };
// step() gets the action name and the values before and after the step.
const moved = (from, to) => {
  for (const t of Object.keys(to.owner)) if (from.owner[t] !== to.owner[t]) return [from.owner[t], to.owner[t]];
  return [undefined, undefined];
};
export const step = (action, from, to) => {
  const [src, dst] = moved(from, to);
  switch (action) {
    case "Gift": return `${who[src]} gives to the foundation`;
    case "GiftStock": return "the founder gives the management company's stock";
    case "LendToFoundation": return `${who[src]} lends to the foundation without interest`;
    case "Buy": return `the foundation buys from ${who[dst]}`;
    case "BuyEquipment": return "the foundation buys the equipment";
    case "LeaseEquipment": return `the foundation leases the equipment to ${who[to.eqUser]}`;
    case "SellEquipment": return `the foundation sells the equipment to ${who[to.eqOwner]}`;
    case "SellStock": return `the foundation sells the stock to ${who[to.stock]}`;
    case "FounderWorks": return "the founder does program work";
    case "WriteRecord": return "the pay record is written";
    case "Wage": return "the foundation pays the founder";
    case "Repay": return `the foundation repays ${who[dst]}`;
    case "Grant": return `the foundation grants to ${who[dst]}`;
    case "GranteeSpends": return `the grantee pays ${who[dst]}`;
    case "PrivateMove": return "private money moves inside the stack";
    case "Rescreen": return "the insider settings are updated";
    case "PeriodEnds": return "the disposition period ends";
    default: return action;
  }
};
