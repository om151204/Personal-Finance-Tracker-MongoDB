# Personal Finance Tracker API

A production-ready, asynchronous REST API built with **FastAPI** and **MongoDB**. This application provides comprehensive financial management, featuring advanced aggregations, full-text search, and ACID-compliant category management.

## Features

- **Transaction Management**: Full CRUD for income and expenses.
- **Advanced Filtering**: Simultaneous filtering by category, date range, type, and tags.
- **Monthly Insights**: Advanced MongoDB aggregation pipelines for financial health reports.
- **Search & Discovery**: Full-text search across titles.
- **Data Validation**: Strict Pydantic v2 enforcement for financial integrity.

---

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com)
- **Database**: [MongoDB](https://www.mongodb.com)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev)
- **Server**: Uvicorn

---

## Schema Design & Justifications

### 1. Transactions Collection
- **Date Storage**: Stored as native `datetime` objects to allow high-performance range queries and native aggregation operators (`$year`, `$month`).
- **Category Denormalization**: Stored as a string name. While a DBRef is possible, storing the name reduces the need for `$lookup` joins in the most common "List Transactions" view.
- **Tags**: Stored as an array of strings with a multikey index to support efficient "contains" filtering.

### 2. Categories Collection
- **Uniqueness**: The `name` field is unique to prevent logic collisions (e.g., having two "Food" categories).
- **Type Constraints**: The `type` field ("income", "expense", "both") acts as a constraint for front-end categorization logic.

---

## Indexing Strategy
Indexes are created programmatically on startup using `Motor`.

| Index | Collection | Type | Purpose |
| :--- | :--- | :--- | :--- |
| `date: -1` | `transactions` | Single Field | Optimizes chronological listing and "latest first" views. |
| `{ category: 1, date: -1 }` | `transactions` | Compound | Speeds up category-specific filtering combined with date sorting. |
| `{ type: 1, date: -1 }` | `transactions` | Compound | Optimizes reports filtered by Income/Expense type. |
| `{ title: "text", description: "text" }` | `transactions` | Text | Powers the full-text search across financial descriptions. |
| `name: 1` | `categories` | Unique | Enforces data integrity at the database level. |

---

## Monthly Summary Aggregation
The `/transactions/summary` endpoint utilizes a `$facet` pipeline to process the following in a single DB pass:
- **Totals**: Conditional `$sum` based on the `type` field.
- **Category Breakdown**: Groups expenses by category and calculates the percentage of total spending.
- **High Water Mark**: Uses `$sort` and `$limit` to identify the single largest expense of the month.
---
## Project Structure
```text
finance_tracker/
├── .venv/                      # Virtual environment (ignored by git)
├── finance/                    # Main package directory
│   ├── api/                    # API related modules
│   │   ├── __init__.py         # Package initializer
│   │   ├── base_models.py      # Pydantic schemas & validations
│   │   └── routes.py           # API endpoints & aggregation logic
│   ├── database/               # Data layer
│   │   ├── __init__.py         # Package initializer
│   │   └── db.py               # Database Connection and CRUD logic
│   └── __init__.py             # Makes finance a top-level package
├── .env                        # Environment variables (Mongo URI)
├── .gitignore                  # Git ignore rules
├── main.py                     # App entry point & index initialization
├── poetry.lock                 # Poetry dependency lock file
├── pyproject.toml              # Project metadata & dependencies
└── README.md                   # Project documentation
```
---
## Getting Started

1.  **Setup Environment**:
    Create a `.env` file in the root directory:
    ```env
    MONGO_URI=mongodb://localhost:27017
    DATABASE_NAME=finance_tracker
    ```

2.  **Install Dependencies**:
    ```bash
    poetry install
    ```

3.  **Run Application**:
    ```bash
    uvicorn main:app --reload
    ```

4.  **API Documentation**:
    View the interactive Swagger UI at [http://127.0.0.1](http://127.0.0.1)
---


## Conclusion
The **Personal Finance Tracker API** is built with a focus on data integrity, high-performance querying, and asynchronous scalability. By leveraging **MongoDB's Aggregation Framework** for real-time reporting, this API provides a robust foundation for modern financial applications. 

Future enhancements could include:
- **JWT Authentication** for multi-user support.
- **Export to CSV/PDF** for monthly summaries.
- **Redis Caching** for high-frequency aggregation reports.
