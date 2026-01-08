import os
import stripe
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

@csrf_exempt
def create_checkout_session(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        total = int(data.get("total", 0))

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "inr",
                            "product_data": {
                                "name": "Ai-Kart Purchase",
                            },
                            "unit_amount": total * 100,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url="https://rrr-shopkart-frontend.onrender.com/success",
                cancel_url="https://rrr-shopkart-frontend.onrender.com/cancel",
            )

            return JsonResponse({"url": session.url})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


def home(request):
    return HttpResponse("Ai-Kart Backend Running 🚀")
