import asyncio
import aiohttp
import sqlite3
from datetime import datetime

db = 'crypto_prices.db'
URL = 'https://api.binance.com/api/v3/ticker/price'
interval = 600

async def get_request(session, symbol):
    async with session.get(f'{URL}?symbol={symbol}') as response:
        return await response.json()


async def update_prices():
    while True:
        async with aiohttp.ClientSession() as session:
            conn = sqlite3.connect(db)
            cursor = conn.cursor()

            try:
                cursor.execute("CREATE TABLE IF NOT EXISTS prices (symbol TEXT, price FLOAT, updated TEXT)")

                async with session.get(URL) as response:
                    data = await response.json()
                    for item in data:
                        name = item['symbol']
                        if not name.endswith('USDT'):
                            continue
                        
                        price = float(item['price'])
                        updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                        cursor.execute("SELECT price FROM prices WHERE symbol = ?", (name,))
                        fetch = cursor.fetchone()

                        if fetch is None or abs(price - fetch[0]) > 0.001:
                            cursor.execute("INSERT OR REPLACE INTO prices VALUES (?, ?, ?)",
                                           (name, price, updated))
                            print(f'{name}: {price}$ (updated at {updated})')

                conn.commit()
            except Exception as e:
                print(f'Error: {e}')
            finally:
                cursor.close()
                conn.close()

        await asyncio.sleep(interval)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_prices())