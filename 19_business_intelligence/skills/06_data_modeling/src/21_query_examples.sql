-- QUERY EXAMPLES
-- Sales by month and category
SELECT d.month_name, p.category_name, SUM(f.total_amount)
FROM FACT_SALES_TRANSACTION f
JOIN DIM_DATE d ON f.date_key = d.date_key
JOIN DIM_PRODUCT p ON f.product_key = p.product_key
WHERE d.year = 2024
GROUP BY d.month_name, p.category_name;
