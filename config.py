# Configuration
symbols = ['ADA','AAVE','ALGO','ALICE','ASTR','AMB','APT','AR','ARB','AVAX','ACX','BCH','BONK','BNB','BNX',
           'BTC','CELO','CFX','COMBO','DYDX','EGLD','ETH','DEFI','DENT','DOGE','FET','FIL','FLOW',
           'GMT','GRT','HBAR','HOOK','ICP','INJ','IOTA','JTO',
           'KAVA','LEVER','LISTA','LDO','LINK','MASK','MINA','NEAR','ONDO','PEOPLE','PAXG','RENDER','RSR','RPL',
           'SAND','1000SATS','SHIB','SOL','SUI','TAO','TON','TRX','VET','WLD','XAI','XRP','XLM','ZRO']

symbols_1000_futures = ['BONK','SHIB']
symbols_no_futures = ['PAXG']

pairs = []
for symbol in symbols:
    pairs.append(f"{symbol}/USDT")  # Always add spot pair
    if symbol in symbols_1000_futures:
        pairs.append(f"1000{symbol}/USDT:USDT")  # Special futures format
    elif symbol in symbols_no_futures:
        pass
    else:
        pairs.append(f"{symbol}/USDT:USDT")  # Standard futures format

value_thresholds = {
    'default': 200000,
    **{k: 5000000 for k in ['1000SATS']},
    **{k: 1000000 for k in ['DOGE','BTC','ETH','BNB','MASK','XRP','SOL']},
    **{k: 300000 for k in ['ADA','LINK','TRX']},
    **{k: 500000 for k in ['HBAR','SUI']}
}