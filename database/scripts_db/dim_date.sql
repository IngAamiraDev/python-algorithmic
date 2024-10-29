-- Create the dim_date table
CREATE TABLE dim_date (
    date_key DATE PRIMARY KEY,
    year INT,
    quarter INT,
    month INT,
    day INT,
    day_of_week INT,
    day_name TEXT,
    month_name TEXT,
    quarter_name TEXT,
    is_weekend BOOLEAN,
    week_of_month TEXT,
    is_holiday BOOLEAN
);

-- Populate the dim_date table with dates
-- Adjust the start_date and end_date as needed
WITH RECURSIVE date_range AS (
    SELECT '2020-01-01'::DATE AS date_key
    UNION ALL
    SELECT (date_key + INTERVAL '1 day')::DATE
    FROM date_range
    WHERE (date_key + INTERVAL '1 day')::DATE <= '2030-12-31'
)
INSERT INTO dim_date (date_key, year, quarter, month, day, day_of_week, day_name, month_name, quarter_name, is_weekend)
SELECT
    date_key,
    EXTRACT(YEAR FROM date_key) AS year,
    EXTRACT(QUARTER FROM date_key) AS quarter,
    EXTRACT(MONTH FROM date_key) AS month,
    EXTRACT(DAY FROM date_key) AS day,
    EXTRACT(DOW FROM date_key) AS day_of_week,
    TO_CHAR(date_key, 'Day') AS day_name,
    TO_CHAR(date_key, 'Month') AS month_name,
    CASE EXTRACT(QUARTER FROM date_key)
        WHEN 1 THEN 'Q1'
        WHEN 2 THEN 'Q2'
        WHEN 3 THEN 'Q3'
        WHEN 4 THEN 'Q4'
    END AS quarter_name,
    CASE EXTRACT(DOW FROM date_key)
        WHEN 6 THEN TRUE
        WHEN 0 THEN TRUE
        ELSE FALSE
    END AS is_weekend
FROM date_range;

-- Calculate the week of the month for each date
WITH week_dates AS (
    SELECT
        date_key,
        EXTRACT(MONTH FROM date_key) AS month,
        EXTRACT(WEEK FROM date_key) AS week,
        EXTRACT(YEAR FROM date_key) AS year,
        EXTRACT(DAY FROM date_key) AS day,
        EXTRACT(DOW FROM date_key) AS day_of_week
    FROM dim_date
),
weeks_in_month AS (
    SELECT
        date_key,
        month,
        week,
        year,
        day,
        day_of_week,
        CASE
            WHEN day <= 7 THEN 'Week 1'
            WHEN day <= 14 THEN 'Week 2'
            WHEN day <= 21 THEN 'Week 3'
            ELSE 'Week 4'
        END AS week_of_month
    FROM week_dates
)
UPDATE dim_date
SET week_of_month = weeks_in_month.week_of_month
FROM weeks_in_month
WHERE dim_date.date_key = weeks_in_month.date_key;

-- Add a function to calculate U.S. holidays dynamically
CREATE OR REPLACE FUNCTION is_us_holiday(date_key DATE) RETURNS BOOLEAN AS $$
DECLARE
    year INT := EXTRACT(YEAR FROM date_key);
    holidays DATE[];
BEGIN
    holidays := ARRAY[
        -- New Year's Day (January 1)
        MAKE_DATE(year, 1, 1),
        -- Martin Luther King Jr. Day (3rd Monday in January)
        MAKE_DATE(year, 1, 1) + ((21 - EXTRACT(DOW FROM MAKE_DATE(year, 1, 1) + INTERVAL '14 day')) % 7) * INTERVAL '1 day',
        -- Presidents' Day (3rd Monday in February)
        MAKE_DATE(year, 2, 1) + ((21 - EXTRACT(DOW FROM MAKE_DATE(year, 2, 1) + INTERVAL '14 day')) % 7) * INTERVAL '1 day',
        -- Memorial Day (last Monday in May)
        MAKE_DATE(year, 5, 31) - EXTRACT(DOW FROM MAKE_DATE(year, 5, 31)) * INTERVAL '1 day',
        -- Independence Day (July 4)
        MAKE_DATE(year, 7, 4),
        -- Labor Day (1st Monday in September)
        MAKE_DATE(year, 9, 1) + ((7 - EXTRACT(DOW FROM MAKE_DATE(year, 9, 1))) % 7) * INTERVAL '1 day',
        -- Columbus Day (2nd Monday of October)
        MAKE_DATE(year, 10, 1) + ((14 - EXTRACT(DOW FROM MAKE_DATE(year, 10, 1))) % 7) * INTERVAL '1 day',
        -- Veterans Day (November 11)
        MAKE_DATE(year, 11, 11),
        -- Thanksgiving Day (4th Thursday of November)
        MAKE_DATE(year, 11, 1) + ((28 - EXTRACT(DOW FROM MAKE_DATE(year, 11, 1))) % 7) * INTERVAL '1 day',
        -- Christmas Day (December 25)
        MAKE_DATE(year, 12, 25)
    ];

    -- Return true if the date_key is a holiday, false otherwise
    RETURN date_key = ANY(holidays);
END;
$$ LANGUAGE plpgsql;

-- Update the dim_date table to set the is_holiday column based on U.S. holidays
UPDATE dim_date
SET is_holiday = is_us_holiday(date_key);