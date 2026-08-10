# Practical: Design and test an IPO model

## Purpose

Build, execute, and evaluate an abstract information model.

## Scenario and data

A fictional community centre records room use: Hall A 6 hours, Hall B 4 hours, Lab 8 hours. Available hours for each room are 10.

## Task

1. State the decision: identify which room has the lowest unused capacity.
2. Define inputs with labels and units.
3. Define the process as explicit calculations and comparisons.
4. Define the output and intended user.
5. Execute the model manually or in a spreadsheet.
6. Test it with a boundary case where a room is used for all 10 hours.
7. Evaluate timeliness and whether a computer is appropriate at three rooms and at 300 rooms.

## Expected results

Unused capacity: Hall A 4 hours, Hall B 6 hours, Lab 2 hours. The Lab has the lowest unused capacity. A fully used room has 0 unused hours.

## Validation checklist

Check that used hours do not exceed available hours; retain units; verify subtraction; confirm the comparison selects the minimum unused capacity.

## Troubleshooting

If a formula returns negative unused time, check the source value and define how invalid over-capacity input should be handled. If ties occur, report every tied room.

## Safety and privacy

Use only the fictional room data. Do not substitute identifiable booking or access records.
