-- SNOWFLAKE SCHEMA (Normalized Dimensions)
CREATE TABLE DIM_PRODUCT_CATEGORY (
    category_key SERIAL PRIMARY KEY,
    category_name VARCHAR(100),
    department_key INTEGER
);

CREATE TABLE DIM_PRODUCT_SNOWFLAKE (
    product_key SERIAL PRIMARY KEY,
    product_name VARCHAR(200),
    category_key INTEGER,
    FOREIGN KEY (category_key) REFERENCES DIM_PRODUCT_CATEGORY(category_key)
);
