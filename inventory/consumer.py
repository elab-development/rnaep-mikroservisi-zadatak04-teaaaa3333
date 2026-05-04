from database import redis
from main import Product
import time
from config import settings


key = 'order_completed'
group = 'inventory-group'

try:
    redis.xgroup_create(key, group, mkstream=True)
except:
    print('Group already exists!')

while True:
    try:
        #citaj samo nove podatke kao append mod, i uzmi samo jednu poruku za sata najsigurnije za realtime obradu
        #block 5s sacekaj ukoliko poruke jos nema
        results = redis.xreadgroup(group, key, {key: '>'}, count=1, block=5000)

        if results:
            for result in results:
                """
                [
                    ['order_completed', # [0] Ime streama
                    [                 # [1] Lista poruka
                    ('1712-0',      # [0][0] ID prve poruke
                    {'id': '123'}) # [0][1] SAMI PODACI (ono što nama treba!)
                    ]
                    ]
                    ]
                    Uzmi listu poruka iz prvog stream-a uzmi prvu poruklu 1,0 i onda uzmi sadrzaj te poruke
                """
                obj = result[1][0][1]
                try:
                    product = Product.get(obj['product_id'])
                    product.quantity -= int(obj['quantity'])
                    product.save()
                    print(f"Stock updated for {product.name}")
                except Exception as e:
                    redis.xadd('refund_order', obj, '*')
                    print(f"Error: {e}")
    except Exception as e:
        print(str(e))