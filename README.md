# Web application structure

* static: gifs, etc.
* templates:
  * admin.html
  * base.html
  * courselist.html
  * driverlist.html
  * index.html
  * overall.html
  * runlist.html
  * top5graph.html
* app.py
  1. `/` Route:
     - Function: Redirects to the `overall` route.
  2. `/listdrivers` Route:
     - Function: Retrieves the list of drivers from the database and displays them.
     - Template: `driverlist.html`
  3. `/listcourses` Route:
     - Function: Retrieves the list of drivers and courses from the database and displays them.
     - Template: `courselist.html`
  4. `/graph` Route:
     - Function: Gathers data to display a chart for the top 5 drivers.
     - Template: `top5graph.html`
  5. `/run_list/<int:driver_id>` Route:
     - Parameter: `driver_id` - Driver's ID.
     - Function: Retrieves the run list and other relevant information for the specified driver and displays them.
     - Template: `runlist.html`
  6. `/overall` Route:
     - Function: Retrieves overall information for all drivers, including rankings and total scores, and displays them.
     - Template: `overall.html`
  7. `/admin` Route:
     - Function: Gathers various data related to the admin page, including driver lists, search functionality, editing run data, and adding drivers.
     - Template: `admin_backup2.html`
  8. `/edit_run` Route:
     - Method: POST
     - Function: Accepts run data edit requests submitted via a form and updates run data in the database.
     - Redirects to the `/admin` route.
  9. `/add_driver` Route:
     - Method: POST
     - Function: Accepts new driver data submitted via a form and inserts it into the database.
     - Redirects to the `/admin` route.

# Assumptions and design decisions
## assumptions
* All user inputs are follow proper formats and data types
* Users will not forge requests to launch attacks on the website
## design decisions
### Module division
I divide the website into 5 main parts:
* Main Page
* Driver List
* Course List
* Driver Run List
* Admin Dashboard

Detailed data is displayed in the Main page, because these data contain detailed information about the competition, this is what the participants and viewers of the competition are most concerned about.

The other data is displayed in the other 3 user pages.

The admin functions are concentrated on one page because the content that needs to be managed is relatively simple.

### Request Methods

Operations involving insert and update use the post method, and other operations use get.

## Function Extraction

"get_overall" and """get_overall_all" are 2 The two most important extracted functions, they implement a large amount of and repetitive logic.

## Database questions

###### What SQL statement creates the car table and defines its three fields/columns? (Copy and
paste the relevant lines of SQL.)

```sql
CREATE TABLE IF NOT EXISTS car
(
car_num INT PRIMARY KEY NOT NULL,
model VARCHAR(20) NOT NULL,
drive_class VARCHAR(3) NOT NULL
);
```

###### Which line of SQL code sets up the relationship between the car and driver tables?
``FOREIGN KEY (caregiver) REFERENCES driver(driver_id)`` in
```sql
CREATE TABLE IF NOT EXISTS driver
(
driver_id INT auto_increment PRIMARY KEY NOT NULL,
first_name VARCHAR(25) NOT NULL,
surname VARCHAR(25) NOT NULL,
date_of_birth DATE,
age INT,
caregiver INT,
car INT NOT NULL,
FOREIGN KEY (caregiver) REFERENCES driver(driver_id)
ON UPDATE CASCADE,
FOREIGN KEY (car) REFERENCES car(car_num)
ON UPDATE CASCADE
ON DELETE CASCADE
);
```
###### Which 3 lines of SQL code insert the Mini and GR Yaris details into the car table?
```sql
INSERT INTO car VALUES
(11,'Mini','FWD'),
(17,'GR Yaris','4WD');
```
in
```sql
INSERT INTO car VALUES
(11,'Mini','FWD'),
(17,'GR Yaris','4WD'),
(18,'MX-5','RWD'),
(20,'Camaro','RWD'),
(22,'MX-5','RWD'),
(31,'Charade','FWD'),
(36,'Swift','FWD'),
(44,'BRZ','RWD')
;
```
###### Suppose the club wanted to set a default value of ‘RWD’ for the driver_class field. What specific change would you need to make to the SQL to do this? (Do not implement this change in your app.)
```sql
ALTER TABLE car
MODIFY drive_class VARCHAR(3) DEFAULT 'RWD' NOT NULL;
```
###### Suppose logins were implemented. Why is it important for drivers and the club admin to access different routes? As part of your answer, give two specific examples of problems that could occur if all of the web app facilities were available to everyone.
Because they have different permissions to access the database.
1. Privacy: If all features are available to everyone, there may be privacy and security issues. For example, a driver should not modify the result of any driver.
2. Data consistency: If all users can edit the result, the data in the database may meet data consistency problem.
### Image sources
No extra images are used.
