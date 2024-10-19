import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os


Auth = "./API_KEY/local-snow-429706-d4-e028ed82a83f.json" # ここにjsonファイルのPathを入力する
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Auth
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials = Credentials.from_service_account_file(Auth, scopes=scope)
Client = gspread.authorize(credentials)

SpreadSheet = Client.open_by_key("1kP892zDoyfpohOZKooVUZmcdfX6Y0FebYOiJTGsS6jY")
RawData = SpreadSheet.worksheet("入力用(京阪神)")
Data = pd.DataFrame(RawData.get_all_values())
print(Data)