-- JUNK DIMENSION IMPLEMENTATION
CREATE TABLE DIM_TRANSACTION_FLAGS (
    transaction_flags_key SERIAL PRIMARY KEY,
    payment_type VARCHAR(20),
    shipping_method VARCHAR(20),
    gift_wrap_flag CHAR(1),
    express_flag CHAR(1),
    first_time_buyer_flag CHAR(1),
    UNIQUE (payment_type, shipping_method, gift_wrap_flag, express_flag, first_time_buyer_flag)
);
