-- Monthly trend: aggregate actuals before comparing with budgets to avoid join fanout.
-- name: monthly_summary
WITH monthly AS (
 SELECT month,SUM(budget_inr) budget_inr,SUM(actual_inr) actual_inr,
 SUM(over_budget_inr) over_budget_inr FROM budget_vs_actual GROUP BY month
)
SELECT *,ROUND(1.0*actual_inr/budget_inr,4) utilization,
 ROUND(100.0*(actual_inr-LAG(actual_inr) OVER(ORDER BY month))/
 NULLIF(LAG(actual_inr) OVER(ORDER BY month),0),2) mom_change_pct
FROM monthly ORDER BY month;

-- name: category_summary
SELECT category,SUM(budget_inr) budget_inr,SUM(actual_inr) actual_inr,
 SUM(over_budget_inr) over_budget_inr,
 ROUND(1.0*SUM(actual_inr)/SUM(budget_inr),4) utilization,
 ROUND(100.0*SUM(actual_inr)/(SELECT SUM(amount_inr) FROM expenses),2) spend_share_pct
FROM budget_vs_actual GROUP BY category ORDER BY actual_inr DESC;

-- name: overspending_months
SELECT * FROM budget_vs_actual WHERE over_budget_inr>0
ORDER BY over_budget_inr DESC;

-- name: vendor_ranking
SELECT category,vendor,COUNT(*) transactions,SUM(amount_inr) total_inr,
 DENSE_RANK() OVER(PARTITION BY category ORDER BY SUM(amount_inr) DESC) category_rank
FROM expenses GROUP BY category,vendor ORDER BY total_inr DESC;

-- Hypothetical 10% reduction in discretionary spend, not realized savings.
-- name: savings_scenario
SELECT e.category,SUM(e.amount_inr) actual_inr,0.10 reduction_rate,
 ROUND(SUM(e.amount_inr)*0.10,2) potential_savings_inr
FROM expenses e JOIN categories c USING(category) WHERE c.discretionary=1
GROUP BY e.category ORDER BY potential_savings_inr DESC;
