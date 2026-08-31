# Документация к библиотеки pysevsu

Библиотека предоставляет поток расписания из публичного источника
Севастопольского государственного университета. Система обеспечивает высокую
производительность, возможность регулировки параметров для контроля памяти и
нагрузки, механизмы ранней и поздней фильтрации.

# Структура библиотеки:

* [pysevsu](modules.md)
  * [`create_pipeline`](modules.md#pysevsu.create_pipeline)
  * [`ScheduleExcelParser`](modules.md#pysevsu.ScheduleExcelParser)
  * [`ScheduleWebsiteParser`](modules.md#pysevsu.ScheduleWebsiteParser)
  * [core](pysevsu.core.md)
    * [`ExcelFileDownloader`](pysevsu.core.md#pysevsu.core.ExcelFileDownloader)
    * [`ExcelFileProcessor`](pysevsu.core.md#pysevsu.core.ExcelFileProcessor)
    * [`CorruptedExcelFileError`](pysevsu.core.md#pysevsu.core.CorruptedExcelFileError)
    * [`UnstableNetworkConnection`](pysevsu.core.md#pysevsu.core.UnstableNetworkConnection)
    * [`WebsiteIterator`](pysevsu.core.md#pysevsu.core.WebsiteIterator)
    * [`ExcelIterator`](pysevsu.core.md#pysevsu.core.ExcelIterator)
    * [`create_engine()`](pysevsu.core.md#pysevsu.core.create_engine)
    * [`create_network_client()`](pysevsu.core.md#pysevsu.core.create_network_client)
    * [interfaces](pysevsu.core.md#module-pysevsu.core.interfaces)
      * [`RequestPolicy`](pysevsu.core.md#pysevsu.core.interfaces.RequestPolicy)
      * [`AsyncQueue`](pysevsu.core.md#pysevsu.core.interfaces.AsyncQueue)
      * [`ThreadSafeQueue`](pysevsu.core.md#pysevsu.core.interfaces.ThreadSafeQueue)
      * [`MixedQueue`](pysevsu.core.md#pysevsu.core.interfaces.MixedQueue)
      * [`ExcelIteratorProtocol`](pysevsu.core.md#pysevsu.core.interfaces.ExcelIteratorProtocol)
      * [`ScheduleStructureIteratorProtocol`](pysevsu.core.md#pysevsu.core.interfaces.ScheduleStructureIteratorProtocol)
    * [network](pysevsu.core.md#module-pysevsu.core.network)
      * [`Client`](pysevsu.core.md#pysevsu.core.network.Client)
    * [engine](pysevsu.core.md#module-pysevsu.core.engine)
      * [`Downloader`](pysevsu.core.md#pysevsu.core.engine.Downloader)
      * [`Processor`](pysevsu.core.md#pysevsu.core.engine.Processor)
      * [`Runner`](pysevsu.core.md#pysevsu.core.engine.Runner)
  * [models](pysevsu.models.md)
    * [schemas](pysevsu.models.md#module-pysevsu.models.schemas)
      * [`Group`](pysevsu.models.md#pysevsu.models.schemas.Group)
      * [`Week`](pysevsu.models.md#pysevsu.models.schemas.Week)
      * [`Teacher`](pysevsu.models.md#pysevsu.models.schemas.Teacher)
      * [`Classroom`](pysevsu.models.md#pysevsu.models.schemas.Classroom)
      * [`Class`](pysevsu.models.md#pysevsu.models.schemas.Class)
# pysevsu

Библиотека предоставляет поток расписания из публичного источника
Севастопольского государственного университета. Система обеспечивает высокую
производительность, возможность регулировки параметров для контроля памяти и
нагрузки, механизмы ранней и поздней фильтрации.

Рекомендуемые импорты:
`CreatePipeline`,
[`ScheduleExcelParser`](#pysevsu.ScheduleExcelParser),
[`ScheduleWebsiteParser`](#pysevsu.ScheduleWebsiteParser).

### create_pipeline

псевдоним для [`Pipeline`](pysevsu.md#pysevsu.factory.Pipeline)

### ScheduleExcelParser

псевдоним для [`File`](pysevsu.sources.md#pysevsu.sources.excel.File)

### ScheduleWebsiteParser

псевдоним для [`Structure`](pysevsu.sources.md#pysevsu.sources.website.Structure)

* [core](pysevsu.core.md)
  * [`ExcelFileDownloader`](pysevsu.core.md#pysevsu.core.ExcelFileDownloader)
  * [`ExcelFileProcessor`](pysevsu.core.md#pysevsu.core.ExcelFileProcessor)
  * [`CorruptedExcelFileError`](pysevsu.core.md#pysevsu.core.CorruptedExcelFileError)
  * [`UnstableNetworkConnection`](pysevsu.core.md#pysevsu.core.UnstableNetworkConnection)
  * [`WebsiteIterator`](pysevsu.core.md#pysevsu.core.WebsiteIterator)
  * [`ExcelIterator`](pysevsu.core.md#pysevsu.core.ExcelIterator)
  * [`create_engine()`](pysevsu.core.md#pysevsu.core.create_engine)
  * [`create_network_client()`](pysevsu.core.md#pysevsu.core.create_network_client)
  * [interfaces](pysevsu.core.md#module-pysevsu.core.interfaces)
  * [network](pysevsu.core.md#module-pysevsu.core.network)
  * [engine](pysevsu.core.md#module-pysevsu.core.engine)
* [models](pysevsu.models.md)
  * [schemas](pysevsu.models.md#module-pysevsu.models.schemas)
  * [enums](pysevsu.models.md#module-pysevsu.models.enums)
  * [raw](pysevsu.models.md#module-pysevsu.models.raw)
* [sources](pysevsu.sources.md)
  * [`ExcelFileIterator`](pysevsu.sources.md#pysevsu.sources.ExcelFileIterator)
  * [`WebsiteStructureIterator`](pysevsu.sources.md#pysevsu.sources.WebsiteStructureIterator)
  * [website](pysevsu.sources.md#module-pysevsu.sources.website)
  * [excel](pysevsu.sources.md#module-pysevsu.sources.excel)

## factory

Фабричный модуль асинхронного конвейера обработки расписания.
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
# models

Пакет предоставляет модели организации выходных данных библиотеки.

## schemas

Модели схемы данных учебного расписания.

Модуль содержит структуры данных для представления ключевых доменных сущностей
расписания: академических групп ([`Group`](#pysevsu.models.schemas.Group)), учебных недель
([`Week`](#pysevsu.models.schemas.Week)), преподавателей ([`Teacher`](#pysevsu.models.schemas.Teacher)), аудиторий
([`Classroom`](#pysevsu.models.schemas.Classroom)) и учебных занятий ([`Class`](#pysevsu.models.schemas.Class)).

### *class* Group(name: str, institute: str, course: int | None = None, degree: [Degree](#pysevsu.models.enums.Degree) | None = None)

Базовые классы: `object`

Академическая группа.

#### name *: str*

#### institute *: str*

#### course *: int | None* *= None*

#### degree *: [Degree](#pysevsu.models.enums.Degree) | None* *= None*

### *class* Week(number: int, year: int, semester: str | None = None, start_date: str | None = None, end_date: str | None = None)

Базовые классы: `object`

Учебная неделя.

#### number *: int*

#### year *: int*

#### semester *: str | None* *= None*

#### start_date *: str | None* *= None*

#### end_date *: str | None* *= None*

### *class* Teacher(fullname: str)

Базовые классы: `object`

Преподаватель.

#### fullname *: str*

### *class* Classroom(cipher: str)

Базовые классы: `object`

Учебная аудитория.

#### cipher *: str*

### *class* Class(number: int, date: date, time: time, name: str, group: [Group](#pysevsu.models.schemas.Group), week: [Week](#pysevsu.models.schemas.Week), study_form: [StudyForm](#pysevsu.models.enums.StudyForm) | None = None, day: [StudyWeekday](#pysevsu.models.enums.StudyWeekday) | None = None, room: [Classroom](#pysevsu.models.schemas.Classroom) | None = None, teacher: [Teacher](#pysevsu.models.schemas.Teacher) | None = None, type_: str | None = None, subgroup: int | None = None)

Базовые классы: `object`

Учебное занятие.

Агрегирует сведения о времени и месте проведения занятия, преподавателе,
академической группе и дисциплине.

#### number *: int*

#### date *: date*

#### time *: time*

#### name *: str*

#### group *: [Group](#pysevsu.models.schemas.Group)*

#### week *: [Week](#pysevsu.models.schemas.Week)*

#### study_form *: [StudyForm](#pysevsu.models.enums.StudyForm) | None* *= None*

#### day *: [StudyWeekday](#pysevsu.models.enums.StudyWeekday) | None* *= None*

#### room *: [Classroom](#pysevsu.models.schemas.Classroom) | None* *= None*

#### teacher *: [Teacher](#pysevsu.models.schemas.Teacher) | None* *= None*

#### type_ *: str | None* *= None*

#### subgroup *: int | None* *= None*
# sources

Отвечает за парсинг и создание потока информации из HTML-структуры сайта
(URL-адресов с контекстом) и файлов электронных таблиц Excel (занятий
расписания). Определяющим требованием к реализации выступает наличие
механизмов фильтрации, за счет которых движок обеспечивает повышение
производительности на пользовательской выборке.

Рекомендуемые импорты:
[`ExcelFileIterator`](#pysevsu.sources.ExcelFileIterator)
[`WebsiteStructureIterator`](#pysevsu.sources.WebsiteStructureIterator).

### ExcelFileIterator

псевдоним для [`File`](#pysevsu.sources.excel.File)

### WebsiteStructureIterator

псевдоним для [`Structure`](#pysevsu.sources.website.Structure)

## website

Модуль синтаксического анализа HTML-содержимого раздела расписания СевГУ.

Предоставляет класс [`Structure`](#pysevsu.sources.website.Structure) для потоковой обработки веб-страницы,
извлечения ссылок на файлы документов и сопоставления их с метаданными.

### *class* Structure(content: str)

Базовые классы: [`ScheduleStructureIteratorProtocol`](pysevsu.core.md#pysevsu.core.interfaces.ScheduleStructureIteratorProtocol)

Итератор по иерархической структуре расписания.

Осуществляет последовательный разбор DOM-дерева и формирует набор
атрибутов контекста для каждой найденной ссылки на документ, который
включает следующее:

- заголовки формы обучения («Расписание учебных занятий ОФО, ОФЗО»,
  «Расписание установочной сессии ЗФО и др.);
- заголовки наименований институтов («ВТШ СПИ Факультет информационных
  технологий», «Институт перспективных исследований» и др.);
- заголовки Excel документов («1 курс Бакалавриат», «2 курс
  Специалитет», «ИТ/б-24-2-о, ИТ/б-24-3-о» и др.);
- заголовки-разделители Excel файлов («I семестр» и «II семестр»).

Такой комплект данных необходим для организации механизмов глубокой
фильтрации и расширения информационного поля расписания.

#### with_filters(filters: dict[Any, Any] | None = None) → [Structure](#pysevsu.sources.website.Structure)

Задает критерии отбора записей при итерации.

Ключи, отсутствующие в схеме атрибутов, игнорируются при фильтрации.

* **Параметры:**
  **filters** – Словарь с эталонными значениями атрибутов.
* **Результат:**
  Текущий экземпляр класса.

## excel

Обработка файлов электронных таблиц учебного расписания.

Предоставляет классы [`File`](#pysevsu.sources.excel.File) и [`Worksheet`](#pysevsu.sources.excel.Worksheet) для эффективного
потокового извлечения данных из рабочих листов. Результат является
последовательностью словарей с ключами `DataKey` .

### *class* File(content: BytesIO | bytes)

Базовые классы: [`ExcelIteratorProtocol`](pysevsu.core.md#pysevsu.core.interfaces.ExcelIteratorProtocol)

Контейнер документа электронной таблицы обеспечивает последовательную
обработку рабочих листов. Предназначен для использования в качестве
контекстного менеджера.

В Excel-документе произвольное количество рабочих листов, именованных
номерами учебных недель с приставки «уч.н.». Остальные (обычно один в
начале) отражают справочную информацию и в обработку не включаются.

#### *property* schedule_worksheets *: Iterable[[Worksheet](#pysevsu.sources.excel.Worksheet)]*

Возвращает последовательность валидных рабочих листов книги.

#### with_filters(filters: dict[Any, Any] | None = None) → [File](#pysevsu.sources.excel.File)

Задает критерии отбора записей при итерации.

* **Параметры:**
  **filters** – Словарь сопоставления ключей и их эталонных значений.
* **Результат:**
  Текущий экземпляр класса.

### *class* Worksheet(name: str, content: CalamineSheet)

Базовые классы: `object`

Обработчик отдельного рабочего листа книги.

На рабочем листе существует множество объединений, в которых данные
находятся в первой от всех слившихся ячеек. Из-за этого и многоуровневых
заголовков выбрана стратегия накопления и мутирования информации в процессе
парсинга. Шаблон внутреннего хранилища предопределен для повышения
детерминизма (`DataKey`).

#### *property* name *: str*

Наименование рабочего листа.

