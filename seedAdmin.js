import db from './config/db.js';
import bcrypt from 'bcrypt';

const seedAdmin = async () => {
  const hash = await bcrypt.hash('mala@1234', 10);
  db.run(
    `INSERT INTO users (first_name, last_name, tr_number, its_number, class, hizb, role, password_hash)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
    ['Aliasger', 'Mala', 26365, 30477380, 7, 'Firozaj', 'admin', hash],
    (err) => {
      if (err) console.error('Error seeding admin:', err);
      else console.log('Admin user created');
    }
  );
};

seedAdmin();
