from app.cache import MessageIDCache
from app.models import MessageID

msg_cache = MessageIDCache()

# writing test: Success
# msg_cache.create("1", "1")
# msg_cache.create("2", "2")
# msg_cache.create("3", "3")

# reading test
print(msg_cache.read("1").to_dict())
print([msg.to_dict() for msg in msg_cache.read_n_day_old(2)])
