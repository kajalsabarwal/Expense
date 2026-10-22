# Data dictionary

All amounts are integer INR, with no taxes or foreign-exchange adjustments. Expense dates use ISO `YYYY-MM-DD`; month keys use `YYYY-MM`. The project covers the 2025 calendar year.

| Table | Field | Meaning |
| --- | --- | --- |
| expenses | expense_id | Unique synthetic transaction identifier |
| expenses | expense_date | Recorded expense date |
| expenses | category | Category key, references categories |
| expenses | vendor | Fictional vendor label, not a real company |
| expenses | amount_inr | Positive transaction amount in INR |
| budgets | month | Budget month |
| budgets | category | Budget category |
| budgets | budget_inr | Positive planned expense amount |
| categories | category | Unique category name |
| categories | discretionary | 1 for scenario-eligible categories, otherwise 0 |

The composite budget key is `(month, category)`. Rent, salaries, and utilities are excluded from the discretionary savings scenario. Marketing, travel, software, meals, and office supplies are included by modeling assumption.

The generator holds rent and salaries at budget, sets software to 118% of budget, increases travel in June/November/December and marketing in Q4, and uses seeded variation elsewhere. These deliberately constructed patterns demonstrate analysis techniques and are not evidence of real-world spending behavior. Amounts are allocated across synthetic transactions and rounded to whole INR while preserving category-month totals.

SQL uses a budget-led comparison view. Expense category-months without budgets must be resolved before using the view; the pipeline checks coverage. Source dates in Excel are numeric dates, while budget keys remain text to match SQL grouping.
