-- devices attached to the modbusRTU or modbusTCP network
BEGIN TRANSACTION;
CREATE TABLE 'devices'(num integer,rtuaddr integer,tcpaddr,mbi integer,status integer,name,location,descr); -- ebables using mixed rtu and tcp inputs

INSERT INTO 'devices' VALUES(1,1,'/dev/ttyAPP0|19200|E',0,0,'DC6888','kytteruum','kytte ja vent kontroller'); -- RS485
-- INSERT INTO 'devices' VALUES(2,1,'/dev/ttyUSB0|19200|E',1,0,'DC6888','test','hiina usb-serial'); -- RS485
-- INSERT INTO 'devices' VALUES(3,1,'10.0.0.4:10001',2,0,'','test','voc sensor'); -- RS485
-- INSERT INTO 'devices' VALUES(0,0,'10.0.0.11:502',1,0,'Barionet50','kytteruum','1w vahendaja kontroller'); -- modbusTCP to barionet50

CREATE UNIQUE INDEX num_devices on 'devices'(num); -- device ordering numbers must be unique
CREATE UNIQUE INDEX addr_devices on 'devices'(rtuaddr,tcpaddr); -- device addresses must be unique

COMMIT;
