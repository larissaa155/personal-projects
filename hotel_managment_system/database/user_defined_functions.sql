-- Function to calculate total revenue for a guest
CREATE FUNCTION CalculateGuestLifetimeValue(@guest_id INT)
RETURNS DECIMAL(10,2)
AS
BEGIN
    DECLARE @total_revenue DECIMAL(10,2);
    
    SELECT @total_revenue = COALESCE(SUM(total_amount), 0)
    FROM Reservations
    WHERE guest_id = @guest_id
        AND status = 'Completed';
    
    RETURN @total_revenue;
END;

-- Function to get room occupancy for a date range
CREATE FUNCTION GetRoomOccupancy(@room_id INT, @start_date DATE, @end_date DATE)
RETURNS INT
AS
BEGIN
    DECLARE @occupied_days INT;
    
    SELECT @occupied_days = COALESCE(SUM(
        CASE 
            WHEN check_in_date >= @start_date AND check_out_date <= @end_date THEN DATEDIFF(DAY, check_in_date, check_out_date)
            WHEN check_in_date < @start_date AND check_out_date > @end_date THEN DATEDIFF(DAY, @start_date, @end_date)
            WHEN check_in_date < @start_date THEN DATEDIFF(DAY, @start_date, check_out_date)
            WHEN check_out_date > @end_date THEN DATEDIFF(DAY, check_in_date, @end_date)
        END
    ), 0)
    FROM Reservations
    WHERE room_id = @room_id
        AND status = 'Completed'
        AND check_in_date <= @end_date
        AND check_out_date >= @start_date;
    
    RETURN @occupied_days;
END;