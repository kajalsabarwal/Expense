"""Rebuild the demo SQLite database and query results. Python standard library only."""
from pathlib import Path
import csv, sqlite3, random, calendar, re, json

ROOT = Path(__file__).resolve().parents[1]

def write_csv(path, headers, rows):
    with path.open('w', newline='') as f:
        w = csv.writer(f); w.writerow(headers); w.writerows(rows)

def main():
    rng = random.Random(42)
    categories = [('Rent',0,40000,1),('Salaries',0,180000,6),
                  ('Utilities',0,12000,4),('Software',1,15000,5),
                  ('Travel',1,20000,10),('Meals',1,8000,16),
                  ('Office supplies',1,6000,8),('Marketing',1,25000,10)]
    expenses, budgets = [], []
    for month in range(1,13):
        for category, discretionary, budget, count in categories:
            budgets.append([f'2025-{month:02}',category,budget])
            factor = 1 if category in ('Rent','Salaries') else rng.uniform(.75,1.22)
            if category=='Travel' and month in (6,11,12): factor=1.65
            if category=='Software': factor=1.18
            if category=='Marketing' and month in (10,11,12): factor=1.35
            total=round(budget*factor)
            weights=[rng.uniform(.5,1.5) for _ in range(count)]
            parts=[round(total*w/sum(weights)) for w in weights]
            parts[-1]+=total-sum(parts)
            for n,amount in enumerate(parts):
                day=rng.randint(1,calendar.monthrange(2025,month)[1])
                expenses.append([f'EXP{len(expenses)+1:05}',f'2025-{month:02}-{day:02}',
                                 category,f'{category} vendor {n%3+1}',amount])
    expenses.sort(key=lambda x:(x[1],x[0]))
    write_csv(ROOT/'data/expenses.csv',['expense_id','expense_date','category','vendor','amount_inr'],expenses)
    write_csv(ROOT/'data/budgets.csv',['month','category','budget_inr'],budgets)
    write_csv(ROOT/'data/categories.csv',['category','discretionary'],[x[:2] for x in categories])
    db=ROOT/'data/expenses.db'
    if db.exists(): db.unlink()
    con=sqlite3.connect(db)
    con.executescript((ROOT/'sql/schema.sql').read_text())
    con.executemany('INSERT INTO categories VALUES (?,?)',[x[:2] for x in categories])
    con.executemany('INSERT INTO expenses VALUES (?,?,?,?,?)',expenses)
    con.executemany('INSERT INTO budgets VALUES (?,?,?)',budgets)
    con.commit()
    results={}
    for name,sql in re.findall(r'-- name: (\w+)\n(.*?;)',(ROOT/'sql/analysis.sql').read_text(),re.S):
        cur=con.execute(sql); headers=[c[0] for c in cur.description]; rows=cur.fetchall()
        write_csv(ROOT/f'reports/{name}.csv',headers,rows)
        results[name]=[dict(zip(headers,r)) for r in rows]
    assert len(expenses)==720 and len(budgets)==96
    assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert not con.execute('PRAGMA foreign_key_check').fetchall()
    assert con.execute('SELECT COUNT(*) FROM (SELECT substr(expense_date,1,7) month,category FROM expenses EXCEPT SELECT month,category FROM budgets)').fetchone()[0]==0
    total=sum(r[4] for r in expenses)
    assert total==sum(r['actual_inr'] for r in results['monthly_summary'])==sum(r['actual_inr'] for r in results['category_summary'])
    # Edge fixture: an empty category-month must retain its budget with zero actuals.
    con.execute("INSERT INTO budgets VALUES ('2026-01','Rent',40000)")
    assert con.execute("SELECT actual_inr,over_budget_inr FROM budget_vs_actual WHERE month='2026-01'").fetchone()==(0,-40000)
    con.rollback()
    (ROOT/'reports/results.json').write_text(json.dumps(results,indent=2))
    con.close()
    print(f'Validated {len(expenses)} expenses; actual INR {total:,}; budget INR {sum(r[2] for r in budgets):,}')

if __name__=='__main__': main()
