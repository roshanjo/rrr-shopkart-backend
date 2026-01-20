const router = require("express").Router();
const Address = require("../models/Address");

// Save address
router.post("/", async (req, res) => {
  try {
    const address = new Address(req.body);
    await address.save();
    res.status(201).json(address);
  } catch (err) {
    res.status(500).json(err);
  }
});

// Get user address
router.get("/:userId", async (req, res) => {
  try {
    const address = await Address.findOne({ userId: req.params.userId });
    res.status(200).json(address);
  } catch (err) {
    res.status(500).json(err);
  }
});

module.exports = router;
