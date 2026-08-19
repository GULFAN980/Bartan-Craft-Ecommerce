from django.core.management.base import BaseCommand
from store.models import Product


class Command(BaseCommand):

    help = "Add demo products to BartanCraft"

    def handle(self, *args, **kwargs):

        products = [

            {
                "name": "Premium Stainless Steel Cookware Set",
                "description": "Complete stainless steel cookware set for everyday cooking.",
                "price": 2499,
                "stock": 25,
                "image": "https://loremflickr.com/800/600/cookware?lock=1",
            },

            {
                "name": "Stainless Steel Pressure Cooker",
                "description": "Durable pressure cooker designed for fast and safe cooking.",
                "price": 1299,
                "stock": 18,
                "image": "https://loremflickr.com/800/600/pressure,cooker?lock=2",
            },

            {
                "name": "Non Stick Frying Pan",
                "description": "Premium non-stick frying pan for easy everyday cooking.",
                "price": 699,
                "stock": 30,
                "image": "https://loremflickr.com/800/600/frying,pan?lock=3",
            },

            {
                "name": "Stainless Steel Kadhai",
                "description": "Heavy-duty stainless steel kadhai for Indian cooking.",
                "price": 899,
                "stock": 22,
                "image": "https://loremflickr.com/800/600/kadhai,pan?lock=4",
            },

            {
                "name": "Stainless Steel Saucepan",
                "description": "Compact saucepan perfect for tea, milk and sauces.",
                "price": 549,
                "stock": 35,
                "image": "https://loremflickr.com/800/600/saucepan?lock=5",
            },

            {
                "name": "Dinner Plate Set",
                "description": "Elegant stainless steel dinner plates for family meals.",
                "price": 799,
                "stock": 40,
                "image": "https://loremflickr.com/800/600/dinner,plates?lock=6",
            },

            {
                "name": "Stainless Steel Bowl Set",
                "description": "Multipurpose stainless steel bowls for kitchen use.",
                "price": 599,
                "stock": 45,
                "image": "https://loremflickr.com/800/600/stainless,bowl?lock=7",
            },

            {
                "name": "Tea Cup Set",
                "description": "Stylish tea cups perfect for everyday serving.",
                "price": 449,
                "stock": 28,
                "image": "https://loremflickr.com/800/600/tea,cups?lock=8",
            },

            {
                "name": "Coffee Mug Set",
                "description": "Modern ceramic mugs for coffee and beverages.",
                "price": 499,
                "stock": 32,
                "image": "https://loremflickr.com/800/600/coffee,mugs?lock=9",
            },

            {
                "name": "Stainless Steel Spoon Set",
                "description": "Premium stainless steel spoons with smooth finish.",
                "price": 299,
                "stock": 60,
                "image": "https://loremflickr.com/800/600/spoons?lock=10",
            },

            {
                "name": "Kitchen Knife Set",
                "description": "Sharp and durable kitchen knife set for food preparation.",
                "price": 899,
                "stock": 20,
                "image": "https://loremflickr.com/800/600/kitchen,knife?lock=11",
            },

            {
                "name": "Wooden Cooking Spoon Set",
                "description": "Natural wooden spoons suitable for everyday cooking.",
                "price": 349,
                "stock": 50,
                "image": "https://loremflickr.com/800/600/wooden,spoon?lock=12",
            },

            {
                "name": "Kitchen Spatula Set",
                "description": "Useful spatula set for frying and cooking.",
                "price": 399,
                "stock": 42,
                "image": "https://loremflickr.com/800/600/spatula?lock=13",
            },

            {
                "name": "Stainless Steel Water Bottle",
                "description": "Reusable stainless steel water bottle for daily use.",
                "price": 599,
                "stock": 35,
                "image": "https://loremflickr.com/800/600/stainless,bottle?lock=14",
            },

            {
                "name": "Kitchen Storage Container Set",
                "description": "Airtight storage containers for organized kitchens.",
                "price": 999,
                "stock": 27,
                "image": "https://loremflickr.com/800/600/kitchen,containers?lock=15",
            },

            {
                "name": "Serving Tray",
                "description": "Elegant serving tray for tea, snacks and meals.",
                "price": 649,
                "stock": 24,
                "image": "https://loremflickr.com/800/600/serving,tray?lock=16",
            },

            {
                "name": "Stainless Steel Jug",
                "description": "Strong and stylish stainless steel water jug.",
                "price": 699,
                "stock": 20,
                "image": "https://loremflickr.com/800/600/stainless,jug?lock=17",
            },

            {
                "name": "Dinner Spoon and Fork Set",
                "description": "Complete spoon and fork set for family dining.",
                "price": 549,
                "stock": 38,
                "image": "https://loremflickr.com/800/600/cutlery?lock=18",
            },

            {
                "name": "Kitchen Measuring Cup Set",
                "description": "Accurate measuring cups for cooking and baking.",
                "price": 299,
                "stock": 33,
                "image": "https://loremflickr.com/800/600/measuring,cups?lock=19",
            },

            {
                "name": "Premium Kitchen Utensil Set",
                "description": "Complete kitchen utensil collection for modern homes.",
                "price": 1199,
                "stock": 15,
                "image": "https://loremflickr.com/800/600/kitchen,utensils?lock=20",
            },
        ]

        added = 0

        for item in products:

            product, created = Product.objects.update_or_create(
                name=item["name"],
                defaults={
                    "description": item["description"],
                    "price": item["price"],
                    "stock": item["stock"],
                    "image": item["image"],
                }
            )

            if created:
                added += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"SUCCESS: {added} new products added/updated."
            )
        )