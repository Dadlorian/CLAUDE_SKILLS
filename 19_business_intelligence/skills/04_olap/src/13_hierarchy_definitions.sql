-- Hierarchy Definitions and Attribute Relationships
-- SQL-based hierarchy metadata

-- Product Hierarchy Structure
INSERT INTO HierarchyDefinition (HierarchyName, LevelNumber, AttributeName, ParentAttribute, RelationshipType)
VALUES
('Product Hierarchy', 1, 'Category', NULL, 'Rigid'),
('Product Hierarchy', 2, 'Subcategory', 'Category', 'Rigid'),
('Product Hierarchy', 3, 'ProductName', 'Subcategory', 'Rigid');

-- Geography Hierarchy Structure
INSERT INTO HierarchyDefinition VALUES
('Geography', 1, 'Region', NULL, 'Rigid'),
('Geography', 2, 'Country', 'Region', 'Rigid'),
('Geography', 3, 'StateProvince', 'Country', 'Rigid'),
('Geography', 4, 'City', 'StateProvince', 'Rigid');

-- Employee Organization Hierarchy (Parent-Child)
WITH EmployeeHierarchy AS (
    SELECT
        EmployeeID,
        EmployeeName,
        ManagerID,
        CAST(EmployeeID AS VARCHAR(MAX)) AS EmployeePath,
        0 AS Level
    FROM Employee
    WHERE ManagerID IS NULL
    
    UNION ALL
    
    SELECT
        e.EmployeeID,
        e.EmployeeName,
        e.ManagerID,
        CAST(eh.EmployeePath + '|' + CAST(e.EmployeeID AS VARCHAR) AS VARCHAR(MAX)),
        eh.Level + 1
    FROM Employee e
    INNER JOIN EmployeeHierarchy eh ON e.ManagerID = eh.EmployeeID
)
SELECT * FROM EmployeeHierarchy;
