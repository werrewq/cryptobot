import unittest

from bot.config.Decrypter import Decrypter
from bot.config.SecuredConfig import SecuredConfig
from bot.config.TradingConfigProvider import TradingConfigProvider
from bot.domain.TradingStatusInteractor import TradingStatusInteractor
from bot.presentation.messenger.AuthManager import AuthManager
from bot.presentation.messenger.MessagePresenter import MessagePresenter
from unittest.mock import Mock

def prepare_presenter() -> MessagePresenter:
    trading_config = TradingConfigProvider().provide(test=True)
    decrypter = Decrypter(
        b'\xda\xff\x84\xceVQ\nr(\x99?\x8b\x074\x05\x1a\xb0\x99\x95\x14z\x96\xd0\n\xf9dB\xa4\xd5j\xcd\xfd')
    secured_config = SecuredConfig(trading_config=trading_config, decrypter=decrypter)
    trading_status_interactor = TradingStatusInteractor()
    auth_manager = AuthManager(secured_config)
    presenter = MessagePresenter(
        trading_status_interactor,
        auth_manager
    )
    return presenter

class TestMessagePresenter(unittest.TestCase):

    # Тестируем сценарий первой авторизации в боте
    def test_auth_correct_pass(self):
        presenter = prepare_presenter()
        api_mock = Mock()
        # Подключаем мок к презентеру
        presenter.attach_to_view(api_mock)
        # Тестируем сам презентер
        presenter.handle_message("qwerty",chat_id=42)
        # Проверяем результаты
        api_mock.send_message_to_id.assert_called_once_with("Вы успешно авторизировались! Бот готов к работе.", 42)
        api_mock.show_trade_buttons.assert_called_once_with(42)

    # Тестируем сценарий первой авторизации в боте с неправильным паролем
    def test_auth_uncorrect_pass(self):
        presenter = prepare_presenter()
        api_mock = Mock()
        # Подключаем мок к презентеру
        presenter.attach_to_view(api_mock)
        # Тестируем сам презентер
        presenter.handle_message("uncorrect",chat_id=42)
        # Проверяем результаты
        api_mock.send_message_to_id.assert_called_once_with("Пароль не верный!", 42)

    # Тестируем сценарий обработки сообщения после успешной авторизации
    def test_handle_message_after_auth(self):
        presenter = prepare_presenter()
        api_mock = Mock()
        # Подключаем мок к презентеру
        presenter.attach_to_view(api_mock)
        # Проходим аунтентификацию
        presenter.handle_message("qwerty",chat_id=42)
        # Проверяем аунтентификацию
        api_mock.send_message_to_id.assert_called_with("Вы успешно авторизировались! Бот готов к работе.", 42)
        api_mock.show_trade_buttons.assert_called_once_with(42)
        # Отправляем сообщение
        presenter.handle_message("Торговать", chat_id=42)
        # Проверяем результаты
        api_mock.send_message_to_id.assert_called_with("Вы нажали на кнопку! Бот начинает торговать.", 42)

    # Тестируем сценарий обработки сообщения от неаунтентифицированого пользователя
    def test_handle_message_from_another_user(self):
        presenter = prepare_presenter()
        api_mock = Mock()
        # Подключаем мок к презентеру
        presenter.attach_to_view(api_mock)
        # Проходим аунтентификацию
        presenter.handle_message("qwerty",chat_id=42)
        # Проверяем аунтентификацию
        api_mock.send_message_to_id.assert_called_with("Вы успешно авторизировались! Бот готов к работе.", 42)
        api_mock.show_trade_buttons.assert_called_once_with(42)
        # Отправляем сообщение другим пользователем
        presenter.handle_message("Торговать", chat_id=7)
        # Проверяем результаты
        api_mock.send_message_to_id.assert_called_with("Бот уже используется другим пользователем", 7)

# Запускаем тесты
if __name__ == '__main__':
    unittest.main()