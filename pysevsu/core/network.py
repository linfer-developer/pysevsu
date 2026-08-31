"""Сетевой клиент для асинхронной загрузки данных.

Предоставляет класс :class:`Client` для выполнения HTTP-запросов к веб-ресурсам
с учетом заданных политик повторных попыток и задержек.
"""

import asyncio
from aiohttp import ClientError
from aiohttp import ClientSession
from .exceptions import UnstableNetworkConnection
from .interfaces import _ClientProtocol
from .interfaces import RequestPolicy


class Client(_ClientProtocol):
    """Асинхронный клиент для сетевого ресурса.

    Реализует функции для взаимодействия с сетевым ресурсом, выполняющие
    GET-запросы для извлечения текстовой HTML-структуры страницы или скачивания
    содержимого в байтовом представлении.

    Связь с сервером регулируется динамическим конфигуратором
    :class:`RequestPolicy`, который ограничивает количество одновременных
    запросов, устанавливает предельное время ожидания и задержку между
    обращениями.

    Стратегия повторных попыток представлена настройкой числа допустимых сетевых
    отказов, по достижении которого система завершит работу с исключением. До
    тех пор ошибки накапливаются во внутреннем хранилище.
    """

    def __init__(
        self,
        base_url: str,
        session: ClientSession,
        request_policy: RequestPolicy,
    ) -> None:
        """Инициализирует параметры сетевого клиента.

        :param base_url: Базовый адрес веб-ресурса.
        :param session: Сеанс сетевых соединений.
        :param request_policy: Политика выполнения сетевых запросов.
        """
        self.base_url = base_url
        self.session = session
        self.request_policy = request_policy
        self._connection_errors: dict[str, Exception] = {}

    @property
    def connection_errors(self):
        """Список накопленных сетевых ошибок."""
        return self._connection_errors

    async def request(
        self,
        end_url: str,
        return_: str = "text",
        number_network_exceptions: int = 1,
        reset_network_exception_counter: bool = True,
    ) -> str | bytes | None:
        """Выполняет сетевой запрос и возвращает ответ в заданном формате.

        :param end_url: Относительный адрес ресурса.
        :param return_: Формат ответа ("text" или "bytes").
        :param number_network_exceptions: Предельное количество сетевых ошибок.
        :param reset_network_exception_counter: Флаг сброса реестра ошибок.

        :return: Текстовое или двоичное содержимое ответа.

        :raises AttributeError: Если передан неподдерживаемый формат ответа.
        :raises UnstableNetworkConnection: При превышении лимита сетевых ошибок.
        """
        if return_ in ("text", "bytes"):
            if reset_network_exception_counter is True:
                self._connection_errors.clear()

            try:
                await asyncio.sleep(self.request_policy.delay)
                if return_ == "text":
                    return await self._request_to_receive_text(end_url)
                return await self._request_to_receive_bytes(end_url)

            except (TimeoutError, ClientError) as connection_error:
                self._connection_errors[end_url] = connection_error
                if number_network_exceptions == -1:
                    return
                if len(self._connection_errors) >= number_network_exceptions:
                    raise UnstableNetworkConnection(
                        f"""Допустимый порог ошибок превысил лимит 
                        ({number_network_exceptions}). Получите список 
                        накопленных сетевых ошибок с помощью свойства 
                        connection_errors."""
                    ) from connection_error

        else:
            raise AttributeError(
                "Возврат может быть только текстом или байтами."
            )

    async def _request_to_receive_text(self, end_url: str | None = None) -> str:
        """Запрашивает и возвращает текстовое содержимое ответа.

        :param end_url: Относительный адрес ресурса.
        :return: Текстовое двоичное содержимое ответа.
        """
        async with self.session.get(
            f"{self.base_url}{end_url}" if end_url else self.base_url,
        ) as response:
            response.raise_for_status()
            return await response.text()

    async def _request_to_receive_bytes(
        self, end_url: str | None = None
    ) -> bytes:
        """Запрашивает и возвращает двоичные данные ответа.

        :param end_url: Относительный адрес ресурса.
        :return: Байтовое двоичное содержимое ответа.
        """
        async with self.session.get(
            f"{self.base_url}{end_url}" if end_url else self.base_url,
        ) as response:
            response.raise_for_status()
            return await response.read()
