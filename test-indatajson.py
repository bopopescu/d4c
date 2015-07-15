#!/usr/bin/python3

from droidcontroller.indata import InData
from droidcontroller.indata_pacui import InDataPacui

id = InData()

id.write('AI100', { "value" : 0.5, "status" : 2 })
id.write('TI600', { "value" : 21.3, "status" : 1 })

print(id)

conv = InDataPacui(id)
json = conv.getJSON()

print(json)

