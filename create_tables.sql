CREATE TABLE qr_mapping (
	qr VARCHAR(50) PRIMARY KEY,
    mac_id VARCHAR(50)
);

CREATE TABLE ip_mapping (
    mac_id VARCHAR(50) PRIMARY KEY,
    ip_address VARCHAR(50)
);

CREATE TABLE app_status (
    mac_id VARCHAR(50) PRIMARY KEY,
    app_status VARCHAR(50)
);