CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	username TEXT UNIQUE,
	password TEXT,
	is_admin BOOLEAN
);

CREATE TABLE topics (
	id SERIAL PRIMARY KEY,
	name TEXT UNIQUE,
	is_visible BOOLEAN,
	is_hidden BOOLEAN
);

CREATE TABLE topic_access (
	id SERIAL PRIMARY KEY,
	topic_id INTEGER REFERENCES topics,
	user_id INTEGER REFERENCES users
);