import io
from django.http import FileResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from ..models import Order


# ==================================================
# ORDERS
# ==================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return Response(
        [
            {
                "id": o.id,
                "total": o.total,
                "created_at": o.created_at,
                "stripe_session_id": o.stripe_session_id,
            }
            for o in orders
        ]
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return Response(
        {
            "id": order.id,
            "total": order.total,
            "items": order.items,
            "created_at": order.created_at,
            "stripe_session_id": order.stripe_session_id,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_invoice(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        if order.user != request.user:
            return Response({"error": "Unauthorized"}, status=403)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    pdf.drawString(50, 800, "RRR Shopkart - Invoice")
    pdf.drawString(50, 770, f"Order ID: {order.id}")
    pdf.drawString(50, 750, f"Customer: {order.user.username}")
    pdf.drawString(50, 730, f"Email: {order.user.email}")
    pdf.drawString(50, 710, f"Total Paid: ₹{order.total}")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f"invoice_{order.id}.pdf"
    )
