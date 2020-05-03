Binance Trading Set Up  
All Binance Trading and data tools v1
This repo will work with the binance api to facilitate data and trading.

Important considerations when placing trades to comply with are the following:  
price >= minPrice
price <= maxPrice
(price-minPrice) % tickSize == 0

price <= weightedAveragePrice * multiplierUp
price >= weightedAveragePrice * multiplierDown

quantity >= minQty
quantity <= maxQty
(quantity-minQty) % stepSize == 0

price * quantity> minNotional

CEIL(qty / icebergQty) > ICEBERG_PARTS limit

number of open orders<= MAX_NUM_ORDERS

number of STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, and TAKE_PROFIT_LIMIT < maxNumAlgoOrders

(orders with icebergQty is > 0)  < maxNumIcebergOrders

orders open on the exchange < maxNumOrders

number of algo orders (STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, and TAKE_PROFIT_LIMIT) < maxNumAlgoOrders
