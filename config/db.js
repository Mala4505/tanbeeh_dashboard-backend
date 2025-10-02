import sqlite3 from 'sqlite3';

const db = new sqlite3.Database('./Tanbeeh.db', (err) => {
  if (err) {
    console.error('Failed to connect to database:', err.message);
  } else {
    console.log('Connected to Tanbeeh.db');
  }
});

// Optional: create users table if it doesn't exist
db.run(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    tr_number INTEGER UNIQUE,
    its_number INTEGER,
    class INTEGER,
    hizb TEXT,
    role TEXT,
    password_hash TEXT
  )
`);

export default db;
