-- Monthly Revenue Report
SELECT 
    YEAR(r.check_in_date) AS Year,
    MONTH(r.check_in_date) AS Month,
    COUNT(r.reservation_id) AS Total_Reservations,
    SUM(r.total_amount) AS Total_Revenue,
    AVG(r.total_amount) AS Average_Booking_Value
FROM Reservations r
WHERE r.status = 'Completed'
GROUP BY YEAR(r.check_in_date), MONTH(r.check_in_date)
ORDER BY Year, Month;

-- Occupancy Rate Analysis
SELECT 
    h.hotel_name,
    COUNT(DISTINCT r.room_id) AS Total_Rooms,
    COUNT(DISTINCT res.room_id) AS Occupied_Rooms,
    CAST(COUNT(DISTINCT res.room_id) AS FLOAT) / COUNT(DISTINCT r.room_id) * 100 AS Occupancy_Rate
FROM Hotels h
LEFT JOIN Rooms r ON h.hotel_id = r.hotel_id
LEFT JOIN Reservations res ON r.room_id = res.room_id 
    AND GETDATE() BETWEEN res.check_in_date AND res.check_out_date
    AND res.status = 'Confirmed'
GROUP BY h.hotel_id, h.hotel_name;

-- Guest Loyalty Analysis
SELECT 
    CASE WHEN loyalty_member = 1 THEN 'Loyalty Member' ELSE 'Regular Guest' END AS Guest_Type,
    COUNT(*) AS Total_Guests,
    AVG(res.total_amount) AS Average_Spend,
    COUNT(res.reservation_id) AS Total_Bookings
FROM Guests g
LEFT JOIN Reservations res ON g.guest_id = res.guest_id
GROUP BY loyalty_member;