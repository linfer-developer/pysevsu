# PySEVSU – Educational Schedule Parser for SevSU

Async pipeline for fetching, parsing, and normalising educational timetables from Sevastopol State University (SevSU).  
The library downloads schedule Excel files from the university website, extracts structured data, and optionally converts it into type-safe Python dataclasses.

---

## ✨ Features

- **Asynchronous & concurrent** – Uses `aiohttp` for fast HTTP requests and a thread pool for CPU‑bound Excel parsing.
- **Automatic Excel parsing** – Handles the specific multi‑line cell format used in SevSU timetable files.
- **Filtering** – Filter schedules by institute, study form, semester, or any other metadata field.
- **Data normalisation** – Optionally transforms raw dictionaries into clean `Class` objects with `Group`, `Week`, `Teacher`, etc.
- **Robust** – Implements rate limiting, error handling, and a producer‑consumer queue for reliable processing.

---

