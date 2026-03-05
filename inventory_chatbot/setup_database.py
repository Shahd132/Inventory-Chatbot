import sqlite3
import datetime
import random

DB_NAME = 'inventory_chatbot.db'

def create_schema(cursor):
    cursor.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS Customers (
        CustomerId   INTEGER PRIMARY KEY AUTOINCREMENT,
        CustomerCode VARCHAR(50)   UNIQUE NOT NULL,
        CustomerName NVARCHAR(200) NOT NULL,
        Email        NVARCHAR(200) NULL,
        Phone        NVARCHAR(50)  NULL,
        BillingAddress1 NVARCHAR(200) NULL,
        BillingCity  NVARCHAR(100) NULL,
        BillingCountry NVARCHAR(100) NULL,
        CreatedAt    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UpdatedAt    DATETIME NULL,
        IsActive     INTEGER  NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS Vendors (
        VendorId    INTEGER PRIMARY KEY AUTOINCREMENT,
        VendorCode  VARCHAR(50)   UNIQUE NOT NULL,
        VendorName  NVARCHAR(200) NOT NULL,
        Email       NVARCHAR(200) NULL,
        Phone       NVARCHAR(50)  NULL,
        AddressLine1 NVARCHAR(200) NULL,
        City        NVARCHAR(100) NULL,
        Country     NVARCHAR(100) NULL,
        CreatedAt   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UpdatedAt   DATETIME NULL,
        IsActive    INTEGER  NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS Sites (
        SiteId      INTEGER PRIMARY KEY AUTOINCREMENT,
        SiteCode    VARCHAR(50)   UNIQUE NOT NULL,
        SiteName    NVARCHAR(200) NOT NULL,
        AddressLine1 NVARCHAR(200) NULL,
        City        NVARCHAR(100) NULL,
        Country     NVARCHAR(100) NULL,
        TimeZone    NVARCHAR(100) NULL,
        CreatedAt   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UpdatedAt   DATETIME NULL,
        IsActive    INTEGER  NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS Locations (
        LocationId       INTEGER PRIMARY KEY AUTOINCREMENT,
        SiteId           INTEGER NOT NULL,
        LocationCode     VARCHAR(50)   NOT NULL,
        LocationName     NVARCHAR(200) NOT NULL,
        ParentLocationId INTEGER NULL,
        CreatedAt        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UpdatedAt        DATETIME NULL,
        IsActive         INTEGER  NOT NULL DEFAULT 1,
        UNIQUE (SiteId, LocationCode),
        FOREIGN KEY (SiteId)           REFERENCES Sites(SiteId),
        FOREIGN KEY (ParentLocationId) REFERENCES Locations(LocationId)
    );

    CREATE TABLE IF NOT EXISTS Items (
        ItemId        INTEGER PRIMARY KEY AUTOINCREMENT,
        ItemCode      NVARCHAR(100) UNIQUE NOT NULL,
        ItemName      NVARCHAR(200) NOT NULL,
        Category      NVARCHAR(100) NULL,
        UnitOfMeasure NVARCHAR(50)  NULL,
        CreatedAt     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UpdatedAt     DATETIME NULL,
        IsActive      INTEGER  NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS Assets (
        AssetId      INTEGER PRIMARY KEY AUTOINCREMENT,
        AssetTag     VARCHAR(100)  UNIQUE NOT NULL,
        AssetName    NVARCHAR(200) NOT NULL,
        SiteId       INTEGER NOT NULL,
        LocationId   INTEGER NULL,
        SerialNumber NVARCHAR(200) NULL,
        Category     NVARCHAR(100) NULL,
        Status       VARCHAR(30)   NOT NULL DEFAULT 'Active',
        Cost         DECIMAL(18,2) NULL,
        PurchaseDate DATE NULL,
        VendorId     INTEGER NULL,
        CreatedAt    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UpdatedAt    DATETIME NULL,
        FOREIGN KEY (SiteId)     REFERENCES Sites(SiteId),
        FOREIGN KEY (LocationId) REFERENCES Locations(LocationId),
        FOREIGN KEY (VendorId)   REFERENCES Vendors(VendorId)
    );

    CREATE TABLE IF NOT EXISTS Bills (
        BillId      INTEGER PRIMARY KEY AUTOINCREMENT,
        VendorId    INTEGER NOT NULL,
        BillNumber  VARCHAR(100)  NOT NULL,
        BillDate    DATE NOT NULL,
        DueDate     DATE NULL,
        TotalAmount DECIMAL(18,2) NOT NULL,
        Currency    VARCHAR(10)   NOT NULL DEFAULT 'USD',
        Status      VARCHAR(30)   NOT NULL DEFAULT 'Open',
        CreatedAt   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UpdatedAt   DATETIME NULL,
        UNIQUE (VendorId, BillNumber),
        FOREIGN KEY (VendorId) REFERENCES Vendors(VendorId)
    );

    CREATE TABLE IF NOT EXISTS PurchaseOrders (
        POId      INTEGER PRIMARY KEY AUTOINCREMENT,
        PONumber  VARCHAR(100) UNIQUE NOT NULL,
        VendorId  INTEGER NOT NULL,
        PODate    DATE NOT NULL,
        Status    VARCHAR(30) NOT NULL DEFAULT 'Open',
        SiteId    INTEGER NULL,
        CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UpdatedAt DATETIME NULL,
        FOREIGN KEY (VendorId) REFERENCES Vendors(VendorId),
        FOREIGN KEY (SiteId)   REFERENCES Sites(SiteId)
    );

    CREATE TABLE IF NOT EXISTS PurchaseOrderLines (
        POLineId    INTEGER PRIMARY KEY AUTOINCREMENT,
        POId        INTEGER NOT NULL,
        LineNumber  INTEGER NOT NULL,
        ItemId      INTEGER NULL,
        ItemCode    NVARCHAR(100) NOT NULL,
        Description NVARCHAR(200) NULL,
        Quantity    DECIMAL(18,4) NOT NULL,
        UnitPrice   DECIMAL(18,4) NOT NULL,
        UNIQUE (POId, LineNumber),
        FOREIGN KEY (POId)   REFERENCES PurchaseOrders(POId),
        FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
    );

    CREATE TABLE IF NOT EXISTS SalesOrders (
        SOId       INTEGER PRIMARY KEY AUTOINCREMENT,
        SONumber   VARCHAR(100) UNIQUE NOT NULL,
        CustomerId INTEGER NOT NULL,
        SODate     DATE NOT NULL,
        Status     VARCHAR(30) NOT NULL DEFAULT 'Open',
        SiteId     INTEGER NULL,
        CreatedAt  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UpdatedAt  DATETIME NULL,
        FOREIGN KEY (CustomerId) REFERENCES Customers(CustomerId),
        FOREIGN KEY (SiteId)     REFERENCES Sites(SiteId)
    );

    CREATE TABLE IF NOT EXISTS SalesOrderLines (
        SOLineId    INTEGER PRIMARY KEY AUTOINCREMENT,
        SOId        INTEGER NOT NULL,
        LineNumber  INTEGER NOT NULL,
        ItemId      INTEGER NULL,
        ItemCode    NVARCHAR(100) NOT NULL,
        Description NVARCHAR(200) NULL,
        Quantity    DECIMAL(18,4) NOT NULL,
        UnitPrice   DECIMAL(18,4) NOT NULL,
        UNIQUE (SOId, LineNumber),
        FOREIGN KEY (SOId)   REFERENCES SalesOrders(SOId),
        FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
    );

    CREATE TABLE IF NOT EXISTS AssetTransactions (
        AssetTxnId     INTEGER PRIMARY KEY AUTOINCREMENT,
        AssetId        INTEGER NOT NULL,
        FromLocationId INTEGER NULL,
        ToLocationId   INTEGER NULL,
        TxnType        VARCHAR(30) NOT NULL,
        Quantity       INTEGER     NOT NULL DEFAULT 1,
        TxnDate        DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        Note           NVARCHAR(500) NULL,
        FOREIGN KEY (AssetId)        REFERENCES Assets(AssetId),
        FOREIGN KEY (FromLocationId) REFERENCES Locations(LocationId),
        FOREIGN KEY (ToLocationId)   REFERENCES Locations(LocationId)
    );
    """)
    print("Schema created")

def seed_data(cursor):
    now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    today = datetime.date.today()
    current_year = today.year

    # --- Customers ---
    customers = [
        ('CUST-001', 'Alpha Corp',    'alpha@alphacorp.com',   '+1-555-0101', '123 Main St',    'New York',  'USA'),
        ('CUST-002', 'Beta LLC',      'beta@betallc.com',      '+1-555-0102', '456 Oak Ave',    'Chicago',   'USA'),
        ('CUST-003', 'Gamma GmbH',    'info@gamma.de',         '+49-30-1234', 'Berliner Str 7', 'Berlin',    'Germany'),
        ('CUST-004', 'Delta Traders', 'delta@traders.ae',      '+971-4-0001', 'Sheikh Rd 1',    'Dubai',     'UAE'),
        ('CUST-005', 'Epsilon Ltd',   'contact@epsilon.co.uk', '+44-20-9999', '10 Downing Ln',  'London',    'UK'),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO Customers
            (CustomerCode, CustomerName, Email, Phone, BillingAddress1, BillingCity, BillingCountry, CreatedAt)
        VALUES (?,?,?,?,?,?,?,?)
    """, [c + (now,) for c in customers])

    # --- Vendors ---
    vendors = [
        ('VEND-001', 'TechSupply Co',   'sales@techsupply.com',   '+1-555-1001', '789 Tech Blvd',   'San Jose',  'USA'),
        ('VEND-002', 'OfficeGear Ltd',  'info@officegear.com',    '+1-555-1002', '321 Office Park',  'Austin',    'USA'),
        ('VEND-003', 'NetEquip Inc',    'support@netequip.com',   '+1-555-1003', '654 Network Dr',   'Seattle',   'USA'),
        ('VEND-004', 'FurniPro',        'orders@furnipro.de',     '+49-89-5555', 'Möbelweg 12',      'Munich',    'Germany'),
        ('VEND-005', 'PowerSystems AE', 'ps@powersys.ae',         '+971-2-8888', 'Industrial Zone',  'Abu Dhabi', 'UAE'),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO Vendors
            (VendorCode, VendorName, Email, Phone, AddressLine1, City, Country, CreatedAt)
        VALUES (?,?,?,?,?,?,?,?)
    """, [v + (now,) for v in vendors])

    # --- Sites ---
    sites = [
        ('SITE-HQ',  'Headquarters',       '1 Corporate Plaza', 'New York',    'USA',     'America/New_York'),
        ('SITE-WH1', 'Warehouse East',     '200 Logistics Ave', 'Newark',      'USA',     'America/New_York'),
        ('SITE-WH2', 'Warehouse West',     '800 Harbor Blvd',   'Los Angeles', 'USA',     'America/Los_Angeles'),
        ('SITE-EUR', 'Europe Office',      'Hauptstr. 5',       'Frankfurt',   'Germany', 'Europe/Berlin'),
        ('SITE-MEA', 'Middle East Office', 'Free Zone Unit 4',  'Dubai',       'UAE',     'Asia/Dubai'),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO Sites
            (SiteCode, SiteName, AddressLine1, City, Country, TimeZone, CreatedAt)
        VALUES (?,?,?,?,?,?,?)
    """, [s + (now,) for s in sites])

    # --- Locations ---
    locations = [
        (1, 'LOC-HQ-FL1',  'Floor 1 - Reception', None),
        (1, 'LOC-HQ-FL2',  'Floor 2 - IT Dept',   None),
        (2, 'LOC-WH1-A',   'Aisle A',             None),
        (2, 'LOC-WH1-B',   'Aisle B',             None),
        (3, 'LOC-WH2-A',   'Aisle A',             None),
        (4, 'LOC-EUR-OFF', 'Open Office',          None),
        (5, 'LOC-MEA-OFF', 'Main Office',          None),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO Locations
            (SiteId, LocationCode, LocationName, ParentLocationId, CreatedAt)
        VALUES (?,?,?,?,?)
    """, [l + (now,) for l in locations])

    # --- Items ---
    items = [
        ('ITM-LAP-001', 'Dell Latitude Laptop',   'IT Equipment', 'Each'),
        ('ITM-MON-001', 'HP 24" Monitor',         'IT Equipment', 'Each'),
        ('ITM-SWT-001', 'Cisco 24-Port Switch',   'Networking',   'Each'),
        ('ITM-CHR-001', 'Ergonomic Office Chair', 'Furniture',    'Each'),
        ('ITM-DSK-001', 'Standing Desk 160cm',    'Furniture',    'Each'),
        ('ITM-UPS-001', 'APC UPS 1500VA',         'Power',        'Each'),
        ('ITM-CAB-001', 'CAT6 Ethernet Cable 5m', 'Networking',   'Roll'),
        ('ITM-PRN-001', 'Canon Laser Printer',    'IT Equipment', 'Each'),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO Items
            (ItemCode, ItemName, Category, UnitOfMeasure, CreatedAt)
        VALUES (?,?,?,?,?)
    """, [i + (now,) for i in items])

    # --- Assets ---
    # Status: only 'Active' or 'Disposed'
    # Mix: mostly Active, some Disposed to support filtering scenarios
    statuses   = ['Active', 'Active', 'Active', 'Active', 'Disposed']  # 80% Active, 20% Disposed
    categories = ['IT Equipment', 'Networking', 'Furniture', 'Power']
    asset_names = [
        'Dell Latitude Laptop', 'HP Monitor', 'Cisco Switch',
        'Ergonomic Chair', 'Standing Desk', 'APC UPS', 'Canon Printer', 'Cisco Router'
    ]

    assets = []
    for i in range(1, 21):
        tag      = f'AST-{i:04d}'
        name     = random.choice(asset_names)
        site_id  = random.randint(1, 5)
        loc_id   = random.randint(1, 7)
        serial   = f'SN{random.randint(100000, 999999)}'
        category = random.choice(categories)
        status   = random.choice(statuses)
        cost     = round(random.uniform(200, 5000), 2)

        # Mix purchase dates: half from current year, half from previous years
        # This supports 'assets purchased this year' scenario
        if i <= 10:
            # Current year purchases
            days_into_year = random.randint(0, (today - datetime.date(current_year, 1, 1)).days)
            purchase = datetime.date(current_year, 1, 1) + datetime.timedelta(days=days_into_year)
        else:
            # Previous years purchases
            purchase = datetime.date(2021, 1, 1) + datetime.timedelta(days=random.randint(0, 700))

        vendor = random.randint(1, 5)
        assets.append((tag, name, site_id, loc_id, serial, category, status,
                       cost, purchase.isoformat(), vendor, now))

    cursor.executemany("""
        INSERT OR IGNORE INTO Assets
            (AssetTag, AssetName, SiteId, LocationId, SerialNumber, Category,
             Status, Cost, PurchaseDate, VendorId, CreatedAt)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, assets)

    # --- Bills ---
    # Statuses: Open, Paid, Overdue — spread across all 4 quarters
    bill_statuses = ['Open', 'Paid', 'Overdue']
    bills = []
    for i in range(1, 16):
        vendor_id   = random.randint(1, 5)
        bill_number = f'BILL-{i:04d}'

        # Spread bills across all 4 quarters of current year
        quarter     = ((i - 1) % 4)  # 0,1,2,3
        month_start = quarter * 3 + 1
        bill_date   = datetime.date(current_year, month_start, random.randint(1, 28))
        due_date    = bill_date + datetime.timedelta(days=30)
        amount      = round(random.uniform(500, 20000), 2)
        status      = random.choice(bill_statuses)
        bills.append((vendor_id, bill_number, bill_date.isoformat(),
                      due_date.isoformat(), amount, 'USD', status, now))

    cursor.executemany("""
        INSERT OR IGNORE INTO Bills
            (VendorId, BillNumber, BillDate, DueDate, TotalAmount, Currency, Status, CreatedAt)
        VALUES (?,?,?,?,?,?,?,?)
    """, bills)

    # --- Purchase Orders ---
    # Include Open POs to support 'open purchase orders' scenario
    po_statuses = ['Open', 'Open', 'Received', 'Cancelled']  # more Open for scenario coverage
    for i in range(1, 11):
        po_number = f'PO-{i:04d}'
        vendor_id = random.randint(1, 5)
        po_date   = (datetime.date(current_year, 1, 1) + datetime.timedelta(days=random.randint(0, 300))).isoformat()
        status    = random.choice(po_statuses)
        site_id   = random.randint(1, 5)
        cursor.execute("""
            INSERT OR IGNORE INTO PurchaseOrders
                (PONumber, VendorId, PODate, Status, SiteId, CreatedAt)
            VALUES (?,?,?,?,?,?)
        """, (po_number, vendor_id, po_date, status, site_id, now))

        po_id = cursor.lastrowid
        if po_id:
            for line in range(1, random.randint(2, 4)):
                item_id  = random.randint(1, 8)
                cursor.execute("SELECT ItemCode FROM Items WHERE ItemId=?", (item_id,))
                item_code = cursor.fetchone()[0]
                cursor.execute("""
                    INSERT OR IGNORE INTO PurchaseOrderLines
                        (POId, LineNumber, ItemId, ItemCode, Description, Quantity, UnitPrice)
                    VALUES (?,?,?,?,?,?,?)
                """, (po_id, line, item_id, item_code, f'Order of {item_code}',
                      random.randint(1, 20), round(random.uniform(50, 2000), 2)))

    # --- Sales Orders ---
    # Include orders from last month to support 'customer sales orders last month' scenario
    last_month       = today.replace(day=1) - datetime.timedelta(days=1)
    last_month_start = last_month.replace(day=1)

    so_statuses = ['Open', 'Shipped', 'Closed']
    for i in range(1, 11):
        so_number   = f'SO-{i:04d}'
        customer_id = random.randint(1, 5)
        status      = random.choice(so_statuses)
        site_id     = random.randint(1, 5)

        # First 4 SOs → last month, rest → random this year
        if i <= 4:
            days_in_month = (last_month - last_month_start).days
            so_date = last_month_start + datetime.timedelta(days=random.randint(0, days_in_month))
        else:
            so_date = datetime.date(current_year, 1, 1) + datetime.timedelta(days=random.randint(0, 300))

        cursor.execute("""
            INSERT OR IGNORE INTO SalesOrders
                (SONumber, CustomerId, SODate, Status, SiteId, CreatedAt)
            VALUES (?,?,?,?,?,?)
        """, (so_number, customer_id, so_date.isoformat(), status, site_id, now))

        so_id = cursor.lastrowid
        if so_id:
            for line in range(1, random.randint(2, 4)):
                item_id  = random.randint(1, 8)
                cursor.execute("SELECT ItemCode FROM Items WHERE ItemId=?", (item_id,))
                item_code = cursor.fetchone()[0]
                cursor.execute("""
                    INSERT OR IGNORE INTO SalesOrderLines
                        (SOId, LineNumber, ItemId, ItemCode, Description, Quantity, UnitPrice)
                    VALUES (?,?,?,?,?,?,?)
                """, (so_id, line, item_id, item_code, f'Sale of {item_code}',
                      random.randint(1, 10), round(random.uniform(100, 3000), 2)))

    # --- Asset Transactions ---
    txn_types = ['Transfer', 'Checkout', 'Return', 'Disposal', 'Acquisition']
    for i in range(1, 26):
        asset_id = random.randint(1, 20)
        from_loc = random.randint(1, 7)
        to_loc   = random.randint(1, 7)
        txn_type = random.choice(txn_types)
        txn_date = (datetime.datetime(current_year, 1, 1) +
                    datetime.timedelta(days=random.randint(0, 300))).strftime('%Y-%m-%d %H:%M:%S')
        note     = f'{txn_type} of asset AST-{asset_id:04d}'
        cursor.execute("""
            INSERT INTO AssetTransactions
                (AssetId, FromLocationId, ToLocationId, TxnType, Quantity, TxnDate, Note)
            VALUES (?,?,?,?,?,?,?)
        """, (asset_id, from_loc, to_loc, txn_type, 1, txn_date, note))

    print("Seed data inserted.")
    

def main():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    print(f"Setting up database: {DB_NAME}")
    create_schema(cursor)
    seed_data(cursor)

    conn.commit()
    conn.close()
    print(f"Done! Database ready at '{DB_NAME}'")


if __name__ == '__main__':
    main()