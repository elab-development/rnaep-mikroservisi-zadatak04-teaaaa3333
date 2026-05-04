import time

from redis import Redis

from config import settings

redis_client = Redis(
    host=settings.redis_host, 
    port=settings.redis_port, 
    password=settings.redis_password, 
    decode_responses=True
)

def process_notifications():
    print("Notification Service je pokrenut i čeka događaje...")
    
    streams = {
        "order_completed": "$", 
        "refund_order": "$"
    }

    while True:
        try:
            results = redis_client.xread(streams, block=0)
            
            for stream_name, messages in results:
                for message_id, data in messages:
                    order_id = data.get("pk") or data.get("product_id")
                    
                    if stream_name == "order_completed":
                        print(f"--- Obaveštenje: Porudžbina {order_id} je uspešno kreirana i plaćena. ---")
                    
                    elif stream_name == "refund_order":
                        print(f"--- Obaveštenje: Porudžbina {order_id} je uspešno stornirana. ---")
                    
        except Exception as e:
            print(f"Greška u Notification servisu: {e}")
            time.sleep(2)

if __name__ == "__main__":
    process_notifications()