Open *Project > Configuration > Time Types*.

For each time type, set **Cost Type**:

- **Employee Cost** (default): the line keeps the employee hourly cost.
- **Ratio of Employee Cost**: set **Cost Ratio**. `1.0` gives 100 % of the
  employee hourly cost.
- **Fixed Hourly Cost**: set **Fixed Cost** in the company currency. Use a
  positive amount. `31.00` gives an hourly cost of 31.00. The analytic amount
  has a minus sign. Zero is not permitted. Use **Employee Cost** when the
  line must not have a cost.

Leave **Company** empty to share the time type between companies.
A shared time type accepts **Employee Cost** and **Ratio of Employee Cost**.
**Fixed Hourly Cost** needs a company, because the amount is in the company
currency.
