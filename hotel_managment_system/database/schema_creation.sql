-- Create Database
CREATE DATABASE HotelManagement;
USE HotelManagement;

-- Core Tables
CREATE TABLE Hotels (
    hotel_id INT PRIMARY KEY IDENTITY(1,1),
    hotel_name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    city VARCHAR(50),
    state VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE RoomTypes (
    room_type_id INT PRIMARY KEY IDENTITY(1,1),
    type_name VARCHAR(50) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2) NOT NULL,
    capacity INT NOT NULL
);

CREATE TABLE Rooms (
    room_id INT PRIMARY KEY IDENTITY(1,1),
    hotel_id INT FOREIGN KEY REFERENCES Hotels(hotel_id),
    room_number VARCHAR(10) NOT NULL,
    room_type_id INT FOREIGN KEY REFERENCES RoomTypes(room_type_id),
    floor INT,
    status VARCHAR(20) DEFAULT 'Available',
    UNIQUE(hotel_id, room_number)
);

CREATE TABLE Guests (
    guest_id INT PRIMARY KEY IDENTITY(1,1),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    date_of_birth DATE,
    loyalty_member BIT DEFAULT 0
);

CREATE TABLE Reservations (
    reservation_id INT PRIMARY KEY IDENTITY(1,1),
    guest_id INT FOREIGN KEY REFERENCES Guests(guest_id),
    room_id INT FOREIGN KEY REFERENCES Rooms(room_id),
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    adults INT DEFAULT 1,
    children INT DEFAULT 0,
    total_amount DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'Confirmed',
    created_date DATETIME DEFAULT GETDATE()
);

CREATE TABLE Payments (
    payment_id INT PRIMARY KEY IDENTITY(1,1),
    reservation_id INT FOREIGN KEY REFERENCES Reservations(reservation_id),
    payment_date DATETIME DEFAULT GETDATE(),
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    transaction_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Completed'
);

CREATE TABLE Staff (
    staff_id INT PRIMARY KEY IDENTITY(1,1),
    hotel_id INT FOREIGN KEY REFERENCES Hotels(hotel_id),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    position VARCHAR(50),
    hire_date DATE,
    salary DECIMAL(10,2)
);