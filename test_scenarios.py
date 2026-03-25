import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from api.models import Product

def setup_scenario_1():
    # Scenario 1: Delete product 1, Deactivate product 10
    print("Setting up Scenario 1: Delete ID 1, Deactivate ID 10")
    Product.objects.filter(id=1).delete()
    Product.objects.filter(id=10).update(is_active=False)

def setup_scenario_2():
    # Scenario 2: Set lower stock for product 11
    print("Setting up Scenario 2: Set stock=2 for ID 11")
    Product.objects.filter(id=11).update(stock=2)

def reset_products():
    # I'll just run sync again to reset
    import subprocess
    subprocess.run([".\\.venv\\Scripts\\python", "run_sync.py"])

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "1":
            setup_scenario_1()
        elif sys.argv[1] == "2":
            setup_scenario_2()
        elif sys.argv[1] == "reset":
            reset_products()
