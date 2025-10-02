// import db from "../config/db.js";
// import bcrypt from "bcrypt";

// // ✅ Create User
// export const createUser = async (req, res) => {
//   const {
//     first_name,
//     last_name,
//     tr_number,
//     its_number,
//     class: class_name,
//     hizb,
//     role,
//     password,
//   } = req.body;

//   try {
//     const hashedPassword = await bcrypt.hash(password, 10);

//     db.run(
//       `INSERT INTO users (first_name, last_name, tr_number, its_number, class, hizb, role, password_hash)
//        VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
//       [
//         first_name,
//         last_name,
//         parseInt(tr_number),
//         parseInt(its_number),
//         parseInt(class_name),
//         hizb,
//         role,
//         hashedPassword,
//       ],
//       (err) => {
//         if (err) {
//           console.error("DB insert error:", err.message);
//           return res.status(500).json({ error: "Failed to create user" });
//         }
//         res.status(201).json({ message: "User created successfully" });
//       }
//     );
//   } catch (err) {
//     console.error("Server error:", err.message);
//     res.status(500).json({ error: "Server error" });
//   }
// };

// // ✅ Update User
// export const updateUser = (req, res) => {
//   if (req.user.role !== "admin") {
//     return res.status(403).json({ error: "Access denied" });
//   }

//   const { id } = req.params;
//   const { first_name, last_name, tr_number, its_number, role } = req.body;

//   db.run(
//     `UPDATE users SET first_name = ?, last_name = ?, tr_number = ?, its_number = ?, role = ? WHERE id = ?`,
//     [first_name, last_name, tr_number, its_number, role, id],
//     function (err) {
//       if (err) {
//         console.error("DB update error:", err.message);
//         return res.status(500).json({ error: "Failed to update user" });
//       }
//       if (this.changes === 0) {
//         return res.status(404).json({ error: "User not found" });
//       }
//       res.json({ success: true });
//     }
//   );
// };

// // ✅ Delete User
// export const deleteUser = (req, res) => {
//   if (req.user.role !== "admin") {
//     return res.status(403).json({ error: "Access denied" });
//   }

//   const { id } = req.params;

//   db.run("DELETE FROM users WHERE id = ?", [id], function (err) {
//     if (err) {
//       console.error("DB delete error:", err.message);
//       return res.status(500).json({ error: "Failed to delete user" });
//     }
//     if (this.changes === 0) {
//       return res.status(404).json({ error: "User not found" });
//     }
//     res.json({ success: true });
//   });
// };
import db from "../config/db.js";
import bcrypt from "bcrypt";

// Create User
export const createUser = async (req, res) => {
  const {
    first_name,
    last_name,
    tr_number,
    its_number,
    class: class_name,
    hizb,
    role,
    password,
  } = req.body;
  
  console.log("Received body:", req.body);
  
  try {
    const hashedPassword = await bcrypt.hash(password, 10);

    db.run(
      `INSERT INTO users (first_name, last_name, tr_number, its_number, class, hizb, role, password_hash)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        first_name,
        last_name,
        parseInt(tr_number),
        parseInt(its_number),
        parseInt(class_name),
        hizb,
        role,
        hashedPassword,
      ],
      (err) => {
        if (err) {
          console.error("DB insert error:", err.message);
          return res.status(500).json({ error: "Failed to create user" });
        }
        res.status(201).json({ message: "User created successfully" });
      }
    );
  } catch (err) {
    console.error("Server error:", err.message);
    res.status(500).json({ error: "Server error" });
  }
};

// Get All Users
export const getAllUsers = (req, res) => {
  if (req.user.role !== "admin") {
    return res.status(403).json({ error: "Access denied" });
  }

  db.all("SELECT * FROM users", [], (err, rows) => {
    if (err) {
      console.error("DB fetch error:", err.message);
      return res.status(500).json({ error: "Failed to fetch users" });
    }
    res.json(rows);
  });
};

// Update User
export const updateUser = (req, res) => {
  if (req.user.role !== "admin") {
    return res.status(403).json({ error: "Access denied" });
  }

  const { id } = req.params;
  const { first_name, last_name, tr_number, its_number, role } = req.body;

  db.run(
    `UPDATE users SET first_name = ?, last_name = ?, tr_number = ?, its_number = ?, role = ? WHERE id = ?`,
    [first_name, last_name, tr_number, its_number, role, id],
    function (err) {
      if (err) {
        console.error("DB update error:", err.message);
        return res.status(500).json({ error: "Failed to update user" });
      }
      if (this.changes === 0) {
        return res.status(404).json({ error: "User not found" });
      }
      res.json({ success: true });
    }
  );
};

// Delete User
export const deleteUser = (req, res) => {
  const id = parseInt(req.params.id);
  console.log("Attempting to delete user with ID:", id);

  if (req.user.role !== "admin") {
    console.log("Access denied: not admin");
    return res.status(403).json({ error: "Access denied" });
  }

  db.run("DELETE FROM users WHERE id = ?", [id], function (err) {
    if (err) {
      console.error("DB delete error:", err.message);
      return res.status(500).json({ error: "Failed to delete user" });
    }

    console.log("Rows affected:", this.changes);
    if (this.changes === 0) {
      return res.status(404).json({ error: "User not found" });
    }

    res.json({ success: true });
  });
};