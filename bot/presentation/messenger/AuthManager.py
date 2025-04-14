from typing import Optional

from bot.config.SecuredConfig import SecuredConfig


class AuthManager:
    __chat_pass: str
    __authenticated_chat_id: Optional[int]

    def __init__(self, secured_config: SecuredConfig):
        self.__chat_pass = secured_config.get_chat_pass()

    def is_authenticated(self, chat_id) -> bool:
        if self.__authenticated_chat_id is None:
            return False
        return chat_id == self.__authenticated_chat_id

    def was_logged(self) -> bool:
        return self.__authenticated_chat_id is not None

    def check_pass(self, message, chat_id) -> bool:
        if self.was_logged():
            return False
        else:
            if message == self.__chat_pass:
                self.__authenticated_chat_id = chat_id
                return True
            else:
                return False

    def get_authenticated_user_id(self):
        return self.__authenticated_chat_id