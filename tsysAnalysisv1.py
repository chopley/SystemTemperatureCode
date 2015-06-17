import pandas
import numpy
import pylab
from config import *

#read in the data from the hot cold load tests
coldOn = pandas.read_csv(coldNDOn,delimiter=",",header=45)
coldOff = pandas.read_csv(coldNDOff,delimiter=",",header=45)
hotOn = pandas.read_csv(hotNDOn,delimiter=",",header=45)
hotOff = pandas.read_csv(hotNDOff,delimiter=",",header=45)

data  = coldOn
data["Freq"] = coldOn["Freq. [Hz]"]
data["Cold_ND_On"]= numpy.interp(data["Freq"],coldOn["Freq. [Hz]"],coldOn["Magnitude [W]"])
data["Cold_ND_Off"]= numpy.interp(data["Freq"],coldOff["Freq. [Hz]"],coldOff["Magnitude [W]"])
data["Hot_ND_On"]= numpy.interp(data["Freq"],hotOn["Freq. [Hz]"],hotOn["Magnitude [W]"])
data["Hot_ND_Off"]= numpy.interp(data["Freq"],hotOff["Freq. [Hz]"],hotOff["Magnitude [W]"])

#read in the noise diode ENR tables
noiseDiode = pandas.read_csv("noiseDiode.csv")
noiseDiode["Temp"] = 10**(noiseDiode["ENR"]/10)*290-290
noiseDiode["Temp+"] = 10**((noiseDiode["ENR"]+0.02)/10)*290-290
noiseDiode["Temp-"] = 10**((noiseDiode["ENR"]-0.02)/10)*290-290
noiseDiodePoly = numpy.polyfit(noiseDiode["Freq"]*1e9,noiseDiode["Temp"],4)
noiseDiodePolyP = numpy.polyfit(noiseDiode["Freq"]*1e9,noiseDiode["Temp+"],4)
noiseDiodePolyN = numpy.polyfit(noiseDiode["Freq"]*1e9,noiseDiode["Temp-"],4)
data["NoiseDiode"]= numpy.polyval(noiseDiodePoly, data["Freq"])
data["NoiseDiode+"]= numpy.polyval(noiseDiodePolyP, data["Freq"])
data["NoiseDiode-"]= numpy.polyval(noiseDiodePolyN, data["Freq"])


#read in the coupler parameters
coupler = pandas.read_csv("ndcoupler.csv",delimiter=couplerDelimit)

#read in the sma parameters
smaConnector = pandas.read_csv("smaConnector.csv",delimiter=smaConnectorDelimit)

data["coupler"]=numpy.interp(data["Freq"],coupler["Freq(GHz)"]/1e9,coupler[couplerPath])
data["sma"]=numpy.interp(data["Freq"],smaConnector["Frequency (GHz)"]/1e9,smaConnector["Calculated SMAm-SMAm"])
#the e diode loss will be the sma gain * coupler gain
data["ndLoss"]=(10**(data["sma"]/10))*data["coupler"]
data["tndEff"] = data["NoiseDiode"]*data["ndLoss"]
data["tndEff+"] = data["NoiseDiode+"]*data["ndLoss"]
data["tndEff-"] = data["NoiseDiode-"]*data["ndLoss"]


pylab.ion()
#calculate the noise diode contributions
data["ND_Diff_Hot"]= data["Hot_ND_On"]-data["Hot_ND_Off"]
data["ND_Diff_Cold"]= data["Cold_ND_On"]-data["Cold_ND_Off"]

data["Watt_Kelvin"]=data["ND_Diff_Cold"]/data["tndEff"]

print data["tndEff+"]
print data["tndEff-"]
print data["tndEff"]

pylab.plot(data["Freq"],data["tndEff"])
pylab.fill_between(numpy.array(data["Freq"]),numpy.array(data["tndEff-"]),numpy.array(data["tndEff+"]),alpha=alphaVal)
pylab.title(['T Noise diode',titleAppend])
pylab.xlabel(['Freq [Hz'])
pylab.ylabel('T [K]')
pylab.xlim(freq)
#pylab.ylim(320, 330)
pylab.grid()
pylab.savefig('TNoiseDiode.png',format='png')
pylab.close()

pylab.plot(data["Freq"],data["Hot_ND_Off"]/data["Watt_Kelvin"])
pylab.plot(data["Freq"],data["Cold_ND_Off"]/data["Watt_Kelvin"])
pylab.plot(data["Freq"],data["Cold_ND_On"]/data["Watt_Kelvin"])
pylab.title(['Calibrated Tsys Dish',titleAppend])
pylab.xlabel(['Freq [Hz'])
pylab.ylabel('Tsys [K]')
pylab.xlim(freq)
pylab.legend(['Hot Load','Cold Sky','Cold Sky +ND'])
pylab.grid()
pylab.savefig('DishNDCalTsys.png',format='png')
pylab.close()




