import re
from getpass import getpass

from hashlib import sha256
from base64 import b64encode as b64enc


class Password:
    """
    Password helper class

    [member]              [use]
    .strength             return password strength [self.min_st ... self.max_st]
    .pwd (._pwd)          the PLAIN password (property)
    .hash (._hashed_pwd)  the hashed password (property)
    .ask()                ask for a password
    """
    def __init__(self, plain_pass=None):

        # _pwd + _hashed_pwd => str()
        if plain_pass is not None and not isinstance(plain_pass, str):
            plain_pass = plain_pass.decode()
        self._pwd = plain_pass
        self._hashed_pwd = None

        self.min_st = 0.0
        self.max_st = 1.0
        self.min_len = 8
        #self.max_len = None

        self.score_th = 0.9

        self.hash_method = "sha256"
        self.salt = None

    @property
    def strength(self):
        score = 1.0
        # decrease score by 10% of max for each char-count < min_len
        score -= max((self.min_len - len(self._pwd)), 0) * (self.max_st / 10)
        # decrease score based char-types in pass (25% each)
        if re.compile(r"[A-Z]").search(self._pwd) is None:
            score -= self.max_st / 4
        if re.compile(r"[a-z]").search(self._pwd) is None:
            score -= self.max_st / 4
        if re.compile(r"[0-9]").search(self._pwd) is None:
            score -= self.max_st / 4
        return min(self.max_st, max(score, self.min_st))

    @property
    def pwd(self):
        if self._pwd is not None:
            return self._pwd
    @pwd.setter
    def pwd(self, val):
        self._pwd = val
        self._hashed_pwd = None

    @property
    def hash(self):
        if self._hashed_pwd is None:
            pwd = self._pwd[:]
            if not isinstance(self._pwd, bytes):
                pwd = self._pwd.encode("utf-8")

            if self.salt is not None:
                if not isinstance(self.salt, bytes):
                    self.salt = self.salt.encode("utf-8")
                pwd = self.salt + pwd

            if self.hash_method == "sha256":
                self._hashed_pwd = b64enc(sha256(pwd).digest()).decode()
            else:
                raise NotImplementedError("unknown password hash method")

        return self._hashed_pwd

    def ask(self, text="Password: ", text_again="Password (again): "):
        p1, p2 = None, False
        while p1 != p2:
            p1 = Password(getpass(text).strip())
            p2 = Password(getpass(text_again).strip())

        if p1.strength >= self.score_th:
            self._pwd = p1._pwd
            return p1
        print(f"too weak, strength: {p1.strength} < {self.score_th}")

    def __eq__(self, rhs):
        if isinstance(rhs, Password):
            # if same object
            return self.pwd == rhs.pwd
        # assuming str(), thus hash
        return self.hash == rhs

if __name__ == "__main__":
    p =  Password()
    while p.pwd is None:
        x = p.ask()
        print(x)

    print (p, p.hash, p.pwd)

    print("equal to self:", p == p)
    print("equal to other:", p == Password("!390ujd"))
    print("equal to hash:", p == "7eVfW8J20DZEqvsMynvtJlWmwzQGwcDfA8A2+pQuJSM=")


