from login_automatic import fyers

data = {
        "symbol": "NSE:SBIN-EQ",
        "resolution": "D",
        "date_format": "1",
        "range_from": "2022-01-08",
        "range_to": "2023-01-07",
        "cont_flag": "1",
    }

candles = fyers.history(data=data)
print(candles)

# https://public.fyers.in/sym_details/NSE_CM.csv