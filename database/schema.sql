PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS units (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    sector TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    capacity REAL NOT NULL,
    weather_id INTEGER
);

CREATE TABLE IF NOT EXISTS weather (
    id INTEGER PRIMARY KEY,
    location TEXT NOT NULL,
    condition TEXT NOT NULL,
    temperature REAL NOT NULL,
    impact TEXT NOT NULL,
    impact_score REAL NOT NULL,
    observed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS depots (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    fuel REAL NOT NULL,
    food REAL NOT NULL,
    water REAL NOT NULL,
    medical REAL NOT NULL,
    spare_parts REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    resource TEXT NOT NULL,
    category TEXT NOT NULL,
    unit TEXT NOT NULL,
    available REAL NOT NULL,
    required REAL NOT NULL,
    safety_stock REAL NOT NULL,
    daily_consumption REAL NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES units(id)
);

CREATE TABLE IF NOT EXISTS consumption_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    resource TEXT NOT NULL,
    day TEXT NOT NULL,
    quantity REAL NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES units(id)
);

CREATE TABLE IF NOT EXISTS routes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    origin_id INTEGER NOT NULL,
    destination_unit_id INTEGER NOT NULL,
    distance_km REAL NOT NULL,
    duration_hours REAL NOT NULL,
    risk_score REAL NOT NULL,
    weather_score REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (origin_id) REFERENCES depots(id),
    FOREIGN KEY (destination_unit_id) REFERENCES units(id)
);

CREATE TABLE IF NOT EXISTS convoys (
    id INTEGER PRIMARY KEY,
    convoy_id TEXT NOT NULL,
    origin_id INTEGER NOT NULL,
    destination_unit_id INTEGER NOT NULL,
    cargo TEXT NOT NULL,
    quantity REAL NOT NULL,
    departure_time TEXT NOT NULL,
    eta TEXT NOT NULL,
    status TEXT NOT NULL,
    delay_hours REAL NOT NULL,
    risk_score REAL NOT NULL,
    FOREIGN KEY (origin_id) REFERENCES depots(id),
    FOREIGN KEY (destination_unit_id) REFERENCES units(id)
);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER,
    resource TEXT,
    predicted_daily REAL,
    shortage_hours REAL,
    risk_score REAL,
    confidence REAL,
    created_at TEXT,
    FOREIGN KEY (unit_id) REFERENCES units(id)
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    severity TEXT NOT NULL,
    unit_id INTEGER,
    resource TEXT,
    reason TEXT NOT NULL,
    action TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES units(id)
);

CREATE TABLE IF NOT EXISTS simulation_state (
    id INTEGER PRIMARY KEY,
    tick INTEGER NOT NULL DEFAULT 0,
    running INTEGER NOT NULL DEFAULT 0,
    mode TEXT NOT NULL DEFAULT 'IDLE',
    updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_inventory_unit
    ON inventory(unit_id);

CREATE INDEX IF NOT EXISTS idx_history_unit_resource
    ON consumption_history(unit_id, resource);

CREATE INDEX IF NOT EXISTS idx_convoys_destination
    ON convoys(destination_unit_id);

CREATE INDEX IF NOT EXISTS idx_alerts_unit_resource
    ON alerts(unit_id, resource);
