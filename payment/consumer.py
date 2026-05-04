from database import redis
from main import Order
import time
from config import settings



key = 'refund_order'
group = 'payment-group'

try:
    # mkstream=True kreira stream ako ne postoji
    redis.xgroup_create(key, group, mkstream=True)
except:
    print('Group already exists!')

while True:
    try:
        # Koristimo block=5000 da ne trošimo CPU dok nema poruka
        results = redis.xreadgroup(group, key, {key: '>'}, count=1, block=5000)

        if results:
            for result in results:
                # Izvlačenje podataka iz poruke
                message_data = result[1][0][1]
                
                try:
                    # Tražimo porudžbinu preko PK koji je stigao u poruci
                    order = Order.get(message_data['pk'])
                    order.status = 'refunded'
                    order.save()
                    print(f"Order {order.pk} successfully refunded.")
                except Exception as e:
                    print(f"Could not find order to refund: {e}")

    except Exception as e:
        print(f"Consumer error: {e}")
    
    time.sleep(1)