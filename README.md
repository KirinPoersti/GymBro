# 🏋️‍♂️ Gym Bro

## Application Features

* Users can create an account and log in to the application.  
* Users can add, edit, and delete workout entries (e.g., exercises, routines, progress logs).  
* Users can view workout entries added to the app (both their own and those of other users).  
* Users can search for workout entries by keyword or other criteria.  
* The app includes user profile pages that display statistics and the entries created by that user.  
* Users can assign one or more classifications to each workout entry (e.g., strength, cardio, mobility).  
* Users can add secondary entries (e.g., notes, comments, or nutrition logs) that complement the main entries.  
* Users can set personal training goals and track their progress.  

## Installation

Install the `flask` library:

```
$ pip install flask
```

Create the database tables and add initial data:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

Run the application:

```
$ flask run
```

## 📌 Additional Information

* **Backend:** Python (Flask)  
* **Database:** SQLite for development (PostgreSQL/MySQL recommended for production)  
* **Interface:** Browser-based web app  
* **Future Extensions:** React frontend, JWT authentication, Docker deployment  

---

💪 *Gym Bro is your web-based training buddy — track workouts, set goals, and get inspired by the progress of others.*