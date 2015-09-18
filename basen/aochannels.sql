
-- modbus do channels to be controlled by a local application (control.py by default).
-- reporting to monitor happens via adichannels! this table only deals with channel control, without attention to service names or members. 
-- actual channel writes will be done when difference is found between values here and in adichannels table.
-- siin puudub viide teenusele?

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE aochannels(mba,regadd,bootvalue,value,ts,rule,desc,comment,mbi integer); -- one line per register bit (coil). 15 columns. 
-- kasutamata: rule. 
-- lisada registergroup (jarjestikusteks kirjutamisteks)? jarjestikusi korraga kirjutamisi on aga harva oodata...
-- nii et grupeerida pole vaja! loendeid vist ka siit ei kirjuta.

INSERT INTO "aochannels" VALUES('3','1000','','','','','panel sauna temp','',0); -- PNW in aico. mba3
INSERT INTO "aochannels" VALUES('3','1001','','','','','panel bath temp','',0); -- 
INSERT INTO "aochannels" VALUES('3','1003','','','','','panel outdoor','',0); -- s401 does not support more than 2 reg
INSERT INTO "aochannels" VALUES('3','1004','','','','','panel hot water','',0); -- 
INSERT INTO "aochannels" VALUES('3','1006','','','','','panel battery','',0); -- 
INSERT INTO "aochannels" VALUES('3','1007','','','','','panel feet','',0); -- 
INSERT INTO "aochannels" VALUES('3','1009','','','','','panel lights','',0); -- 

CREATE UNIQUE INDEX do_mbareg on 'aochannels'(mbi,mba,regadd); 

-- the rule number column is provided just in case some application needs them. should be uniquely indexed!
-- NB but register addresses and bits can be on different lines, to be members of different services AND to be controlled by different rules!!!
-- virtual channels are also possible - these are defined with dir 2 in adichannels.

COMMIT;
