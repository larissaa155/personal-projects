-- Procedure to make a reservation
CREATE PROCEDURE MakeReservation
    @guest_id INT,
    @room_id INT,
    @check_in_date DATE,
    @check_out_date DATE,
    @adults INT = 1,
    @children INT = 0
AS
BEGIN
    DECLARE @room_price DECIMAL(10,2);
    DECLARE @nights INT;
    DECLARE @total_amount DECIMAL(10,2);
    
    -- Calculate nights and total amount
    SET @nights = DATEDIFF(DAY, @check_in_date, @check_out_date);
    
    SELECT @room_price = rt.base_price
    FROM Rooms r
    JOIN RoomTypes rt ON r.room_type_id = rt.room_type_id
    WHERE r.room_id = @room_id;
    
    SET @total_amount = @room_price * @nights;
    
    -- Insert reservation
    INSERT INTO Reservations (guest_id, room_id, check_in_date, check_out_date, adults, children, total_amount)
    VALUES (@guest_id, @room_id, @check_in_date, @check_out_date, @adults, @children, @total_amount);
    
    -- Update room status
    UPDATE Rooms SET status = 'Occupied' WHERE room_id = @room_id;
    
    SELECT SCOPE_IDENTITY() AS new_reservation_id;
END;

-- Procedure to check room availability
CREATE PROCEDURE CheckRoomAvailability
    @hotel_id INT,
    @check_in_date DATE,
    @check_out_date DATE,
    @room_type_id INT = NULL
AS
BEGIN
    SELECT 
        r.room_id,
        r.room_number,
        rt.type_name,
        rt.base_price,
        rt.capacity
    FROM Rooms r
    JOIN RoomTypes rt ON r.room_type_id = rt.room_type_id
    WHERE r.hotel_id = @hotel_id
        AND r.status = 'Available'
        AND (@room_type_id IS NULL OR r.room_type_id = @room_type_id)
        AND r.room_id NOT IN (
            SELECT res.room_id
            FROM Reservations res
            WHERE res.status = 'Confirmed'
                AND (@check_in_date BETWEEN res.check_in_date AND res.check_out_date
                     OR @check_out_date BETWEEN res.check_in_date AND res.check_out_date
                     OR res.check_in_date BETWEEN @check_in_date AND @check_out_date)
        );
END;