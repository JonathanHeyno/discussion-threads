# Discussion Threads Application

An application for maintaining discussion threads on various topics

## Running the application
You can run the app in Heroku [https://discussion-threads.herokuapp.com/](https://discussion-threads.herokuapp.com/)

To run the app on your local computer, download the files and create an .env file with `DATABASE_URL` pointing to the database and `SECRET_KEY` for a generated key. Also create the database tables in the `schema.sql`file. The program can be ran with e.g. flask: `flask run`

## Functionality and use
The application has the following functionalities:
- Create an account (user or admin)
- Admins can add and remove topics
- Admins can create hidden topics visible only for selected users
- Users can create new threads under topics
- Users can post messages under threads
- Users can edit and remove threads and messages they created
- Users can search for topics, threads and messages containg a given string
- The application shows for each topic:
  - The number of threads in the topic
  - The total number of messages
  - Time of the latest message