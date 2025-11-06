-- Insert sample data
INSERT INTO Hotels (hotel_name, address, city, state, phone, email) VALUES
('Grand Plaza Hotel', '123 Main Street', 'New York', 'NY', '212-555-0100', 'info@grandplaza.com'),
('Ocean View Resort', '456 Beach Blvd', 'Miami', 'FL', '305-555-0200', 'reservations@oceanview.com');

INSERT INTO RoomTypes (type_name, description, base_price, capacity) VALUES
('Standard', 'Comfortable room with basic amenities', 99.99, 2),
('Deluxe', 'Spacious room with premium features', 149.99, 3),
('Suite', 'Luxurious suite with separate living area', 249.99, 4);

INSERT INTO Rooms (hotel_id, room_number, room_type_id, floor, status) VALUES
(1, '101', 1, 1, 'Available'),
(1, '102', 1, 1, 'Available'),
(1, '201', 2, 2, 'Available'),
(1, '301', 3, 3, 'Available');

INSERT INTO Guests (first_name, last_name, email, phone, loyalty_member) VALUES
('John', 'Smith', 'john.smith@email.com', '555-0101', 1),
('Sarah', 'Johnson', 'sarah.j@email.com', '555-0102', 0),
('Mike', 'Davis', 'mike.davis@email.com', '555-0103', 1);