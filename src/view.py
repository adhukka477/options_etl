from sqlalchemy import text
from postgres_conn import Session

view_names = ['current_eod_options']

def refresh_materialized_views():

    with Session() as session:
        for view in view_names:
            try:
                # Transactions are often required; commit to persist the refresh
                query = text(f"REFRESH MATERIALIZED VIEW options_dba.{view}")
                session.execute(query)
                session.commit()
                print(f"Successfully refreshed view: {view}")
            except Exception as e:
                print(f"Error refreshing view {view}: {e}")