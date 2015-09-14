-- rakvere pikk40 kelder

-- modbus do channels to be controlled by a local application (control.py by default).
-- reporting to monitor happens via adichannels! this table only deals with channel control, without attention to service names or members. 
-- actual channel writes will be done when difference is found between values here and in adichannels table.
-- siin puudub viide teenusele, teenus seostub vaid sisenditega.

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE dochannels(mba,regadd,bit,bootvalue,value,ts,rule,desc,comment,mbi integer); -- one line per register bit (coil). 15 columns.  NO ts???

-- regvalue is read from register, value is the one we want the register to be (written by app). write value to register to make regvalue equal!
-- if the value is empty / None, then no control will be done, just reading the register
-- but if an output is controlled out of this table, then you can also use dichannels table to monitor that channel.
-- it is possible to combine values from different modbus slaves and registers into one service. 
-- possible status values are 0..3

INSERT INTO "dochannels" VALUES('1','0','8','0','0','','','output DO1','vent',0); --  porand

-- the rule number column is provided just in case some application needs them. should be uniquely indexed!
-- NB but register addresses and bits can be on different lines, to be members of different services AND to be controlled by different rules!!!
-- virtual channels are also possible - these are defined with dir 2 in adichannels.

COMMIT;
