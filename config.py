# config.py:
freq = (4.92e9,5.1e9)
#name of the header that the noise diode path follows through the coupler
couplerPath =  "GainS13Path"
#title headers
titleAppend = '5.0 GHz Bottom'
#thot and tcold assumption
Thot  = 273+36
Tcold = 2.7 + 3 + 5 + 1 + 1

coldNDOn = '5_cold_bottomchannel_ndon.csv'
coldNDOff = '5_cold_bottomchannel_ndoff.csv'
hotNDOn = '5_hot_bottomchannel_ndon.csv'
hotNDOff = '5_hot_bottomchannel_ndoff.csv'

couplerDelimit = "\t"
smaConnectorDelimit = ","
alphaVal = 0.3
