import pandas
from GetData import run
import Client

df = pandas.DataFrame(Client.run())
print(df)

#df = pandas.DataFrame(run())
#df.to_csv("Data.csv")