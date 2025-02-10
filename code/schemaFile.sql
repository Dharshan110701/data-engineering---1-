-- Create Database if it doesn't exist
CREATE DATABASE IF NOT EXISTS dataengg;

-- Use the created database
USE dataengg;

-- Disable foreign key checks
SET FOREIGN_KEY_CHECKS = 0;

-- Drop Tables if they exist
DROP TABLE IF EXISTS Sports;
DROP TABLE IF EXISTS Olympiad;
DROP TABLE IF EXISTS CountryMedals;
DROP TABLE IF EXISTS ContinentalMedals;
DROP TABLE IF EXISTS AthletesMedals;

-- Enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Create Tables
CREATE TABLE Sports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Abbreviation VARCHAR(5),
    Discipline VARCHAR(255),
    Sport VARCHAR(255),
    Season VARCHAR(255)
);

CREATE TABLE Olympiad (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Years INT UNIQUE,  -- Make the Years column unique
    Host_City VARCHAR(255),
    Nations INT,
    Athletes INT
);

CREATE TABLE CountryMedals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Team VARCHAR(255),
    Gold INT,
    Silver INT,
    Bronze INT,
    Total INT,
    Years INT,
    Flag_URL VARCHAR(255),
    FOREIGN KEY (Years) REFERENCES Olympiad(Years)
);

CREATE TABLE ContinentalMedals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Years INT,
    Position VARCHAR(10),
    Continent VARCHAR(255),
    Gold INT,
    Silver INT,
    Bronze INT,
    Total INT,
    FOREIGN KEY (Years) REFERENCES Olympiad(Years)
);

CREATE TABLE AthletesMedals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Athlete_Name VARCHAR(255),
    Gold INT,
    Silver INT,
    Bronze INT,
    Total INT,
    Years INT,
    FOREIGN KEY (Years) REFERENCES Olympiad(Years)
);
