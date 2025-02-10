

-- 1. Retrieve all sports disciplines and their corresponding seasons:
SELECT DISTINCT Discipline, Season
FROM Sports
ORDER BY Season, Discipline;

-- 2. Find the host city and details of the Olympiad for a given year:
SELECT Years, Host_City, Nations, Athletes
FROM Olympiad
WHERE Years = 2020;

-- 3. Get the total medal count for each country in a specific year:
SELECT Team, Gold, Silver, Bronze, Total
FROM CountryMedals
WHERE Years = 2008
ORDER BY Total DESC;

-- 4. List all athletes and their medal counts for a given Olympiad year:
SELECT Athlete_Name, Gold, Silver, Bronze, Total
FROM AthletesMedals
WHERE Years = 2004
ORDER BY Total DESC;

-- 5. Summarize the total number of medals won by each continent in a specific year:
SELECT Continent, SUM(Gold) as Total_Gold, SUM(Silver) as Total_Silver,SUM(Bronze) as Total_Bronze, SUM(Total) as Grand_Total
FROM ContinentalMedals
WHERE Years = 2012
GROUP BY Continent
ORDER BY Grand_Total DESC; 

-- 6. Compare the performance of a specific country across all Olympics:
SELECT cm.Team, cm.Gold, cm.Silver, cm.Bronze, cm.Total, o.Years, o.Host_City
FROM CountryMedals cm
JOIN Olympiad o ON cm.Years = o.Years
WHERE cm.Team = 'United States'
ORDER BY o.Years;

-- 7. Identify the top-ranked continent based on total medals for a given year: 
SELECT Continent, Gold, Silver, Bronze, Total
FROM ContinentalMedals
WHERE Years = 2016
AND Position = '1';

-- 8. Find the Olympics with the highest number of participating nations and athletes:
SELECT o.Years, o.Host_City, o.Nations, o.Athletes, cm.Gold, cm.Silver, cm.Bronze, cm.Total
FROM Olympiad o
LEFT JOIN ContinentalMedals cm ON o.Years = cm.Years AND cm.Continent = 'Asia'
ORDER BY o.Nations DESC, o.Athletes DESC
LIMIT 1;

-- 9. List the top athletes with their medal counts and the corresponding Olympic host city:
SELECT am.Athlete_Name, am.Gold, am.Silver, am.Bronze, am.Total, o.Host_City, o.Years
FROM AthletesMedals am
JOIN Olympiad o ON am.Years = o.Years
ORDER BY am.Total DESC
LIMIT 10;