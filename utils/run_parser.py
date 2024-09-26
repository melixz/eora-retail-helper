import asyncio
from utils.parser import parse_all_urls

if __name__ == "__main__":
    print("Starting data parsing...")
    asyncio.run(parse_all_urls())
    print("Parsing completed.")
