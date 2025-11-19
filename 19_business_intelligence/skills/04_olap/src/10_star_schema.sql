-- Star Schema Implementation
-- Production-ready data warehouse schema

-- Fact Table
CREATE TABLE FactSales (
    -- Surrogate key (optional)
    SalesKey BIGINT IDENTITY(1,1) PRIMARY KEY,
    
    -- Dimension keys
    DateKey INT NOT NULL,
    ProductKey INT NOT NULL,
    CustomerKey INT NOT NULL,
    EmployeeKey INT NOT NULL,
    GeographyKey INT NOT NULL,
    ChannelKey INT NOT NULL,
    
    -- Degenerate dimensions
    OrderID VARCHAR(20) NOT NULL,
    OrderLineNumber INT NOT NULL,
    InvoiceNumber VARCHAR(20),
    
    -- Measures
    SalesAmount DECIMAL(18,2) NOT NULL,
    SalesQuantity INT NOT NULL,
    UnitPrice DECIMAL(18,2) NOT NULL,
    DiscountAmount DECIMAL(18,2) DEFAULT 0,
    TaxAmount DECIMAL(18,2) DEFAULT 0,
    CostAmount DECIMAL(18,2),
    ShippingCost DECIMAL(18,2) DEFAULT 0,
    
    -- Audit columns
    SourceSystemID INT,
    LoadDate DATETIME2 DEFAULT SYSUTCDATETIME(),
    LoadBatchID INT,
    
    -- Constraints
    CONSTRAINT FK_FactSales_Date FOREIGN KEY (DateKey) REFERENCES DimDate(DateKey),
    CONSTRAINT FK_FactSales_Product FOREIGN KEY (ProductKey) REFERENCES DimProduct(ProductKey),
    CONSTRAINT FK_FactSales_Customer FOREIGN KEY (CustomerKey) REFERENCES DimCustomer(CustomerKey),
    CONSTRAINT FK_FactSales_Employee FOREIGN KEY (EmployeeKey) REFERENCES DimEmployee(EmployeeKey),
    CONSTRAINT FK_FactSales_Geography FOREIGN KEY (GeographyKey) REFERENCES DimGeography(GeographyKey),
    CONSTRAINT FK_FactSales_Channel FOREIGN KEY (ChannelKey) REFERENCES DimChannel(ChannelKey)
);

-- Columnstore index for fast analytics
CREATE CLUSTERED COLUMNSTORE INDEX CCI_FactSales ON FactSales;

-- Nonclustered indexes for filtering
CREATE NONCLUSTERED INDEX IX_FactSales_DateKey ON FactSales(DateKey) INCLUDE (SalesAmount, SalesQuantity);
CREATE NONCLUSTERED INDEX IX_FactSales_ProductKey ON FactSales(ProductKey) INCLUDE (SalesAmount);
CREATE NONCLUSTERED INDEX IX_FactSales_CustomerKey ON FactSales(CustomerKey);

-- Dimension Tables
CREATE TABLE DimProduct (
    ProductKey INT IDENTITY(1,1) PRIMARY KEY,
    ProductID VARCHAR(50) NOT NULL,
    ProductName VARCHAR(200) NOT NULL,
    
    -- Hierarchy attributes
    Category VARCHAR(100) NOT NULL,
    Subcategory VARCHAR(100),
    Brand VARCHAR(100),
    ProductLine VARCHAR(100),
    
    -- Product attributes
    Color VARCHAR(50),
    Size VARCHAR(20),
    Weight DECIMAL(10,2),
    UnitOfMeasure VARCHAR(20),
    
    -- Pricing
    StandardCost DECIMAL(18,2),
    ListPrice DECIMAL(18,2),
    
    -- Status
    Status VARCHAR(20),
    IntroducedDate DATE,
    DiscontinuedDate DATE,
    
    -- SCD Type 2
    StartDate DATE NOT NULL DEFAULT '1900-01-01',
    EndDate DATE NOT NULL DEFAULT '9999-12-31',
    IsCurrent BIT NOT NULL DEFAULT 1,
    
    -- Audit
    LoadDate DATETIME2 DEFAULT SYSUTCDATETIME()
);

CREATE UNIQUE INDEX UX_DimProduct_ProductID_Current ON DimProduct(ProductID, IsCurrent);
CREATE INDEX IX_DimProduct_Category ON DimProduct(Category, Subcategory);

CREATE TABLE DimCustomer (
    CustomerKey INT IDENTITY(1,1) PRIMARY KEY,
    CustomerID VARCHAR(50) NOT NULL,
    
    -- Demographics
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    FullName AS (FirstName + ' ' + LastName),
    Email VARCHAR(200),
    Phone VARCHAR(20),
    BirthDate DATE,
    Gender VARCHAR(1),
    MaritalStatus VARCHAR(1),
    
    -- Segmentation
    CustomerSegment VARCHAR(50),
    CustomerType VARCHAR(50),
    AnnualIncome DECIMAL(15,2),
    CreditRating VARCHAR(10),
    
    -- Geographic reference
    GeographyKey INT,
    
    -- Status
    AccountOpenDate DATE,
    AccountCloseDate DATE,
    CustomerStatus VARCHAR(20),
    
    -- SCD Type 2
    StartDate DATE NOT NULL DEFAULT '1900-01-01',
    EndDate DATE NOT NULL DEFAULT '9999-12-31',
    IsCurrent BIT NOT NULL DEFAULT 1,
    
    -- Audit
    LoadDate DATETIME2 DEFAULT SYSUTCDATETIME(),
    
    CONSTRAINT FK_DimCustomer_Geography FOREIGN KEY (GeographyKey) REFERENCES DimGeography(GeographyKey)
);

CREATE UNIQUE INDEX UX_DimCustomer_CustomerID_Current ON DimCustomer(CustomerID, IsCurrent);
CREATE INDEX IX_DimCustomer_Segment ON DimCustomer(CustomerSegment);

CREATE TABLE DimGeography (
    GeographyKey INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Hierarchy
    Country VARCHAR(100) NOT NULL,
    CountryCode VARCHAR(3),
    Region VARCHAR(50),
    StateProvince VARCHAR(100),
    StateProvinceCode VARCHAR(10),
    City VARCHAR(100),
    PostalCode VARCHAR(10),
    
    -- Coordinates
    Latitude DECIMAL(9,6),
    Longitude DECIMAL(9,6),
    
    -- Computed
    FullLocation AS (City + ', ' + StateProvinceCode + ', ' + Country)
);

CREATE INDEX IX_DimGeography_Country ON DimGeography(Country, StateProvince, City);

-- Unknown member records
INSERT INTO DimProduct (ProductKey, ProductID, ProductName, Category, IsCurrent)
VALUES (-1, 'UNKNOWN', 'Unknown Product', 'Unknown', 1);

INSERT INTO DimCustomer (CustomerKey, CustomerID, FullName, IsCurrent)
VALUES (-1, 'UNKNOWN', 'Unknown Customer', 1);

INSERT INTO DimGeography (GeographyKey, Country, City)
VALUES (-1, 'Unknown', 'Unknown');
