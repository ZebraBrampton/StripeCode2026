WAIT_TIME=30
JOY_FACTOR=75
ITEMS_SOLD=20


HOUR_INDEX=0
NAME_INDEX=1


TIME_INDEX=2
JOY_INDEX=3


SOLD_INDEX=2
SALES_INDEX=3








       


ridesLog = open("Galaxy Rides Log data.csv")
grLines = ridesLog.readlines()


concesLog=open("Galaxy Concessios log data.csv")
gcLines=concesLog.readlines()






ridesDict = {}
concesDict={}




for line in grLines[1:]:
    alert=False
    rideInfo = line.split(',')
    if float(rideInfo[TIME_INDEX]) > WAIT_TIME:
        alert=True


    if int((rideInfo[JOY_INDEX].replace('%',''))) < JOY_FACTOR:
        alert=True
    ridesDict[(rideInfo[HOUR_INDEX][:2], rideInfo[NAME_INDEX])] = (rideInfo[TIME_INDEX], rideInfo[JOY_INDEX][:-1], alert)
   






for line in gcLines[1:]:
    alert=False
    concesInfo = line.split(',')
    if float(concesInfo[SOLD_INDEX]) < ITEMS_SOLD:
        alert=True
    concesDict[(concesInfo[HOUR_INDEX][:2], concesInfo[NAME_INDEX])] = (concesInfo[SOLD_INDEX], concesInfo[SALES_INDEX][:-1], alert)












combinedDict = ridesDict| concesDict
#print(combinedDict)









def falsify_Key(key):
    if key in combinedDict:
        value = combinedDict[key]
        x,y,alert_value = value
        if alert_value == True:
            combinedDict[key]= (x,y,False)



def falsify_allAlerts():
    for key,value in combinedDict.items():
        print (value)
        x,y,alert_value = value
        if alert_value == True:
            combinedDict[key]= (x,y,False)



if __name__ == "__main__":
    #falsify_allAlerts()
    print("#####################################")
    print(combinedDict)


        
    key = ('12:00', 'Rocket Slingshot')


    #falsify_Key(key)
    #print(combinedDict)

