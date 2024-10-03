from app.cache import MessageIDCache

msg_cache = MessageIDCache()

# writing test: Success
# msg_cache.create("1", "1")
# msg_cache.create("2", "2")
# msg_cache.create("3", "3")

# reading test: Success
# print(msg_cache.read("1").to_dict())
# print([msg.to_dict() for msg in msg_cache.read_n_day_old(2)])

# updating test: Success
# msg_cache.update_status("1", "accepted")
# print([msg for msg in msg_cache.data])

# deleting test: Success
# msg_cache.delete("1")
# msg_cache.delete("2")
# msg_cache.delete("3")
# print([msg for msg in msg_cache.data])
