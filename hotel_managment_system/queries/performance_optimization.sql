-- Create indexes for better performance
CREATE INDEX IX_Reservations_CheckInCheckOut ON Reservations(check_in_date, check_out_date);
CREATE INDEX IX_Reservations_GuestId ON Reservations(guest_id);
CREATE INDEX IX_Reservations_RoomId ON Reservations(room_id);
CREATE INDEX IX_Guests_Email ON Guests(email);
CREATE INDEX IX_Payments_ReservationId ON Payments(reservation_id);

-- Query performance analysis
SET STATISTICS IO ON;
SET STATISTICS TIME ON;

-- Your query here
SELECT * FROM Reservations WHERE check_in_date >= '2024-01-01';