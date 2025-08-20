import pandas as pd
import random
import numpy as np

def thoughput_data_generation(
    N_CUSTOMERS = 10,
    P_CUSTOMERS = [13860/55991, 9240/55991, 6930/55991, 5544/55991,
        4620/55991, 3960/55991, 3465/55991, 3080/55991, 2772/55991, 2520/55991],
    TOTAL_MONTHLY_MIN = 1000,
    TOTAL_MONTHLY_MAX = 1200,
    N_YEARS = 3,
    START_DATE = "2022-01-01",
    OUTPUT_FILE = "lumpy_customer_sales.csv",
    test = False
    ):

    end_date = pd.to_datetime(START_DATE) + pd.DateOffset(years=N_YEARS) - pd.DateOffset(days=1)
    dates = pd.date_range(start=START_DATE, end=end_date, freq='D')
    daily_sales = pd.DataFrame(index=dates, columns=["orders", "customer"], data = [(0, "")]) #type: ignore


    for month_start in pd.date_range(start=START_DATE,
        end=end_date,
        freq='MS'):
        monthly_total_quantity = random.randint(TOTAL_MONTHLY_MIN, TOTAL_MONTHLY_MAX)
        customer_quantities = np.random.multinomial(monthly_total_quantity,P_CUSTOMERS)
        customer_quantities = np.array([int(i/10) * 10 for i in customer_quantities.tolist()])
        base_days = np.linspace(4, 28, N_CUSTOMERS).astype(int)

        for i in range(N_CUSTOMERS):
            customer_id = "customer_" + str(i + 1)
            order_day = base_days[i]
            last_day_of_month = month_start.days_in_month
            order_day = max(1, min(order_day, last_day_of_month))
            order_date = pd.Timestamp(year=month_start.year, month=month_start.month, day=order_day)
            order_quantity = customer_quantities[i]
            if order_date in daily_sales.index:
                daily_sales.loc[order_date, 'orders'] += order_quantity
                daily_sales.loc[order_date, 'customer'] = customer_id
    daily_sales.reset_index(inplace=True)
    daily_sales.rename(columns={'index': 'Date'}, inplace=True)
    if test:
        daily_sales.to_csv(OUTPUT_FILE, index=False)
    return daily_sales

thoughput_data_generation(test = True)
