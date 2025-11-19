-- ROLE-PLAYING DIMENSION (Date used multiple times)
CREATE VIEW DIM_ORDER_DATE AS SELECT * FROM DIM_DATE;
CREATE VIEW DIM_SHIP_DATE AS SELECT * FROM DIM_DATE;
CREATE VIEW DIM_DELIVERY_DATE AS SELECT * FROM DIM_DATE;

-- Fact table with multiple date roles
-- FACT_ORDER
-- - order_date_key (FK to DIM_DATE)
-- - ship_date_key (FK to DIM_DATE)
-- - delivery_date_key (FK to DIM_DATE)
