# 06. The one thing only the founder can supply

[Back to the rehearsal overview](README.md)

The twin needs twelve months of real transactions. Email receipts show only a slice: anything paid by card at a counter, by bill pay, or by automatic draft (housing, utilities, insurance, fuel, phone, taxes) never sends a receipt. Only the bank and card statements have the whole picture.

## The one motion

For each checking account and each credit card:

1. Sign in to the bank or card site yourself.
2. Open the account's activity or statements page.
3. Choose **Download** or **Export**, pick **CSV**, and set the dates to the last 12 months.
4. Save the file and attach it in the Finch-Dagen channel.

That is the whole handoff. No sign-in is shared and no password is typed by an agent.

## What happens to the file

- It stays in the private project folder, never in this public repository.
- Only these columns are kept: date, description, amount, debit or credit. Card and account numbers, if the export has them, are dropped on read.
- Lines are sorted into the [taxonomy](02-expense-domain-taxonomy.md). Anything health-related or otherwise sensitive is put in the withheld domain and left for the founder to sort.
- The twin runs on the sorted ledger. Results go to the founder first.

## Useful but optional

- The formation documents for each entity (trust instruments, operating agreements, EIN letters). They settle the tax classification facts the twin otherwise marks "unknown".
- The last filed returns for each entity, if any were filed.
