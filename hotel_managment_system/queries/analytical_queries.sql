-- Peak Season Analysis
WITH MonthlyBookings AS (
    SELECT 
        MONTH(check_in_date) AS Month,
        COUNT(*) AS Bookings,
        SUM(total_amount) AS Revenue
    FROM Reservations
    WHERE YEAR(check_in_date) = YEAR(GETDATE())
    GROUP BY MONTH(check_in_date)
)
SELECT 
    Month,
    Bookings,
    Revenue,
    RANK() OVER (ORDER BY Revenue DESC) AS Revenue_Rank
FROM MonthlyBookings;

-- Guest Segmentation by Spending
WITH GuestSpending AS (
    SELECT 
        g.guest_id,
        g.first_name + ' ' + g.last_name AS guest_name,
        COUNT(r.reservation_id) AS total_stays,
        SUM(r.total_amount) AS total_spent,
        AVG(r.total_amount) AS avg_booking_value
    FROM Guests g
    LEFT JOIN Reservations r ON g.guest_id = r.guest_id
    WHERE r.status = 'Completed'
    GROUP BY g.guest_id, g.first_name, g.last_name
)
SELECT 
    guest_name,
    total_stays,
    total_spent,
    CASE 
        WHEN total_spent > 1000 THEN 'VIP'
        WHEN total_spent > 500 THEN 'Loyal'
        WHEN total_spent > 100 THEN 'Regular'
        ELSE 'Occasional'
    END AS guest_segment
FROM GuestSpending
ORDER BY total_spent DESC;