import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import authRoutes from './routes/authRoutes.js';
import userRoutes from './routes/userRoutes.js';

dotenv.config();
const app = express();

// ✅ Parse JSON before routes
app.use(express.json());

// ✅ CORS must come before routes
app.use(cors({
  origin: 'https://tanbeeh-dashboard-frontend.vercel.app',
  credentials: true,
}));

// ✅ Global request logger (optional)
app.use((req, res, next) => {
  console.log(`[${req.method}] ${req.originalUrl}`);
  next();
});

// ✅ Mount routes
app.use('/api', authRoutes);
app.use('/api/users', userRoutes);

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

// import express from 'express';
// import cors from 'cors';
// import dotenv from 'dotenv';
// import authRoutes from './routes/authRoutes.js';
// import userRoutes from './routes/userRoutes.js';

// dotenv.config();
// const app = express();

// // ✅ CORS must come BEFORE routes
// // app.use(cors({
// //   origin: 'https://tanbeeh-dashboard-frontend.vercel.app',
// //   credentials: true,
// // }));

// app.use(cors({
//   origin: 'https://tanbeeh-dashboard-frontend.vercel.app', // ✅ no trailing slash
//   methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
//   allowedHeaders: ['Content-Type', 'Authorization'],
//   credentials: true,
// }));

// app.use(express.json());
// // ✅ Mount routes
// app.use('/api', authRoutes);
// app.use('/api/users', userRoutes);


// // ✅ Global request logger
// app.use((req, res, next) => {
//   console.log(`[${req.method}] ${req.originalUrl}`);
//   next();
// });


// const PORT = process.env.PORT || 8000;
// app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
