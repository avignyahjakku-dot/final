-- ==============================================================
-- Smart Lost & Found System - Database Schema
-- Database: smart_lost_found
-- Team of 2 BTech CSE Students Project
-- ==============================================================

CREATE DATABASE IF NOT EXISTS smart_lost_found;
USE smart_lost_found;

-- Drop tables in reverse order of foreign key dependency
DROP TABLE IF EXISTS Matches;
DROP TABLE IF EXISTS Items;
DROP TABLE IF EXISTS Users;

-- --------------------------------------------------------------
-- 1. Users Table
-- Stores student and administrator credentials & profile information
-- --------------------------------------------------------------
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    student_id VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin') NOT NULL DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------------
-- 2. Items Table
-- Stores lost and found item reports submitted by students
-- --------------------------------------------------------------
CREATE TABLE Items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    report_type ENUM('Lost', 'Found') NOT NULL,
    image_path VARCHAR(255) DEFAULT NULL,
    status ENUM('Pending', 'Claimed', 'Resolved') NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_items_user FOREIGN KEY (user_id) 
        REFERENCES Users(user_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------------
-- 3. Matches Table
-- Stores automatically and manually identified matches
-- --------------------------------------------------------------
CREATE TABLE Matches (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    lost_item_id INT NOT NULL,
    found_item_id INT NOT NULL,
    match_reason VARCHAR(255) NOT NULL,
    match_status ENUM('Potential', 'Confirmed', 'Rejected') NOT NULL DEFAULT 'Potential',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_matches_lost FOREIGN KEY (lost_item_id) 
        REFERENCES Items(item_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_matches_found FOREIGN KEY (found_item_id) 
        REFERENCES Items(item_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------------
-- Indexes for optimized querying
-- --------------------------------------------------------------
CREATE INDEX idx_items_category ON Items(category);
CREATE INDEX idx_items_location ON Items(location);
CREATE INDEX idx_items_report_type ON Items(report_type);
CREATE INDEX idx_items_status ON Items(status);

-- --------------------------------------------------------------
-- Sample Data (Pre-hashed passwords using Werkzeug generate_password_hash)
-- Password for all sample users is 'password123'
-- Admin: admin@campus.edu / admin123
-- --------------------------------------------------------------

-- Insert Users
INSERT INTO Users (user_id, name, email, student_id, password, role) VALUES
(1, 'Campus Admin', 'admin@campus.edu', 'ADM-001', 'scrypt:32768:8:1$5e8c14831201$192e2760bf00827a514d2e1b123616641e7845fef2e63c0be8b082adad48687258380486c9f809d4378f8cb0a761ec81e3a4fb3d726615b3c3b06ad941a87e07', 'admin'),
(2, 'Aarav Sharma', 'aarav.sharma@campus.edu', '23BCSE101', 'scrypt:32768:8:1$5e8c14831201$192e2760bf00827a514d2e1b123616641e7845fef2e63c0be8b082adad48687258380486c9f809d4378f8cb0a761ec81e3a4fb3d726615b3c3b06ad941a87e07', 'student'),
(3, 'Diya Patel', 'diya.patel@campus.edu', '23BCSE102', 'scrypt:32768:8:1$5e8c14831201$192e2760bf00827a514d2e1b123616641e7845fef2e63c0be8b082adad48687258380486c9f809d4378f8cb0a761ec81e3a4fb3d726615b3c3b06ad941a87e07', 'student'),
(4, 'Rohan Verma', 'rohan.verma@campus.edu', '23BCSE103', 'scrypt:32768:8:1$5e8c14831201$192e2760bf00827a514d2e1b123616641e7845fef2e63c0be8b082adad48687258380486c9f809d4378f8cb0a761ec81e3a4fb3d726615b3c3b06ad941a87e07', 'student'),
(5, 'Ananya Iyer', 'ananya.iyer@campus.edu', '23BCSE104', 'scrypt:32768:8:1$5e8c14831201$192e2760bf00827a514d2e1b123616641e7845fef2e63c0be8b082adad48687258380486c9f809d4378f8cb0a761ec81e3a4fb3d726615b3c3b06ad941a87e07', 'student');

-- Insert Items (Lost and Found pairs designed to showcase matching & DSA search)
INSERT INTO Items (item_id, user_id, item_name, category, description, location, date, report_type, image_path, status) VALUES
(1, 2, 'Dell XPS 13 Laptop', 'Electronics', 'Silver Dell laptop with anime sticker on cover. Left in CS Lab 3 desk.', 'Computer Lab 3', '2026-10-28', 'Lost', NULL, 'Pending'),
(2, 3, 'Dell Laptop (Silver)', 'Electronics', 'Found a silver 13-inch Dell laptop on the back row of computer lab 3.', 'Computer Lab 3', '2026-10-28', 'Found', NULL, 'Pending'),
(3, 4, 'Black Leather Wallet', 'Bags & Wallets', 'Contains College ID card, debit card, and cash. Lost near Central Cafeteria.', 'Central Cafeteria', '2026-10-29', 'Lost', NULL, 'Pending'),
(4, 5, 'Leather Wallet (Black)', 'Bags & Wallets', 'Black men wallet picked up from lunch table at cafeteria with college ID.', 'Central Cafeteria', '2026-10-29', 'Found', NULL, 'Pending'),
(5, 2, 'Casio fx-991EX Calculator', 'Electronics', 'ClassWiz scientific calculator with name written on the back cover.', 'Main Auditorium', '2026-10-30', 'Lost', NULL, 'Pending'),
(6, 3, 'Casio Scientific Calculator', 'Electronics', 'Found scientific calculator after Calculus exam in auditorium seat 42.', 'Main Auditorium', '2026-10-30', 'Found', NULL, 'Pending'),
(7, 4, 'Boat Airdopes 141 Case', 'Electronics', 'Matte black charging case with white earbuds inside. Lost in Library 2nd floor.', 'Central Library', '2026-10-31', 'Lost', NULL, 'Pending'),
(8, 5, 'Campus ID Card 23BCSE103', 'ID & Cards', 'Found identity card of Rohan Verma near Sports Complex cricket ground.', 'Sports Complex', '2026-11-01', 'Found', NULL, 'Pending'),
(9, 2, 'C++ Data Structures Textbook', 'Books & Notes', 'Author Mark Allen Weiss, blue cover, bookmarked with sticky notes.', 'Central Library', '2026-11-01', 'Lost', NULL, 'Pending'),
(10, 3, 'Water Bottle (Milton 1L)', 'Others', 'Blue stainless steel Milton thermosteel flask found in Seminar Hall 1.', 'Seminar Hall 1', '2026-11-02', 'Found', NULL, 'Pending');

-- Insert Pre-computed Matches
INSERT INTO Matches (match_id, lost_item_id, found_item_id, match_reason, match_status) VALUES
(1, 1, 2, 'Matching category Electronics, similar item Dell Laptop, location Computer Lab 3, same date 2026-10-28', 'Potential'),
(2, 3, 4, 'Matching category Bags & Wallets, similar item Leather Wallet, location Central Cafeteria, same date 2026-10-29', 'Potential'),
(3, 5, 6, 'Matching category Electronics, similar item Casio Calculator, location Main Auditorium, same date 2026-10-30', 'Potential');
