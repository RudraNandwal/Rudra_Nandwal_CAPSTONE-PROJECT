
# FINDING NUMBER OF TOTAL ORDERS, CALCULATING TOTAL REVENUE AND AVERAGE ORDER VALUE, TASK3: (A)
# OUTPUT : total_orders- 180, total_revenue- 99860.20, avg_order_value- 554.78
SELECT COUNT(*) AS total_orders,
    ROUND( SUM( o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100)), 2) AS total_revenue,
    ROUND( AVG( o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100)), 2) AS avg_order_value
FROM orders o
JOIN products p
    ON o.product_id = p.product_id;
    
# FINDING NUMBERS OF TOTAL ORDERS, RATED ORDERS AND UN-RATED ORDERS, TASK3: (B)
# OUTPUT: total_orders- 180, rated_orders- 165, unrated_orders- 15
SELECT
    COUNT(*) AS total_orders,
    COUNT(rating) AS rated_orders,
    COUNT(*) - COUNT(rating) AS unrated_orders
FROM orders;

# FINDING CUSTOMERS WITH ZERO ORDERS USING [LEFT JOIN], TASK3: (C)
# OUTPUT: customer_id- C045, name- Vihaan
SELECT
    c.customer_id, c.name
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id, c.name
HAVING COUNT(o.order_id) = 0;

# FINDING CUSTOMERS WITH ZERO ORDERS USING [NOT IN], TASK3: (C)
# OUTPUT: customer_id- C045, name- Vihaan
SELECT
    c.customer_id, c.name
FROM customers c
WHERE c.customer_id NOT IN (
    SELECT DISTINCT customer_id
    FROM orders );
    
# CALCULATING THE RETURN RATE(CITY WISE) AND EXCLUDING CITIES WHICH HAS RETURN RATE >20, TASK3: (D)
# OUTPUT: city     total_orders    returned_orders    return_rate_pct
#        Jaipur         19                8                   42.1
#       Lucknow         49                15                  30.6
#      Bangalore        33                8                   24.2
SELECT
    c.city,
    COUNT(*) AS total_orders, SUM(o.returned) AS returned_orders,
    ROUND(
        SUM(o.returned) * 100.0 / COUNT(*), 1) AS return_rate_pct
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20
ORDER BY return_rate_pct DESC;

# RANKING TOP 5 CUSTOMERS BY THIER TOTAL SPEND, TASK 3:(E)
# OUTPUT:   customer_id     name     total_spend
#              C043       Reyansh     12920.00
#              C026        Isha        8371.60
#              C008        Meera       4564.60
#              C011        Arjun       4111.00
#              C042        Sanya       3785.00
SELECT
    c.customer_id,
    c.name,
    ROUND(
        SUM(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100)), 2) AS total_spend
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY
    c.customer_id, c.name
ORDER BY
    total_spend DESC, c.customer_id ASC
LIMIT 5;

# USING [LIMIT 3 OFFSET 2] IN THE SAME TASK TO FIND TOP 3-5 (LAST 3 OF TOP 5), TASK 3:(E)
# OUTPUT:  customer_id     name    total_spend
#              C008        Meera       4564.60
#              C011        Arjun       4111.00
#              C042        Sanya       3785.00     
SELECT
    c.customer_id,
    c.name,
    ROUND(
        SUM(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100)), 2) AS total_spend
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY
    c.customer_id, c.name
ORDER BY
    total_spend DESC, c.customer_id ASC
LIMIT 3 OFFSET 2;

# FINDING TOTAL ORDERS AND REVENUE, CATEGORY WISE, TASK 3: (F)
# OUTPUT:       category    order_count  category_revenue
#               Haircare	    54	        44956.10
#               Skincare	    60	        27346.00
#               Babycare	    30	        16805.00
#              PersonalCare 	36	        10753.10
SELECT
    p.category,
    COUNT(*) AS order_count,
    ROUND(
        SUM(o.quantity * p.price *(1 - COALESCE(o.discount_pct, 0) / 100)), 2) AS category_revenue
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY p.category
ORDER BY category_revenue DESC;

# FINDING CUSTOMERS WHOSE NAME STARTS WITH 'A' USING [LIKE A], TASK 3: (G)
# OUTPUT:  customer_id    name
#             C001	      Aarav
#             C003	      Aditi
#             C004	      Ananya
#             C011	      Arjun
#             C021	      Aryan
#             C030     	  Anika
#             C031	      Aditya
#             C036	      Aisha
#             C041   	    Ayaan
#             C044	      Aria
SELECT
    customer_id, name
FROM customers
WHERE name LIKE 'A%';

# FINDING DISCTINT SOURCES OF CUSTOMER ACQUISITION, TASK 3 : (H)
# OUTPUT:  acquisition_source
#              Organic
#             Referral
#                Ad
#              Social
SELECT DISTINCT acquisition_source
FROM customers;

# ADDING A ADDITIONAL COLUMN IN CUSTOMERS COLUMN AS TIER, TASK 3: (I)
# OUTPUT:    loyalty_tier     customer_count
#               Gold               28
#              Silver              17
  # ADDING THE TIER COLUMN.
ALTER TABLE customers
ADD COLUMN loyalty_tier VARCHAR(10);

  # RATING CUSTOMERS BY GOLD AND SILVER BASED ON THEIR CITY_TIER [IF CITY_TIER 1, THEN GOLD ELSE SILVER]
UPDATE customers
SET loyalty_tier = CASE
    WHEN city_tier = 1 THEN 'Gold'
    ELSE 'Silver'
END;
  # FINDING NUMBER OF CUSTOMERS WITH GOLD AND SILVER LOYALTY_TIER.
SELECT
    loyalty_tier,
    COUNT(*) AS customer_count
FROM customers
GROUP BY loyalty_tier;
