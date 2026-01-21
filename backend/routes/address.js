const router = require("express").Router();
const Address = require("../models/Address");

// Save address
router.post("/", async (req, res) => {
  try {
    // 🔍 DEBUG (you can remove later)
    console.log("ADDRESS BODY:", req.body);

    if (!req.body.userId) {
      return res.status(400).json({ message: "UserId is required" });
    }

    const address = new Address({
      userId: req.body.userId,
      fullName: req.body.fullName,
      phone: req.body.phone,
      street: req.body.street,
      city: req.body.city,
      state: req.body.state,
      pincode: req.body.pincode,
    });

    const savedAddress = await address.save();
    res.status(201).json(savedAddress);
  } catch (err) {
    console.error("ADDRESS SAVE ERROR:", err);
    res.status(500).json(err);
  }
});

// Get user address
router.get("/:userId", async (req, res) => {
  try {
    const address = await Address.findOne({ userId: req.params.userId });
    res.status(200).json(address);
  } catch (err) {
    console.error("ADDRESS FETCH ERROR:", err);
    res.status(500).json(err);
  }
});

module.exports = router;
