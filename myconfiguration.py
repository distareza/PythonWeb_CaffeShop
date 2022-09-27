import configparser
config = configparser.RawConfigParser()
config.read(filenames="../config.properties")

google_api_key = config.get("google.com", "api-key")
secret_key = config.get("mrbond.com", "secret")