import pandas as pd
import io

def export_df_to_csv(df, filename="export.csv"):
    """
    Export a DataFrame to CSV bytes for download.
    Returns bytes buffer.
    """
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer.getvalue().encode('utf-8')

def export_df_to_excel(df, filename="export.xlsx"):
    """
    Export a DataFrame to Excel bytes for download.
    Returns bytes buffer.
    """
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    buffer.seek(0)
    return buffer.read()