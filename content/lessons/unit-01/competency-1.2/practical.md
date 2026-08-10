# Practical: Compare manual and digital workflows

## Purpose

Compare two methods using measured evidence rather than assumptions.

## Dataset

Fictional request codes: `P, N, P, L, N, P, N, N, L, P, L, N, P, P, N, L, N, P, L, N` where P = printing, N = network, and L = login.

Expanded dataset: duplicate that complete 20-code sequence once, preserving its order, to make exactly 40 records.

## Task

1. Prepare the 20-record source list. Half the pairs start manually; half start digitally, so practice does not favour the same method for everyone.
2. For the manual trial, start timing when the first code is read and stop when all three category totals and the grand total are written. Tally each category and record elapsed time.
3. For the digital trial, include data entry in the timed workflow. Enter one code per cell, count each category with a platform-equivalent expression such as `COUNTIF(range,"P")`, and stop when all four totals are displayed.
4. Compare both totals with the expected results and investigate any difference. Do not discard a failed trial; record the cause and correction.
5. Repeat steps 2–4 with the fixed 40-record expanded dataset. If time allows, complete three trials per method and compare the median time rather than the fastest attempt.
6. Evaluate speed, accuracy, reproducibility, setup effort, retrieval, and suitability at each scale.
7. Recommend a manual, digital, or hybrid workflow and state where human checking remains necessary.

## Evidence table

| Records | Method | Trial | Time (seconds) | P | N | L | Grand total | Error or correction |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 20 | Manual/digital | 1 | | | | | | |
| 40 | Manual/digital | 1 | | | | | | |

## Expected results

Original totals: P = 7, N = 8, L = 5; total records = 20. Expanded totals: P = 14, N = 16, L = 10; total records = 40.

## Validation checklist

Preserve the source list; confirm category totals sum to the record count; repeat one count independently; distinguish measured time from opinion; state whether data entry/setup time was included when comparing results.

## Troubleshooting

Remove leading spaces if identical codes count differently. If a formula range omits rows, select the complete populated column and recalculate.

## Safety and privacy

Use only fictional codes. Do not substitute support tickets, usernames, or identifiable service records.
