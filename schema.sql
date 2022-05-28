CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	username TEXT UNIQUE,
	password TEXT,
	is_admin BOOLEAN
);

CREATE TABLE topics (
	id SERIAL PRIMARY KEY,
	name TEXT UNIQUE,
	is_hidden BOOLEAN
);