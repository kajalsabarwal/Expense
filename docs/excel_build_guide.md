# Rebuild the Excel dashboard manually

The delivered workbook is ready to use. The Python command rebuilds the SQL data and reports only. To recreate the workbook in Excel:

1. Import `data/expenses.csv` into a sheet named Expenses. Put the header in row 3 and transactions in rows 4–723. Convert the expense_date column to Excel dates and amount_inr to numbers.
2. Import `data/budgets.csv` into Budgets, also with headers at row 3. Keep month as text and budget_inr as numeric.
3. On Dashboard, calculate annual budget with `=SUM(Budgets!C4:C99)` and actual spend with `=SUM(Expenses!E4:E723)`.
4. For each month, use `SUMIF` against the text budget month and `SUMIFS` against the transaction date range. For example, January actuals use `=SUMIFS(Expenses!$E$4:$E$723,Expenses!$B$4:$B$723,">="&DATE(2025,1,1),Expenses!$B$4:$B$723,"<"&DATE(2025,2,1))`.
5. Use `SUMIF` on category to calculate category actual and budget totals. Calculate variance as actual minus budget and utilization as actual divided by budget, guarding zero denominators.
6. Insert a line chart for monthly budget and actuals, and a clustered column chart for category comparisons. Link charts directly to the formula summary cells.
7. Add conditional formatting to highlight positive over-budget variances. Include a savings-rate input and multiply discretionary category actuals by that rate.
8. Reconcile annual and monthly results to the CSV reports. Confirm the workbook updates after changing an existing budget amount, then restore the original value.

Do not import `month` as a numeric Excel date without also adjusting the matching formulas. Do not sum budgets after joining them directly to multiple transactions.
