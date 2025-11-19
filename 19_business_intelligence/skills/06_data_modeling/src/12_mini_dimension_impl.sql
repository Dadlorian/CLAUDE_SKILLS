-- MINI-DIMENSION IMPLEMENTATION
CREATE TABLE DIM_CUSTOMER_DEMOGRAPHICS (
    demographics_key SERIAL PRIMARY KEY,
    age_range VARCHAR(20),
    income_band VARCHAR(20),
    credit_score_band VARCHAR(20),
    customer_segment VARCHAR(30),
    UNIQUE (age_range, income_band, credit_score_band)
);
