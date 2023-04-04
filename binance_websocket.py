import time
import websockets
import asyncio
import json


class CoinCounter:

    def __init__(self, name) -> None:
        self.name = name
        self.prices = []

    def add_data(self, price):
        """Добавляет данные в списки."""
        self.prices.append(price)

    def clean(self):
        """Очищает списки для обновления счетчика."""
        self.prices.clear()

    def calc_procent(self, full, piece):
        """Дает проценты частного от целого."""
        return (piece * 100) / full

    def calc_piece(self, first, last):
        """Дает частное, от целого."""
        return last - first

    def get_result(self):
        """Дает процент отклонения цены."""
        prices = self.prices
        current_price = prices.pop()
        try:
            negative_procent = self.calc_procent(
                sorted(prices, reverse=True)[0],
                self.calc_piece(sorted(prices, reverse=True)[0], current_price)
            )
            positive_procent = self.calc_procent(
                sorted(prices)[0],
                self.calc_piece(sorted(prices)[0], current_price)
            )
            if negative_procent < 0:
                self.add_data(current_price)
                return negative_procent
            elif positive_procent > 0:
                self.add_data(current_price)
                return positive_procent
            else:
                return 0
        except IndexError:
            self.add_data(current_price)

class OwnMovement:
    def __init__(self, name) -> None:
        self.name = name
        self.required = 0
        self.subtracted = 0

    def fill(self, required, subtracted):
        """Записываем актуальные данные."""
        self.required = required
        self.subtracted = subtracted

    def get_subtract (self):
        """Получаем собственный процент отклонения."""
        return self.required - self.subtracted

    def get_result(self, event_time):
        """Получаем результат."""
        if abs(self.get_subtract()) >= 1:
            print(f'Цена {self.name} изменилась на {self.get_subtract()} %, в {event_time}')
        else:
            pass

etherium_counter = CoinCounter(name='ethusdt')
bitcoin_counter = CoinCounter(name='btcusdt')
eth_move = OwnMovement('ethusdt')
btcusdt = {
    'c': bitcoin_counter,
}
ethusdt = {
    'c': etherium_counter,
}

coin_pairs = {
    'BTCUSDT': btcusdt,
    'ETHUSDT': ethusdt
}

async def main():
    uri = "wss://stream.binance.com:9443/stream?streams=btcusdt@miniTicker/ethusdt@miniTicker"
    async with websockets.connect(uri) as client:
        while True:
            data = json.loads(await client.recv())['data']
            event_time = time.localtime(data['E'] // 1000)
            event_time = f"{event_time.tm_hour}:{event_time.tm_min}:{event_time.tm_sec}"
            coin_pair = coin_pairs[data['s']]['c']
            coin_pair.add_data(float(data['c']))
            try:
                eth_result = etherium_counter.get_result()
                btc_result = bitcoin_counter.get_result()
                if eth_result and btc_result:
                    eth_move.fill(eth_result, btc_result)
                    eth_move.get_result(event_time)
            except IndexError:
                continue

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
