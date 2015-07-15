#resolve overlapping in gcal
import collections, operator

eventlist= [(100,110,1), (102,112,2), (103,104,3), (101,111,4), (102,110,5), (99,100,9), (109,115,9)] # unsorted
valuedict = {} # temporary to keep account about ongoing parallel events
defaultvalue = 0 
value=defaultvalue
start = 0
end = 0

tslist = []
valuelist = []
valuedict={} # to keep account about overlappings values, value:start
tsdict = {} # to keep account account about all times start + stop

print(eventlist) # debug
sortedeventsbystart = sorted(eventlist, key=lambda event:event[0])

for i in range(len(eventlist)):
    start = sortedeventsbystart[i][0]
    end = sortedeventsbystart[i][1]
    value = sortedeventsbystart[i][2]
    #valuedict.update({value : (start, end)})
    tsdict.update({end : (None,start,end,value)}) # ending event
    tsdict.update({start : (value,start,end,value)}) # start ts may ovewrite some other end
    
sortedtsdict  = collections.OrderedDict(sorted(tsdict.items()))  # members are (ts,value)
#sortedtsdict = sorted(tsdict.items(), key=operator.itemgetter(0))
##print('sortedtsdict',sortedtsdict)

for tsevent in sortedtsdict.items():
    ##print('processing sortedtsdict element',tsevent) # (ts,(value,start,end,value))
    
    if tsevent[1][0] != None: # start with new value, simple part
        tslist.append(tsevent[0])
        valuelist.append(tsevent[1][0])
        valuedict.update({tsevent[1][0] : (tsevent[0],tsevent[1][2])}) # temporary dict of currently active events. value:(start,end)
        ##print('added value',tsevent[1][0],' to valuedict')
    else: # ending the event, value None
        end = tsevent[0]
        value = tsevent[1][3]
        try:
            del valuedict[value]
            ##print('deleted from valuedict value '+str(value))
        except:
            pass # print('valuedict value '+str(value)+' was already deleted')

        # make sure there are no undeleted ended events
        deletelist=[]
        for valueevent in valuedict:
            ##print('checking valuedict element with value',valueevent,'from',valuedict[valueevent][0],'to',valuedict[valueevent][1])
            if valuedict[valueevent][1] < tsevent[0]:
                ##print('valuedict element with value ',valueevent,'to be deleted')
                deletelist.append(valueevent)
        
        ##print('deletelist',deletelist)
        for value in range(len(deletelist)):
            del valuedict[deletelist[value]]
        
        # append ts, value to the according lists if value different from previous
        
        if len(valuedict) == 0:
            valuelist.append(defaultvalue)
            tslist.append(tsevent[0])
        else:
            #print('tricky part here, find the previous value to be continued')
            sortedvaluedict = sorted(valuedict.items(), key=operator.itemgetter(1)) 
            # collections.OrderedDict(sorted(valuedict.items()))
            ##print('sortedvaluedict', sortedvaluedict)
            if valuelist[-1] != sortedvaluedict[-1][0]:
                valuelist.append(sortedvaluedict[-1][0]) # latest started is the last
                tslist.append(tsevent[0]) 
            
    ##print('valuedict after processing tsevent', tsevent, valuedict)
    

for i in range(len(tslist)): # more members here than in the original eventlist
    print('result',tslist[i], valuelist[i])