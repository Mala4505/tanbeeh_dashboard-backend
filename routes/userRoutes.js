// import express from 'express';
// import { createUser } from '../controllers/userController.js';
// import { verifyToken } from '../middleware/authMiddleware.js';
// import db from '../config/db.js';

// import { deleteUser, updateUser } from "../controllers/userController.js";

// const router = express.Router();

// router.get('/all', verifyToken, (req, res) => {
//   if (req.user.role !== 'admin') {
//     console.log('Access denied: not admin');
//     return res.status(403).json({ error: 'Access denied' });
//   }

//   db.all('SELECT * FROM users', [], (err, rows) => {
//     if (err) {
//       console.error('DB error:', err);
//       return res.status(500).json({ error: 'Failed to fetch users' });
//     }
//     console.log(`Returned ${rows.length} users`);
//     res.json(rows);
//   });
// });

// router.post('/', verifyToken, (req, res) => {
//   if (req.user.role !== 'admin') {
//     return res.status(403).json({ error: 'Access denied' });
//   }

//   createUser(req, res);
// });

// router.delete("/users/:id", verifyToken, deleteUser);
// router.put("/users/:id", verifyToken, updateUser);

// export default router;
import express from "express";
import {
  createUser,
  deleteUser,
  updateUser,
  getAllUsers,
} from "../controllers/userController.js";
import { verifyToken } from "../middleware/authMiddleware.js";

const router = express.Router();

router.get("/all", verifyToken, getAllUsers);
router.post("/", verifyToken, createUser);
router.put("/:id", verifyToken, updateUser);
router.delete("/:id", verifyToken, deleteUser);

export default router;
