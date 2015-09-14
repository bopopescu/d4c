-- needed for channelmonitor_pm.py since 29.01.2014 starman
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

INSERT INTO "aochannels" VALUES('1','53249','','65535','','','vent 1 speed','max fff0?',0); -- vent 1
INSERT INTO "aochannels" VALUES('2','53249','','65535','','','vent 2 speed','',0); -- vent 2 starman
-- vent reziimi maaravad reg 53505 (olgu 0001 modbus jaoks, 0 man jaoks) ja 53248 (wr 0002 joustab)

INSERT INTO "aochannels" VALUES('3','1','','1','','','pump 1 speed','max 200',0); -- tsirk pump 1 
INSERT INTO "aochannels" VALUES('4','1','','1','','','pump 2 speed','max 200',0); -- tsirk pump 2 starman
INSERT INTO "aochannels" VALUES('3','40','5','5','','','pump 1 on','on 4, off 4 voi 0',0); -- tsirk pump 1 starman
INSERT INTO "aochannels" VALUES('4','40','5','5','','','pump 2 on','on 4, off 4 voi 0',0); -- tsirk pump 2 starman

INSERT INTO "aochannels" VALUES('9','110','','0','','','3T ajami impulss','max 4',0); -- ajami juhtimine koos aichannels M1W
INSERT INTO "aochannels" VALUES('9','111','','0','','','3T ajami impulss','max 4',0); -- ajami juhtimine koos aichannels M1W

INSERT INTO "aochannels" VALUES('9','112','','0','','','bypass ajami impulss','max 4',0); -- ajami juhtimine koos aichannels M4W, kinni
INSERT INTO "aochannels" VALUES('9','113','','0','','','bypass ajami impulss','max 4',0); -- ajami juhtimine koos aichannels M4W, lahti

CREATE UNIQUE INDEX do_mbareg on 'aochannels'(mbi,mba,regadd); -- you need to put a name to the channel even if you do not plan to report it

-- the rule number column is provided just in case some application needs them. should be uniquely indexed!
-- NB but register addresses and bits can be on different lines, to be members of different services AND to be controlled by different rules!!!
-- virtual channels are also possible - these are defined with dir 2 in adichannels.

COMMIT;
