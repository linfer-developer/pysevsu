"""Модуль для хранения типов специализированных исключений библиотеки."""


class CorruptedExcelFileError(Exception):
    """Исключение повреждения документа ЭТ или неверного формат файла."""


class UnstableNetworkConnection(Exception):
    """Исключение большой потери запросов."""
