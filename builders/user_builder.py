class UserBuilder:
    def __init__(self):
        self._username = "valid.user@example.com"
        self._password = "StrongP@ssw0rd"

    def with_username(self, username: str):
        self._username = username
        return self

    def with_password(self, password: str):
        """
        Устанавливает произвольный пароль (валидный или нет).
        """
        self._password = password
        return self

    def with_invalid_password(self, case: str):
        match case:
            case "short":
                self._password = "Aa1@abc"
            case "no_upper":
                self._password = "abcdef1@"
            case "no_lower":
                self._password = "ABCDEF1@"
            case "no_digit":
                self._password = "Abcdefg@"
            case "no_symbol":
                self._password = "Abcdefg1"
        return self

    def build(self):
        return {
            "username": self._username,
            "password": self._password,
        }
