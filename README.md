# PurBeurre

## Intent of the project

This program manipulates a database of foods scored by their nutritive quality. 
Its aim is to find healthier alternatives to the alimentation of the user.

It is a school project for a course with OpenClassrooms.  
It is made to practice how to use an API and a database in web development.  

## How to use the program

In order to use this program, you need first to create an empty database, 
that will be filled at the start of the program.

Before starting the program, those elements have to be set by the user:
  - the name of the database must be : 
    - DB_NAME = 'purbeurre'
  - the credentials for the database must be stored in environment variables with specific keys:
    - DB_HOST, 
    - DB_USER, 
    - DB_PASSWORD

## Components of the program

Those are the main elements developed for the program:
  - api caller: get the data from the website OpenFoodFacts
  - api parser: organize properly the JSON object containing the data, and modify its format to make it usable for the database
  - db builder: create the database and the tables
  - db manager: fill the tables with the data fetched from the website
  - entity manager: pilot the interactions of the program with the database (creates sql queries and return result asobjects)
  - view manager: run the visuals for the user interface (as a command line interface)
  - controller: orchestrate the interactions between the user interface and the part of the program manipulating the data
