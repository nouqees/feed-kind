-- Reference schema matching the SQLAlchemy models.
-- Normally you won't run this file directly — `flask --app app init-db`
-- creates these same tables automatically. Kept here for documentation
-- and for anyone who prefers to create the tables manually.

CREATE DATABASE IF NOT EXISTS food_waste_db;
USE food_waste_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    role VARCHAR(10) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE food_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE food_donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    food_name VARCHAR(120) NOT NULL,
    category_id INT NOT NULL,
    quantity VARCHAR(50) NOT NULL,
    prepared_at DATETIME NOT NULL,
    available_until DATETIME NOT NULL,
    pickup_location TEXT NOT NULL,
    description TEXT,
    image_path VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'Available',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES food_categories(id)
);

CREATE TABLE donation_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donation_id INT NOT NULL,
    ngo_id INT NOT NULL,
    requested_quantity VARCHAR(50) NOT NULL,
    message TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    requested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donation_id) REFERENCES food_donations(id),
    FOREIGN KEY (ngo_id) REFERENCES users(id)
);

CREATE TABLE donation_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donation_id INT NOT NULL UNIQUE,
    request_id INT NOT NULL UNIQUE,
    completed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT,
    FOREIGN KEY (donation_id) REFERENCES food_donations(id),
    FOREIGN KEY (request_id) REFERENCES donation_requests(id)
);
