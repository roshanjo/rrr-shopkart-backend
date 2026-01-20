const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);

router.post("/checkout", async (req, res) => {
  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ["card"],
      line_items: req.body.products,
      mode: "payment",
      success_url: `${process.env.CLIENT_URL}/order-success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.CLIENT_URL}/cart`,
      metadata: {
        userId: req.body.userId,
        addressId: req.body.addressId
      }
    });

    res.json({ url: session.url });
  } catch (err) {
    res.status(500).json(err);
  }
});
