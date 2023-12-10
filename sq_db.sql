CREATE TABLE IF NOT EXISTS users (
id integer PRIMARY KEY AUTOINCREMENT,
uname text NOT NULL,
surname text NOT NULL,
username text NOT NULL,
passwd text NOT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
id integer PRIMARY KEY AUTOINCREMENT,
product text NOT NULL,
category text NOT NULL,
buydate date NOT NULL,
cost integer NOT NULL,
username text NOT NULL
);