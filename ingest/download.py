from sec_edgar_downloader import Downloader

# The SEC requires a name and a real email
dl = Downloader("Spoorthy Nadella", "spoorthynadellas@gmail.com", "data/raw")

# Download the latest 10-K for Apple
dl.get("10-K", "AAPL", limit=1)
print("Done")