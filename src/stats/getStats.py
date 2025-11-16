import duckdb
import pandas as pd

# import stats from DuckDB
def get_data() -> dict[str: pd.DataFrame]:
    conn = duckdb.connect()

    try:
        result = conn.execute("SELECT * FROM your_existing_table").fetchall() # replace with some fetching of DuckDB information
        for row in result:
            print(row)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        conn.close()
    
    return dict(result) # return a dictionary of dataframes, with keys for the type of data we want to pull
