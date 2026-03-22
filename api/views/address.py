from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Address


# ==================================================
# ADDRESS
# ==================================================

@csrf_exempt
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def address_view(request):

    if request.method == "GET":
        try:
            address = Address.objects.get(user=request.user)
            return Response(
                {
                    "id": address.id,
                    "full_name": address.full_name,
                    "phone": address.phone,
                    "street": address.street,
                    "city": address.city,
                    "state": address.state,
                    "pincode": address.pincode,
                }
            )
        except Address.DoesNotExist:
            return Response({}, status=200)

    # POST
    data = request.data
    required_fields = ["full_name", "phone", "street", "city", "state", "pincode"]

    if not all(data.get(field) for field in required_fields):
        return Response({"error": "All address fields are required"}, status=400)

    address, created = Address.objects.update_or_create(
        user=request.user,
        defaults={
            "full_name": data["full_name"],
            "phone": data["phone"],
            "street": data["street"],
            "city": data["city"],
            "state": data["state"],
            "pincode": data["pincode"],
        }
    )

    return Response({"id": address.id, "created": created}, status=201)
