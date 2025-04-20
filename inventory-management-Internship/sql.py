CREATE DATABASE IF NOT EXISTS inventory_db;

USE inventory_db;

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    stock INT NOT NULL,
    threshold INT NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    last_updated DATETIME NOT NULL
);