-- BRIDGE TABLE for Ragged Hierarchy
CREATE TABLE BRIDGE_EMPLOYEE_HIERARCHY (
    employee_key INTEGER,
    manager_key INTEGER,
    hierarchy_level INTEGER,
    is_top_level CHAR(1),
    is_bottom_level CHAR(1),
    PRIMARY KEY (employee_key, manager_key)
);