pylab.plot(data["Freq"],data["ND_Diff_Hot"])
pylab.plot(data["Freq"],data["ND_Diff_Cold"])
pylab.grid()
pylab.title(['<Delta> Noise Diode',titleAppend])
pylab.xlabel('Frequency [Hz]')
pylab.ylabel('NDon - NDOff [W]')
pylab.ylim(4e-11,1e-10)
pylab.xlim(freq)
pylab.legend(['Hot','Cold'])
pylab.savefig('DeltaNoiseDiode.png',format='png')
pylab.close()


pylab.plot(data["Freq"],data["Hot_ND_Off"])
pylab.plot(data["Freq"],data["Cold_ND_Off"])
pylab.grid()
pylab.title(['Total Power',titleAppend])
pylab.xlabel('Frequency [Hz]')
pylab.ylabel('Power [W]')
pylab.ylim(4e-11,1e-10)
pylab.xlim(freq)
pylab.legend(['Hot','Cold'])
pylab.savefig('totalPower.png',format='png')
pylab.close()

#first measurements of the tsys using the hot/cold load
data["Y"]  = data["Hot_ND_Off"]/data["Cold_ND_Off"]
data["Tsys"]  = Thot/(data["Y"] - 1)
data["Tsys+"]  = (Thot+5)/(data["Y"] - 1)
data["Tsys-"]  = (Thot-5)/(data["Y"] - 1)
data["Trx"] = (Thot-data["Y"]*Tcold)/(data["Y"]-1)
data["Trx+"] = (Thot+5 -data["Y"]*(Tcold-2))/(data["Y"]-1)
data["Trx-"] = (Thot-5 - data["Y"]*(Tcold+2))/(data["Y"]-1)

#first measurements of the tsys using the noise diode
data["YND"]  = data["Cold_ND_On"]/data["Cold_ND_Off"]
data["TrxND"] = (data["tndEff"]-data["YND"]*Tcold)/(data["YND"]-1)
data["TrxND+"] = (data["tndEff+"]-data["YND"]*Tcold)/(data["YND"]-1)
data["TrxND-"] = (data["tndEff-"]-data["YND"]*Tcold)/(data["YND"]-1)
data["TrxND2"] = (data["tndEff"])/(data["YND"]-1)
data["TrxND2+"] = (data["tndEff+"])/(data["YND"]-1)
data["TrxND2-"] = (data["tndEff-"])/(data["YND"]-1)

pylab.plot(data["Freq"],data["Trx"])
pylab.fill_between(numpy.array(data["Freq"]),numpy.array(data["Trx-"]),numpy.array(data["Trx+"]),alpha=alphaVal)
pylab.grid()
pylab.title(['Tsys Measured Using Hot load on dish ',titleAppend])
pylab.ylabel('Tsys [K]')
pylab.xlabel('Frequency [Hz]')
pylab.ylim((75,200))
pylab.xlim(freq)
pylab.savefig('TsysHotLoad.png',format='png')
pylab.close()


pylab.plot(data["Freq"],data["Tsys"])
pylab.fill_between(numpy.array(data["Freq"]),numpy.array(data["Tsys-"]),numpy.array(data["Tsys+"]),alpha=alphaVal)
pylab.grid()
pylab.title(['Tsys Measured Using Hot load on dish ',titleAppend])
pylab.ylabel('Tsys [K]')
pylab.xlabel('Frequency [Hz]')
pylab.ylim((75,200))
pylab.xlim(freq)
pylab.savefig('TsysHotLoadGeorge.png',format='png')
pylab.close()

pylab.plot(data["Freq"],data["TrxND"])
pylab.fill_between(numpy.array(data["Freq"]),numpy.array(data["TrxND-"]),numpy.array(data["TrxND+"]),alpha=alphaVal)
pylab.grid()
pylab.title(['Trx Measured Using Noise Diode ',titleAppend])
pylab.ylabel('Trx [K]')
pylab.xlabel('Frequency [Hz]')
pylab.ylim((75,200))
pylab.xlim(freq)
pylab.savefig('TsysND.png',format='png')
pylab.close()

pylab.plot(data["Freq"],data["TrxND2"])
pylab.fill_between(numpy.array(data["Freq"]),numpy.array(data["TrxND2-"]),numpy.array(data["TrxND2+"]),alpha=alphaVal)
pylab.grid()
pylab.title(['Trx Measured Using Noise Diode-George ',titleAppend])
pylab.ylabel('Trx [K]')
pylab.xlabel('Frequency [Hz]')
pylab.ylim((75,200))
pylab.xlim(freq)
pylab.savefig('TsysND2.png',format='png')
pylab.close()
