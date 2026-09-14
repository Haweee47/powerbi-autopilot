# Outdoor shop sample data

Synthetic sales for an outdoor gear retailer, 2024-01-01 to 2026-08-31. Used by [example 05](../../05-own-model/README.md)
to test a pilot on a model that is shaped differently from the reference model.

```bash
python generate.py   # Orders.csv, Stores.csv, Products.csv, Budget.csv (UTF-8, fixed seed: the same files for everyone)
```

| File | Rows | What |
|---|---:|---|
| Orders.csv | 13,559 | One order per row: date, store, product, quantity, discount, net sales, cost (USD) |
| Stores.csv | 12 | 10 retail stores in 4 regions + 2 online stores |
| Products.csv | 24 | 5 categories, 17 subcategories |
| Budget.csv | 180 | Monthly sales budget by category, full years 2024-2026 |

Planted story, January-August 2026 vs the same months of 2025: Camping ▼7.3%, Footwear ▲19.3%, Climbing ▲17.7%,
Burlington store ▼48.6%, total ▲0.4%. The budget covers whole years on purpose: a report that compares eight months of sales
with a twelve-month budget shows 64.5% attainment instead of 95.6%.

All names and numbers are made up. License: MIT, like the rest of the repository.
