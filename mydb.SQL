CREATE TABLE command_history (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    client_id INTEGER,
    command TEXT,
    result TEXT,
    status VARCHAR(20)
);

CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(10), -- INFO, ERROR, WARN
    source VARCHAR(50), -- ListenThread, CLI, Handshake
    message TEXT,
    client_addr TEXT -- IP adress of client involved, if applicable
);