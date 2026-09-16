import os
import sys
import json
import time
import asyncio
from datetime import datetime

# Add API to path to import models and core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../api')))

import redis
from sqlalchemy.orm import Session
from core.database import SessionLocal
from core.config import settings
from models.notification import Notification

try:
    redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception:
    redis_client = None

def process_notifications():
    if not redis_client:
        print("No Redis connection for worker.")
        return
        
    print("Started Notification Worker. Listening to 'notifications_queue'...")
    
    while True:
        try:
            # Block until an item is available
            item = redis_client.brpop("notifications_queue", timeout=5)
            if item:
                _, payload_str = item
                payload = json.loads(payload_str)
                
                db: Session = SessionLocal()
                try:
                    # 1. Save to PostgreSQL
                    notification = Notification(
                        user_id=payload["user_id"],
                        type=payload["type"],
                        title=payload["title"],
                        body=payload["body"],
                        entity_type=payload["entity_type"],
                        entity_id=payload["entity_id"],
                        action_url=payload["action_url"]
                    )
                    db.add(notification)
                    db.commit()
                    db.refresh(notification)
                    
                    # 2. WebSocket Push via Redis Pub/Sub
                    # The API's ws.py will listen to this channel
                    ws_payload = {
                        "type": "notification.new",
                        "payload": {
                            "id": str(notification.id),
                            "type": notification.type,
                            "title": notification.title,
                            "body": notification.body,
                            "created_at": notification.created_at.isoformat(),
                            "action_url": notification.action_url
                        }
                    }
                    redis_client.publish(f"user_channel:{payload['user_id']}", json.dumps(ws_payload))
                    
                    # 3. Simulate Email (Never silently pretend)
                    # Checking user preferences could happen here
                    print(f"[EMAIL MOCK] Sending email to User {payload['user_id']}: {payload['title']}")
                    
                except Exception as e:
                    print(f"Error processing notification: {e}")
                finally:
                    db.close()
        except Exception as e:
            print(f"Worker loop error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    process_notifications()

