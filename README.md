# Finding-The-Best-Coins-on-Binance-with-python-using-RSI-MACD-and-SMA-methods
Finding The Best Coins on Binance with python using RSI, MACD and SMA methods

Many indicators are used both in the stock market and in cryptocurrencies.
Investors choose suitable indicators according to their own experiences or the behavior of traders in the market and trade on the stock markets.
However, these transactions as a trader take a lot of time to determine which coin we will choose when we check it on the computer or phone.
If we are going to be a long-term investor, we can invest in that crypto money for a long time by reading the papers of the relevant coin. In this case, we can also have information about the future of crypto money by using indicators.
How The Algorithm was Designed?

In a previous article, I talked about which coin should be chosen according to the crypto behavior in the last 24 hours. The link is below.
How to decide to buy cryptocurrency using Python?
In the first step, I defined a few rules. We see the buying frequency of a crypto currency that we choose according to…medium.com
The rules was defined below:
Select last 24 hours data from Binance
RSI ≥20 && RSI ≤80. However, it should be RSI≥50 for buying signal
MACD ≥ 0
SMA(50) > SMA(200)
Close Value > SMA(50) && Close Value > SMA(200)

There are currently 514 coins in Binance spot transactions, as well as 41 coins in futures transactions.
While designing the algorithm, spot transactions in the last 24 hours are taken into account.
The best coins are automatically selected according to the rule we set in spot transactions and the best 5 coins among 514 coins are selected. Only spot market can be traded here. However, for long and short transactions, the binance exchange currently does not allow trading in the spot market. For this, the program checks whether the top 5 coins are suitable for futures transactions. If the coins comply with the rules above and can be traded in futures, the following rules should be defined.
Select last 1 minutes data from Binance
Condition 1(Position=1): SMA(5) > SMA(8) && SMA(5) > SMA(13) && SMA(8) > SMA(13)
Condition 2 (Position=-1): SMA(5) < SMA(8) && SMA(5) < SMA(13) && SMA(8) < SMA(13)
Stable Position (Position=-0): If condition1 and condition2 are not
