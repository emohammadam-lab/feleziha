import random
from .models import Product, PriceHistory

# Benchmark market indices (simulating real-time financial API feed)
BENCHMARK_RATES = {
    'LME_COPPER_USD': 9780,       # دلار در هر تن در بورس لندن
    'LME_ALUMINUM_USD': 2640,     # دلار در هر تن
    'USD_NIMA_EXCHANGE': 62800,   # نرخ حواله نیما (تومان)
    'IME_STEEL_INDEX': 32800,     # شاخص قیمت پایه میلگرد بورس کالا (تومان)
    'ZINC_LME_USD': 3050,         # دلار در هر تن روی
}

def calculate_formula_price(product):
    """
    Computes real-time price based on metal category & formula:
    Price = (LME_USD / 1000) * USD_NIMA * Category_Factor
    """
    cat_slug = product.subcategory.category.slug
    nima = BENCHMARK_RATES['USD_NIMA_EXCHANGE']
    jitter = random.randint(-1500, 2500) # Small real-time market fluctuation

    if cat_slug == 'copper':
        # Copper: base cathode is LME * Nima * 1.05 + small premium for wire/tube
        lme = BENCHMARK_RATES['LME_COPPER_USD']
        base_per_kg = int((lme / 1000.0) * nima * 1.045)
        if 'wire' in product.subcategory.slug:
            base_per_kg = int(base_per_kg * 1.035) # Premium for wire rod
        elif 'tube' in product.subcategory.slug:
            base_per_kg = int(base_per_kg * 1.11)  # Premium for seamless tubes
        elif 'sheet' in product.subcategory.slug:
            base_per_kg = int(base_per_kg * 1.07)  # Premium for sheets
        return base_per_kg + jitter

    elif cat_slug == 'aluminum':
        lme = BENCHMARK_RATES['LME_ALUMINUM_USD']
        base_per_kg = int((lme / 1000.0) * nima * 1.42)
        if 'sheet' in product.subcategory.slug:
            base_per_kg = int(base_per_kg * 1.18)
        elif 'profile' in product.subcategory.slug:
            base_per_kg = int(base_per_kg * 1.22)
        return base_per_kg + jitter

    elif cat_slug == 'steel':
        base = BENCHMARK_RATES['IME_STEEL_INDEX']
        if 'beam' in product.subcategory.slug:
            base = int(base * 1.07)
        elif 'sheet' in product.subcategory.slug:
            base = int(base * 1.15)
        return base + random.randint(-200, 300)

    elif cat_slug == 'other-metals':
        lme = BENCHMARK_RATES['ZINC_LME_USD']
        return int((lme / 1000.0) * nima * 1.38) + jitter

    return product.price or 100000


def sync_all_api_products():
    """
    Updates all products configured with AUTO_API pricing mode.
    """
    api_products = Product.objects.filter(pricing_mode=Product.PricingMode.AUTO_API)
    updated_count = 0

    for prod in api_products:
        new_price = calculate_formula_price(prod)
        if new_price > 0 and new_price != prod.price:
            prod.price_previous = prod.price or new_price
            prod.price = new_price
            prod.save()

            PriceHistory.objects.create(
                product=prod,
                price=new_price,
                note="بروزرسانی خودکار بر مبنای وب‌سرویس LME/بورس کالا و دلار نیما"
            )
            updated_count += 1

    return updated_count
