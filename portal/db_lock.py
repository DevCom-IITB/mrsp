db_lock = False


def obtain_lock():
    global db_lock
    while db_lock:
        pass
    db_lock = True


def release_lock():
    global db_lock
    db_lock = False
