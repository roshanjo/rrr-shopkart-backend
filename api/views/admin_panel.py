from django.contrib.auth import get_user_model
User = get_user_model()
from django.db.models import Sum
from django.utils import timezone
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import HttpResponse

from ..models import Order, Profile, ActivityLog, Product


from ..permissions import IsCustomAdmin

import datetime


# ==================================================
# ADMIN - ANALYTICS
# ==================================================

@api_view(["GET"])
@permission_classes([IsCustomAdmin])
def analytics(request):
    total_users = User.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(Sum("total"))["total__sum"] or 0

    # Daily Sales (Last 7 Days)
    today = timezone.now().date()
    sales_data = []
    for i in range(6, -1, -1):
        date = today - datetime.timedelta(days=i)
        # Handle date lookup safely depending on DB
        # MySQL/Postgres support __date, SQLite might need range
        start_time = timezone.make_aware(datetime.datetime.combine(date, datetime.time.min))
        end_time = timezone.make_aware(datetime.datetime.combine(date, datetime.time.max))
        
        day_sales = Order.objects.filter(
            created_at__range=(start_time, end_time)
        ).aggregate(Sum("total"))["total__sum"] or 0
        
        sales_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "revenue": day_sales
        })

    return Response({
        "total_users": total_users,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "daily_sales": sales_data
    })


# ==================================================
# ADMIN - USERS LIST
# ==================================================

@api_view(["GET"])
@permission_classes([IsCustomAdmin])
def list_users(request):
    # Get all users (sorted by ID)
    users = User.objects.all().order_by("-id")
    data = []
    for u in users:
        profile, _ = Profile.objects.get_or_create(user=u)
        data.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "date_joined": u.date_joined,
            "status": profile.status,
            "is_active": u.is_active,
        })
    return Response(data)


# ==================================================
# ADMIN - USER ACTIONS
# ==================================================

@api_view(["POST"])
@permission_classes([IsCustomAdmin])
def user_action(request, user_id):
    action = request.data.get("action") # block, suspend, ban, unblock
    
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if user.email == "admin@aikart.com":
        return Response({"error": "Cannot modify Admin user"}, status=400)

    if action == "block":
        profile.status = "blocked"
        user.is_active = False # Sync with Django auth
    elif action == "suspend":
        profile.status = "suspended"
        user.is_active = False
    elif action == "ban":
        profile.status = "banned"
        user.is_active = False
    elif action == "unblock" or action == "activate":
        profile.status = "active"
        user.is_active = True
    elif action == "delete" or action == "hard_delete":
        # PROTECT ADMIN + SUPERUSER
        PROTECTED_ADMIN_EMAIL = "admin@aikart.com"
        if user.email == PROTECTED_ADMIN_EMAIL or user.is_superuser:
            return Response({
                "error": "This account cannot be deleted"
            }, status=403)

        # PERMANENT HARD DELETE
        username = user.username
        with transaction.atomic():
            user.delete()
            ActivityLog.objects.create(user=request.user, action=f"Hard-deleted user {username} (ID: {user_id})")
        
        return Response({"message": f"User {username} permanently deleted", "status": "deleted"})
    else:
        return Response({"error": "Invalid action"}, status=400)

    profile.save()
    user.save()
    
    ActivityLog.objects.create(
        user=request.user, 
        action=f"{action.capitalize()}ed user {user.username}"
    )

    return Response({"message": f"User {action}ed successfully", "status": profile.status})


# ==================================================
# ADMIN - ACTIVITY LOGS
# ==================================================

@api_view(["GET"])
@permission_classes([IsCustomAdmin])
def list_logs(request):
    logs = ActivityLog.objects.select_related("user").all().order_by("-timestamp")[:100]
    data = [
        {
            "id": l.id,
            "username": l.user.username if l.user else "Anonymous",
            "action": l.action,
            "timestamp": l.timestamp
        }
        for l in logs
    ]
    return Response(data)

# ==================================================
# ADMIN - PAYMENTS
# ==================================================

@api_view(["GET"])
@permission_classes([IsCustomAdmin])
def list_payments(request):
    payments = Order.objects.select_related("user").all().order_by("-created_at")
    data = [
        {
            "id": p.id,
            "user": p.user.username,
            "amount": p.total,
            "status": p.payment_status,
            "payment_method": p.payment_method,
            "paid_at": p.paid_at,
            "created_at": p.created_at
        }
        for p in payments
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([IsCustomAdmin])
def admin_products(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponse(status=403)
    products = Product.objects.all().order_by("id")
    data = [
        {
            "id": p.id,
            "title": p.title,
            "price_inr": p.price_inr,
            "stock": p.stock,
            "category": p.category
        }
        for p in products
    ]
    return Response(data)

@api_view(["PATCH"])
@permission_classes([IsCustomAdmin])
def admin_product_detail(request, product_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponse(status=403)
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    stock = request.data.get("stock")
    if stock is not None:
        try:
            stock = int(stock)
            if stock < 0:
                return Response({"error": "Stock cannot be negative"}, status=400)
            product.stock = stock
        except ValueError:
            return Response({"error": "Invalid stock value"}, status=400)

    product.save()
    
    from django.core.cache import cache
    cache.delete(f"product_{product_id}")

    ActivityLog.objects.create(
        user=request.user, 
        action=f"Updated stock for Product #{product_id} to {product.stock}"
    )

    return Response({
        "message": "Product stock updated successfully",
        "id": product.id,
        "stock": product.stock
    })

