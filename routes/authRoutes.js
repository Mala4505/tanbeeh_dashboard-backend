import express from 'express';
import { login, getProfile } from '../controllers/authController.js';
import { verifyToken } from '../middleware/authMiddleware.js';

const router = express.Router();

router.post('/login', login);
router.get('/me', verifyToken, getProfile);

export default router;
