const mongoose = require("mongoose");

const orderSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "User",
    required: true
  },
  products: Array,
  address: Object,
  amount: Number,
  paymentStatus: String,
  stripeSessionId: String
}, { timestamps: true });

module.exports = mongoose.model("Order", orderSchema);
