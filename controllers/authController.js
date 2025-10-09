// import db from '../config/db.js';
// import bcrypt from 'bcrypt';
// import jwt from 'jsonwebtoken';
// import dotenv from 'dotenv';
// dotenv.config();

// export const login = (req, res) => {
//   const { trNumber, password } = req.body;
//   const trNumberInt = Number(trNumber);

//   db.get('SELECT * FROM users WHERE tr_number = ?', [trNumberInt], async (err, user) => {
//     if (err || !user) return res.status(401).json({ error: 'Invalid TR Number' });

//     try {
//       const match = await bcrypt.compare(password, user.password_hash);
//       if (!match) return res.status(401).json({ error: 'Invalid password' });

//       const payload = { id: user.id, role: user.role };
//       const token = jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '1d' });

//       console.log('User logged in:', user.tr_number);
//       res.json({ token });
//     } catch (error) {
//       console.error('Login error:', error);
//       res.status(500).json({ error: 'Server error during login' });
//     }
//   });
// };

// export const getProfile = (req, res) => {
//   db.get(
//     'SELECT first_name, last_name, tr_number, its_number, class, hizb, role FROM users WHERE id = ?',
//     [req.user.id],
//     (err, user) => {
//       if (err || !user) return res.status(404).json({ error: 'User not found' });
//       res.json(user);
//     }
//   );
// };



import db from '../config/db.js';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';
dotenv.config();

// 🔐 POST /api/login
export const login = (req, res) => {
  const { trNumber, password } = req.body;
  console.log('Incoming login request:', req.body);


  // Validate input
  if (!trNumber || !password) {
    return res.status(400).json({ error: 'TR number and password are required' });
  }
  
  const trNumberInt = Number(trNumber);
  console.log('Login attempt with TR:', trNumberInt);
  if (isNaN(trNumberInt)) {
    return res.status(400).json({ error: 'Invalid TR number format' });
  }

  // Query user from DB
  db.get('SELECT * FROM users WHERE tr_number = ?', [trNumberInt], async (err, user) => {
    if (err) {
      console.error('DB error:', err.message);
      return res.status(500).json({ error: 'Database error' });
    }

    if (!user) {
      return res.status(401).json({ error: 'Invalid TR number' });
    }

    try {

      const match = await bcrypt.compare(password, user.password_hash);
      if (!match) {
        return res.status(401).json({ error: 'Invalid password' });
      }

      const payload = { id: user.id, role: user.role };
      const token = jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '1d' });

      console.log(`✅ User logged in: TR ${user.tr_number}`);
      res.json({ token });
    } catch (error) {
      console.error('Login error:', error.message);
      res.status(500).json({ error: 'Server error during login' });
    }
  });
};

// 👤 GET /api/me
export const getProfile = (req, res) => {
  const userId = req.user?.id;

  if (!userId) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  db.get(
    'SELECT first_name, last_name, tr_number, its_number, class, hizb, role FROM users WHERE id = ?',
    [userId],
    (err, user) => {
      if (err) {
        console.error('DB error:', err.message);
        return res.status(500).json({ error: 'Database error' });
      }

      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      res.json(user);
    }
  );
};
