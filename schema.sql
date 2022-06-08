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
	is_hidden BOOLEAN,
	count_threads INTEGER,
	count_messages INTEGER,
	latest_message TIMESTAMP
);

CREATE INDEX idx_topic_name ON topics (name);

CREATE TABLE threads (
	id SERIAL PRIMARY KEY,
	subject TEXT,
	topic_id INTEGER REFERENCES topics,
	creator_id INTEGER REFERENCES users,
	is_visible BOOLEAN,
	count_messages INTEGER,
	latest_message TIMESTAMP
);

CREATE TABLE topic_access (
	id SERIAL PRIMARY KEY,
	topic_id INTEGER REFERENCES topics,
	user_id INTEGER REFERENCES users,
	UNIQUE(topic_id, user_id)
);

CREATE INDEX idx_topic_access_topics ON topic_access (topic_id);

CREATE TABLE messages (
	id SERIAL PRIMARY KEY,
	content TEXT,
	thread_id INTEGER REFERENCES threads,
	creator_id INTEGER REFERENCES users,
	is_visible BOOLEAN,
	sent_at TIMESTAMP
);