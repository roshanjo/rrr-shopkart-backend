const mongoose = require("mongoose");

const addressSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "User",
    required: true
  },
  fullName: String,
  phone: String,
  street: String,
  city: String,
  state: String,
  pincode: String,
  country: String
}, { timestamps: true });

module.exports = mongoose.model("Address", addressSchema);
