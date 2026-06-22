-- ==========================================
-- Local Food Wastage Management System
-- SQL Analytical Queries Reference File
-- ==========================================

-- 1. Providers by City (Count of food providers in each city)
-- Helps understand the geographic distribution of food donation sources.
SELECT City, COUNT(*) as Provider_Count
FROM providers
GROUP BY City
ORDER BY Provider_Count DESC
LIMIT 15;

-- 2. Receivers by City (Count of food receivers in each city)
-- Helps locate the demand hubs and where receivers (NGOs/shelters) are located.
SELECT City, COUNT(*) as Receiver_Count
FROM receivers
GROUP BY City
ORDER BY Receiver_Count DESC
LIMIT 15;

-- 3. Most Contributing Provider (Top 10 providers by total quantity listed)
-- Identifies the major donors who list the highest quantities of surplus food.
SELECT p.Provider_ID, p.Name, p.Type, p.City, SUM(f.Quantity) as Total_Quantity_Donated
FROM food_listings f
JOIN providers p ON f.Provider_ID = p.Provider_ID
GROUP BY p.Provider_ID
ORDER BY Total_Quantity_Donated DESC
LIMIT 10;

-- 4. Most Claimed Food (Top food items by times claimed)
-- Identifies which food items are most sought after by receivers.
SELECT f.Food_Name, COUNT(c.Claim_ID) as Claims_Count, SUM(f.Quantity) as Total_Quantity
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY f.Food_Name
ORDER BY Claims_Count DESC
LIMIT 10;

-- 5. Total Food Quantity (Overall sum of food listed)
-- Displays the scale of total food listed for donation in the system.
SELECT SUM(Quantity) as Total_Food_Quantity
FROM food_listings;

-- 6. Top City by Food Listing (Total food listed per city)
-- Identifies cities with the highest volume of surplus food listings.
SELECT Location as City, COUNT(*) as Listings_Count, SUM(Quantity) as Total_Quantity
FROM food_listings
GROUP BY Location
ORDER BY Total_Quantity DESC
LIMIT 10;

-- 7. Most Common Food Type (Vegan vs. Vegetarian vs. Non-Vegetarian)
-- Helps analyze nutritional/dietary preference distribution of donations.
SELECT Food_Type, COUNT(*) as Listings_Count, SUM(Quantity) as Total_Quantity
FROM food_listings
GROUP BY Food_Type
ORDER BY Total_Quantity DESC;

-- 8. Claims per Food Item (Most claimed individual listings)
-- Shows which specific food listings received the highest number of claims.
SELECT f.Food_ID, f.Food_Name, f.Quantity, p.Name as Provider_Name,
       (SELECT COUNT(*) FROM claims WHERE Food_ID = f.Food_ID) as Claims_Count
FROM food_listings f
JOIN providers p ON f.Provider_ID = p.Provider_ID
ORDER BY Claims_Count DESC
LIMIT 10;

-- 9. Provider with Most Successful Claims (Top 10 providers by completed claims)
-- Highlights the most reliable providers whose listed food actually reaches receivers.
SELECT p.Provider_ID, p.Name, p.Type, p.City, COUNT(c.Claim_ID) as Successful_Claims
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
JOIN providers p ON f.Provider_ID = p.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Provider_ID
ORDER BY Successful_Claims DESC
LIMIT 10;

-- 10. Claim Status Percentage (Completed vs. Pending vs. Cancelled)
-- Measures the overall efficiency of food reclamation (how much gets reclaimed vs wasted).
SELECT Status, COUNT(*) as Claim_Count, 
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) as Percentage
FROM claims
GROUP BY Status;

-- 11. Average Quantity Claimed (Per successful transaction)
-- Shows the average volume of food distributed in a successful claim.
SELECT ROUND(AVG(f.Quantity), 2) as Avg_Quantity_Claimed
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed';

-- 12. Most Claimed Meal Type (Breakfast vs. Lunch vs. Dinner vs. Snacks)
-- Helps understand temporal peak times of food demand.
SELECT f.Meal_Type, COUNT(c.Claim_ID) as Claims_Count
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY f.Meal_Type
ORDER BY Claims_Count DESC;

-- 13. Total Donated Quantity by Provider Type
-- Analyzes which sectors (e.g., Restaurants vs. Supermarkets) contribute the most.
SELECT Provider_Type, SUM(Quantity) as Total_Quantity, COUNT(*) as Listings_Count
FROM food_listings
GROUP BY Provider_Type
ORDER BY Total_Quantity DESC;

-- 14. Top Receivers by Successful Claims (Top 10 receivers by completed claims)
-- Recognizes key receivers, such as active NGOs, that are successfully distributing food.
SELECT r.Receiver_ID, r.Name, r.Type, r.City, COUNT(c.Claim_ID) as Completed_Claims, SUM(f.Quantity) as Total_Quantity_Claimed
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
JOIN food_listings f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed'
GROUP BY r.Receiver_ID
ORDER BY Completed_Claims DESC
LIMIT 10;

-- 15. City with Highest Food Demand (Top 10 cities by number of claims made)
-- Pinpoints high-need areas where hunger alleviation and NGO expansion are most needed.
SELECT r.City, COUNT(c.Claim_ID) as Claims_Count, SUM(f.Quantity) as Total_Quantity_Requested
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY r.City
ORDER BY Claims_Count DESC
LIMIT 10;

-- 16. Total Listings vs Claimed Status (General system efficiency)
-- Provides a high-level balance sheet of total food listings and their ultimate outcomes.
SELECT 
    COUNT(f.Food_ID) as Total_Listings,
    SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) as Completed_Claims,
    SUM(CASE WHEN c.Status = 'Pending' THEN 1 ELSE 0 END) as Pending_Claims,
    SUM(CASE WHEN c.Status = 'Cancelled' OR c.Status IS NULL THEN 1 ELSE 0 END) as Wasted_Unclaimed_Listings
FROM food_listings f
LEFT JOIN claims c ON f.Food_ID = c.Food_ID;
