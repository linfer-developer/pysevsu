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

Объединяет сетевое взаимодействие, разбор HTML-структуры, многопоточную
обработку книг Excel и формирование объектов моделей в рамках единого
асинхронного менеджера контекста.

### *class* Pipeline(base_url: str = 'https://www.sevsu.ru', request_timeout: int = 30, requests_limit: int = 15, requests_delay: int = 0, requests_queue_size: int = 0, thread_queue_size: int = 0, max_workers: int = 4, excel_processor_chunk_size: int = 50)

Базовые классы: `object`

Асинхронный менеджер контекста для управления конвейером обработки.

Управляет жизненным циклом сетевых соединений, пула рабочих потоков
и промежуточных очередей передачи данных.

#### *async* run(return_objects: bool = True, filters: dict[[WebsiteDataKey](pysevsu.models.md#pysevsu.models.raw.WebsiteDataKey) | [ExcelDataKey](pysevsu.models.md#pysevsu.models.raw.ExcelDataKey), Any] | None = None) → AsyncIterator[[Class](pysevsu.models.md#pysevsu.models.schemas.Class) | dict[[WebsiteDataKey](pysevsu.models.md#pysevsu.models.raw.WebsiteDataKey) | [ExcelDataKey](pysevsu.models.md#pysevsu.models.raw.ExcelDataKey), Any]]

Запускает полный цикл обработки расписания и предоставляет поток
результатов.

* **Параметры:**
  * **return_objects** – Флаг преобразования словарей данных в объекты
    моделей.
  * **filters** – Критерии фильтрации записей.
* **Yields:**
  Элементы расписания в виде моделей или исходных словарей.
