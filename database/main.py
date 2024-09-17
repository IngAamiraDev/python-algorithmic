from sqlalchemy import create_engine, MetaData, Table, insert, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_excel_file(file_path: str, sheet_name: str = 'Sheet1') -> pd.DataFrame:
    """
    Reads data from an Excel file and returns it as a DataFrame.
    
    :param file_path: Path to the Excel file.
    :param sheet_name: Name of the Excel sheet to read from. Default is 'Sheet1'.
    :return: DataFrame containing the data from the Excel file.
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        logging.info(f"Successfully read data from {file_path}.")
        return df
    except FileNotFoundError:
        logging.error(f"Error: File {file_path} not found.")
    except Exception as e:
        logging.error(f"Error reading Excel file: {e}")
    return pd.DataFrame()

def create_db_engine(user: str, password: str, host: str, port: str, db_name: str):
    """
    Creates a SQLAlchemy engine for connecting to PostgreSQL.
    
    :param user: PostgreSQL username.
    :param password: PostgreSQL password.
    :param host: PostgreSQL host address.
    :param port: PostgreSQL port (default is 5432).
    :param db_name: Name of the database.
    :return: SQLAlchemy engine object.
    """
    try:
        engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}')
        logging.info("Successfully connected to the database.")
        return engine
    except SQLAlchemyError as e:
        logging.error(f"Error creating database engine: {e}")
        return None
    
def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses the DataFrame to handle missing values and ensure data integrity.
    Replaces missing values with appropriate defaults and removes rows with null dates.
    """

    # Ensure 'Date' column is datetime type and drop rows with NaT in 'Date'
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df[df['Date'].notna()].copy()  # Make a copy to avoid SettingWithCopyWarning

    # Replace NaN values with empty strings for object columns
    object_columns = ['PDT Alert', 'Status', 'Asset']
    for col in object_columns:
        if col in df.columns:
            df.loc[:, col] = df[col].fillna('')

    # Replace NaN values with 0 for numeric columns
    numeric_columns = ['Shares', 'Cost/Shares', 'Cost Basis', 'Day Trading', 'Last Buy Price', 'Profit/Loss']
    for col in numeric_columns:
        if col in df.columns:
            df.loc[:, col] = df[col].fillna(0)

    # Optional: Remove any additional unnecessary columns if needed
    # df = df.drop(columns=['UnnecessaryColumn'])

    return df

def insert_data_to_postgresql(df: pd.DataFrame, engine, table_name: str):
    """
    Inserts a DataFrame into a PostgreSQL table.
    
    :param df: DataFrame containing data to be inserted.
    :param engine: SQLAlchemy engine for PostgreSQL connection.
    :param table_name: Target table in PostgreSQL.
    """
    if df.empty:
        logging.error("Error: DataFrame is empty. Aborting import.")
        return
    
    df = preprocess_dataframe(df)

    # Create a connection to the database
    with engine.connect() as connection:
        # Define metadata and reflect the table schema from the database
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)

        # Start a transaction
        with connection.begin():
            for index, row in df.iterrows():
                # Prepare data for insertion
                data = {
                    'date_trade': row.get('Date', pd.NaT).strftime('%Y-%m-%d') if not pd.isna(row.get('Date')) else None,
                    'status': row.get('Status', '') or '',
                    'tickers': row.get('Asset', '') or '',
                    'shares': row.get('Shares', 0) if not pd.isna(row.get('Shares')) else 0,
                    'cost_shares': row.get('Cost/Shares', 0) if not pd.isna(row.get('Cost/Shares')) else 0,
                    'cost_basis': row.get('Cost Basis', 0) if not pd.isna(row.get('Cost Basis')) else 0,
                    'count_day_trading': row.get('Day Trading', 0) if not pd.isna(row.get('Day Trading')) else 0,
                    'pdt_alert': row.get('PDT Alert', '') or '',
                    'last_buy_price': row.get('Last Buy Price', 0) if not pd.isna(row.get('Last Buy Price')) else 0,
                    'profit_loss': row.get('Profit/Loss', 0) if not pd.isna(row.get('Profit/Loss')) else 0
                }

                # Create an insert statement using SQLAlchemy Core
                stmt = insert(table).values(data)

                # Execute the insert statement
                connection.execute(stmt)

        logging.info(f"Data successfully inserted into PostgreSQL table '{table_name}'.")

def delete_null_date_rows(engine, table_name: str):
    """
    Deletes rows with null 'date_trade' from the PostgreSQL table.
    
    :param engine: SQLAlchemy engine for PostgreSQL connection.
    :param table_name: Target table in PostgreSQL.
    """
    with engine.connect() as connection:
        try:
            # Use the text construct to execute raw SQL
            delete_stmt = text(f"DELETE FROM {table_name} WHERE date_trade IS NULL")
            result = connection.execute(delete_stmt)
            logging.info(f"Deleted {result.rowcount} rows with null 'date_trade' from table '{table_name}'.")
        except SQLAlchemyError as e:
            logging.error(f"Error deleting rows: {e}")

def main():
    # File and database parameters
    excel_file_path = r'/mnt/d/OneDrive - Fundacion Universitaria Catolica del Norte/Personal/Presupuesto_2024.xlsx'
    sheet_name = 'DAY_TRADING'
    table_name = 'trading_tracker'  # Target PostgreSQL table

    # PostgreSQL connection details
    db_config = {
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': '5432',
        'db_name': 'trading_db'
    }

    # Read data from Excel
    df = read_excel_file(excel_file_path, sheet_name)

    # Create PostgreSQL engine
    engine = create_db_engine(db_config['user'], db_config['password'], db_config['host'], db_config['port'], db_config['db_name'])

    if engine:
        # Insert data into PostgreSQL
        insert_data_to_postgresql(df, engine, table_name)
        # Delete rows with null 'date_trade'
        #delete_null_date_rows(engine, table_name)
        # Ensure engine is disposed of after usage
        engine.dispose()
        logging.info("Database engine disposed.")

if __name__ == "__main__":
    main()