def user_exist(username):
    if users.find_one({"username": username}):
        return True
    else:
        return False


def verify_pw(username, password):
    user = users.find_one({"username": username})
    if check_password_hash(user["password"], password):
        return True
    else:
        return False

def check_amount(amount):
    if amount <= 0:
        return False
    else:
        return True


def verify_credentials(username, password):
    if not user_exist(username):
        return ret_map(301, "User exist"), True
    if not verify_pw(username, password):
        return ret_map(302, "Wrong password"), True
    return None, False


def ret_map(code, msg):
    return {"Status code": code, "msg": msg}