import express from "express";
import cors from "cors";
import dotenv from "dotenv";

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());

// health check
app.get("/", (req, res) => {
  res.send("RRR Shopkart Backend is running 🚀");
});

// favicon fix
app.get("/favicon.ico", (req, res) => {
  res.status(204).end();
});

// test route
app.get("/api/test", (req, res) => {
  res.json({ message: "API working successfully" });
});

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
