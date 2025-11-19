-- ETL: Fact Table Loading
INSERT INTO FACT_SALES_TRANSACTION (date_key, customer_key, product_key, ...)
SELECT d.date_key, c.customer_key, p.product_key, ...
FROM staging.sales s
JOIN DIM_DATE d ON s.sale_date = d.date
JOIN DIM_CUSTOMER c ON s.customer_id = c.customer_id AND d.date BETWEEN c.effective_date AND c.expiration_date
JOIN DIM_PRODUCT p ON s.product_id = p.product_id;
