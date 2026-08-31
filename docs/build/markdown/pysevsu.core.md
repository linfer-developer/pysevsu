# core

Предоставляет публичные интерфейсы для реализации итеративных парсеров
веб-ресурса и документов электронных таблиц Microsoft Excel, организует
взаимосвязь сетевого клиента со сбором данных из источников в модуле
module:engine .

Рекомендуемые импорты:
[`CorruptedExcelFileError`](#pysevsu.core.CorruptedExcelFileError),
[`UnstableNetworkConnection`](#pysevsu.core.UnstableNetworkConnection),
[`WebsiteIterator`](#pysevsu.core.WebsiteIterator),
[`ExcelIterator`](#pysevsu.core.ExcelIterator),
[`create_network_client()`](#pysevsu.core.create_network_client),
[`create_engine()`](#pysevsu.core.create_engine),

### ExcelFileDownloader

псевдоним для [`Downloader`](#pysevsu.core.engine.Downloader)

### ExcelFileProcessor

псевдоним для [`Processor`](#pysevsu.core.engine.Processor)

### *exception* CorruptedExcelFileError

Базовые классы: `Exception`

Исключение повреждения документа ЭТ или неверного формат файла.

### *exception* UnstableNetworkConnection

Базовые классы: `Exception`

Исключение большой потери запросов.

### WebsiteIterator

псевдоним для [`ScheduleStructureIteratorProtocol`](#pysevsu.core.interfaces.ScheduleStructureIteratorProtocol)

### ExcelIterator

псевдоним для [`ExcelIteratorProtocol`](#pysevsu.core.interfaces.ExcelIteratorProtocol)

### create_engine(client: [Client](#pysevsu.core.network.Client), web_iterator: [ScheduleStructureIteratorProtocol](#pysevsu.core.interfaces.ScheduleStructureIteratorProtocol), downloader_queue: [AsyncQueue](#pysevsu.core.interfaces.AsyncQueue), executor: Executor, excel_iterator_model: type[[ExcelIteratorProtocol](#pysevsu.core.interfaces.ExcelIteratorProtocol)], processor_chunk_size: int, processor_queue: [MixedQueue](#pysevsu.core.interfaces.MixedQueue), filters: dict[Any, Any] | None = None) → [Runner](#pysevsu.core.engine.Runner)

Создает движок системы.

### create_network_client(base_url: str, session: Any, request_limit: int, request_timeout: int, request_delay: int) → [Client](#pysevsu.core.network.Client)

Создает асинхронный сетевой клиент системы.

## interfaces

Интерфейсы и базовые типы данных системы обработки расписания.

Модуль определяет публичные протоколы взаимодействия компонентов
очередей ([`AsyncQueue`](#pysevsu.core.interfaces.AsyncQueue), [`ThreadSafeQueue`](#pysevsu.core.interfaces.ThreadSafeQueue), [`MixedQueue`](#pysevsu.core.interfaces.MixedQueue)) и
итераторов источников данных ([`ExcelIteratorProtocol`](#pysevsu.core.interfaces.ExcelIteratorProtocol),
[`ScheduleStructureIteratorProtocol`](#pysevsu.core.interfaces.ScheduleStructureIteratorProtocol)) .

### *class* RequestPolicy(limit: int = 30, timeout: int = 15, delay: int = 0)

Базовые классы: `object`

Параметры ограничения сетевых запросов.

* **Параметры:**
  * **limit** – Предельное количество одновременных запросов.
  * **timeout** – Время ожидания ответа в секундах.
  * **delay** – Задержка между повторными запросами в секундах.

#### limit *: int* *= 30*

#### timeout *: int* *= 15*

#### delay *: int* *= 0*

### *class* AsyncQueue(\*args, \*\*kwargs)

Базовые классы: `Protocol`, `Generic`

#### *async* put(item: T) → None

#### *async* get() → T

#### *async* join() → None

#### task_done() → None

### *class* ThreadSafeQueue(\*args, \*\*kwargs)

Базовые классы: `Protocol`, `Generic`

#### put(item: T, block: bool = True, timeout: float | None = None) → None

#### get(block: bool = True, timeout: float | None = None) → T

#### join() → None

#### task_done() → None

### *class* MixedQueue(\*args, \*\*kwargs)

Базовые классы: `Protocol`, `Generic`

#### *property* async_q *: [AsyncQueue](#pysevsu.core.interfaces.AsyncQueue)*

#### *property* sync_q *: [ThreadSafeQueue](#pysevsu.core.interfaces.ThreadSafeQueue)*

### *class* ExcelIteratorProtocol(content: bytes | BytesIO)

Базовые классы: `Protocol`

#### with_filters(filters: dict[Any, Any] | None = None) → [ExcelIteratorProtocol](#pysevsu.core.interfaces.ExcelIteratorProtocol)

### *class* ScheduleStructureIteratorProtocol(content: str)

Базовые классы: `Protocol`

#### with_filters(filters: dict[Any, Any] | None = None) → [ScheduleStructureIteratorProtocol](#pysevsu.core.interfaces.ScheduleStructureIteratorProtocol)

## network

Сетевой клиент для асинхронной загрузки данных.

Предоставляет класс [`Client`](#pysevsu.core.network.Client) для выполнения HTTP-запросов к веб-ресурсам
с учетом заданных политик повторных попыток и задержек.

### *class* Client(base_url: str, session: ClientSession, request_policy: [RequestPolicy](#pysevsu.core.interfaces.RequestPolicy))

Базовые классы: `_ClientProtocol`

Асинхронный клиент для сетевого ресурса.

Реализует функции для взаимодействия с сетевым ресурсом, выполняющие
GET-запросы для извлечения текстовой HTML-структуры страницы или скачивания
содержимого в байтовом представлении.

Связь с сервером регулируется динамическим конфигуратором
`RequestPolicy`, который ограничивает количество одновременных
запросов, устанавливает предельное время ожидания и задержку между
обращениями.

Стратегия повторных попыток представлена настройкой числа допустимых сетевых
отказов, по достижении которого система завершит работу с исключением. До
тех пор ошибки накапливаются во внутреннем хранилище.

#### *property* connection_errors

Список накопленных сетевых ошибок.

#### *async* request(end_url: str, return_: str = 'text', number_network_exceptions: int = 1, reset_network_exception_counter: bool = True) → str | bytes | None

Выполняет сетевой запрос и возвращает ответ в заданном формате.

* **Параметры:**
  * **end_url** – Относительный адрес ресурса.
  * **return** – Формат ответа («text» или «bytes»).
  * **number_network_exceptions** – Предельное количество сетевых ошибок.
  * **reset_network_exception_counter** – Флаг сброса реестра ошибок.
* **Результат:**
  Текстовое или двоичное содержимое ответа.
* **Исключение:**
  * **AttributeError** – Если передан неподдерживаемый формат ответа.
  * [**UnstableNetworkConnection**](#pysevsu.core.UnstableNetworkConnection) – При превышении лимита сетевых ошибок.

## engine

Асинхронный и многопоточный механизм конвейерной обработки расписания.

Модуль реализует архитектуру «Производитель — Потребитель», разделенную на два
этапа выполнения:

1. Загрузка данных [`Downloader`](#pysevsu.core.engine.Downloader): Асинхронное получение файлов
   по сети с ограничением интенсивности запросов.
2. Обработка данных [`Processor`](#pysevsu.core.engine.Processor): Разбор документов и извлечение
   записей в пуле вычислительных потоков.
3. Координация [`Runner`](#pysevsu.core.engine.Runner): Связывание этапов загрузки и разбора
   через очереди данных с предоставлением итогового потока записей.

### *class* Downloader(client: \_ClientProtocol, iterator: [ScheduleStructureIteratorProtocol](#pysevsu.core.interfaces.ScheduleStructureIteratorProtocol), queue: [AsyncQueue](#pysevsu.core.interfaces.AsyncQueue), filters: dict[Any, Any] | None = None)

Базовые классы: `_DownloaderProtocol`

Асинхронный компонент загрузки Excel файлов расписания из сети.

Планирует одновременные HTTP-запросы на основе элементов структуры сайта,
ограничивая их количество семафором.

Использует шаблон «Производитель — Потребитель» с общей асинхронной очередью
для скачивания файлов на странице. Сетевой клиент получает содержимое
ресурса с активацией итеративного парсера веб-ресурса. Для каждого
полученного URL-адреса документов выполняется GET-запрос с последующим
размещением байтов в очереди с контекстом их расположения. Потребитель
перебирает все имеющиеся данные, генеративно возвращая информацию
фиксированными единицами.

#### run() → AsyncIterator[tuple[bytes, dict[Any, Any]]]

Предоставляет асинхронный поток загруженных файлов.

* **Yields:**
  Кортеж из двоичных данных файла и словаря метаданных.

### *class* Processor(executor: Executor, queue: [MixedQueue](#pysevsu.core.interfaces.MixedQueue), iterator_model: type[[ExcelIteratorProtocol](#pysevsu.core.interfaces.ExcelIteratorProtocol)], chunk_size: int = 50, filters: dict[Any, Any] | None = None)

Базовые классы: `_ProcessorProtocol`

Многопоточный компонент анализа файлов Excel.

Делегирует задачи разбора документов пулу потоков для исключения
блокировки цикла событий.

Проводит итеративный парсинг файлов ЭТ в новых независимых потоках,
насыщая очередь `MixedQueue` информацией с соединением контекста
расположения и расписания. Когда исходные данные заканчиваются, дается
команда на остановку очереди.

#### run(file: bytes, website_data: dict[Any, Any] | None = None) → None

Передает задачу разбора файла на выполнение в пул потоков.

* **Параметры:**
  * **file** – Двоичные данные файла Excel.
  * **website_data** – Метаданные контекста файла.

#### get_errors() → None

Проверяет результаты выполнения задач в потоках и транслирует исключения.

* **Исключение:**
  **Exception** – Возникает при сбое обработки внутри любого из потоков.

#### done() → None

Отправляет сигнал завершения обработки в очередь результатов.

#### stream() → AsyncIterator[dict[Any, Any]]

Извлекает элементы из очереди до получения маркера завершения.

### *class* Runner(processor: \_ProcessorProtocol, downloader: \_DownloaderProtocol)

Базовые классы: `_RunnerProtocol`

Координатор процессов загрузки и обработки расписания.

Начинает фоновое скачивание Excel-документов с помощью загрузчика и
запускает обработчик для независимого сбора и слияния информации.
Количество воркеров фиксировано, поэтому при полной загрузке новые
файлы электронных таблиц ожидают освобождения ресурсов. Одновременно
с процессом наполнения очереди запускается ее итерация с возвратом данных
вызываемому компоненту.

#### start() → AsyncIterator[dict[Any, Any]]

Запускает полный цикл и предоставляет поток итоговых записей.

* **Yields:**
  Объединенный словарь метаданных и полей записи расписания.
