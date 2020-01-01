import re
from getpass import getpass

from hashlib import sha256
from base64 import b64encode as b64enc

def get_pass_strength(pwd, minval=0.0, maxval=1.0, minlen=8):

    score = 1.0
    # decrease score by 0.1 for each char-count < 8
    score -= max((minlen - len(pwd)) / 10, 0)
    # decrease score based char-types in pass
    if re.compile(r"[A-Z]").search(pwd) is None:
        score -= maxval / 4
    if re.compile(r"[a-z]").search(pwd) is None:
        score -= maxval / 4
    if re.compile(r"[0-9]").search(pwd) is None:
        score -= maxval / 4
    return max(score, 0)

def get_strong_pass(text="Password: ", text_again="Password (again): ",
                    pass_th=0.9):

    p1, p2 = None, False
    while p1 != p2:
        p1 = getpass(text).strip()
        p2 = getpass(text_again).strip()

    st = get_pass_strength(p1)
    if st >= pass_th:
        return p1
    print(f"password too weak, strength: {st} < {pass_th}")

def get_pass_hash(pwd, salt=None, meth="sha256"):
    if not isinstance(pwd, bytes):
        pwd = pwd.encode("utf-8")

    if salt is not None:
        if not isinstance(salt, bytes):
            salt = salt.encode("utf-8")
        pwd = salt + pwd

    if meth == "sha256":
        return b64enc(sha256(pwd).digest()).decode()
    print(f"Unknown hashing method: {meth}")
    return None


if __name__ == "__main__":
    p =  None
    while p is None:
        p = get_strong_pass()
        print()

    print (p)
    print(get_pass_hash(p))



