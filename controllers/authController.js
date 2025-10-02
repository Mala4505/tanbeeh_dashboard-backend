import db from '../config/db.js';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';
dotenv.config();

export const login = (req, res) => {
  const { trNumber, password } = req.body;
  const trNumberInt = Number(trNumber);

  db.get('SELECT * FROM users WHERE tr_number = ?', [trNumberInt], async (err, user) => {
    if (err || !user) return res.status(401).json({ error: 'Invalid TR Number' });

    try {
      const match = await bcrypt.compare(password, user.password_hash);
      if (!match) return res.status(401).json({ error: 'Invalid password' });

      const payload = { id: user.id, role: user.role };
      const token = jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '1d' });

      console.log('User logged in:', user.tr_number);
      res.json({ token });
    } catch (error) {
      console.error('Login error:', error);
      res.status(500).json({ error: 'Server error during login' });
    }
  });
};

export const getProfile = (req, res) => {
  db.get(
    'SELECT first_name, last_name, tr_number, its_number, class, hizb, role FROM users WHERE id = ?',
    [req.user.id],
    (err, user) => {
      if (err || !user) return res.status(404).json({ error: 'User not found' });
      res.json(user);
    }
  );
};
