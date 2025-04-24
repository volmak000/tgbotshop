import requests

# Сопоставление названий криптовалют с их ID в API CoinGecko
CRYPTO_IDS = {
    "btc": "bitcoin",
    "ETH": "ethereum",
    "USDT_ERC20": "tether",
    "USDC_ERC20": "usd-coin",
    "TRX": "tron",
    "USDT_TRC20": "tether",
    "USDC_TRC20": "usd-coin",
    "BNB": "binancecoin",
    "USDT_BEP20": "tether",
    "BUSD": "binance-usd",
    "SOL": "solana",
    "USDC_SOL": "usd-coin",
    "LTC": "litecoin"

    
}

def convert_rub_to_crypto(amount_rub, crypto):
    crypto_id = CRYPTO_IDS.get(crypto)  # Получаем ID криптовалюты
    if not crypto_id:
        print(f"❌ Ошибка: Неизвестная криптовалюта {crypto}{crypto_id}")
        return 0.0  

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ Ошибка API: {response.status_code}")
        return 0.0  

    data = response.json()
    rate = data.get(crypto_id, {}).get("usd")

    if rate is None:
        print(f"❌ Ошибка: не удалось получить курс {crypto.upper()}")
        return 0.0  

    return round(amount_rub / rate, 6)  # Округляем до 6 знаков
