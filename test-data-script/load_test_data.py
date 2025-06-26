import os
from dotenv import load_dotenv 

load_dotenv() 

import teradatasql

# List your SQL commands here
data_loading_queries = [
    '''
    CREATE DATABASE teddy_retailers
    AS PERMANENT = 50000000;
    ''',
    '''
    CREATE TABLE teddy_retailers.fct_order_details AS
    (
      SELECT order_id,product_id,customer_id,order_date,unit_price,quantity,amount
         FROM (
            LOCATION='/s3/dev-rel-demos.s3.amazonaws.com/ai_agent_dbt/fct_order_details.csv') as order_details
    ) WITH DATA;''',

    '''
    CREATE TABLE teddy_retailers.dim_customers AS
    (
      SELECT customer_id,first_name,last_name,email
         FROM (
            LOCATION='/s3/dev-rel-demos.s3.amazonaws.com/ai_agent_dbt/dim_customers.csv') as customers
    ) WITH DATA;
    ''',
    '''
    CREATE TABLE teddy_retailers.dim_orders AS
    (
      SELECT order_id,order_date,order_status
         FROM (
            LOCATION='/s3/dev-rel-demos.s3.amazonaws.com/ai_agent_dbt/dim_orders.csv') as orders
    ) WITH DATA;
    ''',
    '''
    CREATE TABLE teddy_retailers.dim_products AS
    (
      SELECT product_id,product_name,product_category,price_dollars
         FROM (
            LOCATION='/s3/dev-rel-demos.s3.amazonaws.com/ai_agent_dbt/dim_products.csv') as products
    ) WITH DATA;
    '''
]

def main():
    # Read connection info from environment variables
    host = os.getenv("TD_HOST")
    user = os.getenv("TD_USER")
    password = os.getenv("TD_PASSWORD")

    with teradatasql.connect(
        host=host,
        user=user,
        password=password
    ) as conn:
        with conn.cursor() as cur:
            for idx, query in enumerate(data_loading_queries, 1):
                print(f"\nExecuting query {idx}...")
                try:
                    cur.execute(query)
                    print(f"Query {idx} executed successfully.")
                except Exception as e:
                    print(f"Error executing query {idx}: {e}")

if __name__ == "__main__":
    main()