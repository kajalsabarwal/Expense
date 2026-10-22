PRAGMA foreign_keys = ON;
CREATE TABLE categories (
 category TEXT PRIMARY KEY,
 discretionary INTEGER NOT NULL CHECK(discretionary IN (0,1))
);
CREATE TABLE expenses (
 expense_id TEXT PRIMARY KEY,
 expense_date TEXT NOT NULL CHECK(date(expense_date) IS NOT NULL),
 category TEXT NOT NULL REFERENCES categories(category),
 vendor TEXT NOT NULL,
 amount_inr INTEGER NOT NULL CHECK(amount_inr > 0)
);
CREATE TABLE budgets (
 month TEXT NOT NULL CHECK(length(month)=7),
 category TEXT NOT NULL REFERENCES categories(category),
 budget_inr INTEGER NOT NULL CHECK(budget_inr > 0),
 PRIMARY KEY(month,category)
);
CREATE VIEW budget_vs_actual AS
WITH actual AS (
 SELECT substr(expense_date,1,7) month, category, SUM(amount_inr) actual_inr
 FROM expenses GROUP BY 1,2
)
SELECT b.month,b.category,b.budget_inr,COALESCE(a.actual_inr,0) actual_inr,
 COALESCE(a.actual_inr,0)-b.budget_inr over_budget_inr,
 1.0*COALESCE(a.actual_inr,0)/b.budget_inr utilization
FROM budgets b LEFT JOIN actual a USING(month,category);
