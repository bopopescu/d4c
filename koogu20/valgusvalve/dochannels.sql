-- modbus do channels to be written. write them as a full register in one go (06) or coils (05), see dichannels cfg. no multiregister write!
-- reporting to monitor happens via dichannels! this table only deals with channel control, without attention to service names or members. 
-- channels writes are done when value change is found. channels with block=1 are not reported as services, but still get written to reg.

-- # block values. 1 = read and write registers, but do not report to server.  2=skip everything, do not even try to read or write
-- rule can be used by the application to define the channel behavior by numbered rules located somewhere, not implemented yet

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE dochannels(mba,regadd,bit,bootvalue,value,ts,rule,desc,comment, mbi integer); -- one line per register bit (coil). 15 columns

-- regvalue is read from register, value is the one we want the register to be (written by app). write value to register to make regvalue equal!
-- if the value is empty / None, then no control will be done, just reading the register
-- but if an outpout is controlled out of this table, then you can also use dichannels table to monitor that channel.
-- it is possible to combine values from different modbus slaves and registers into one service. 
-- possible status values are 0..3

-- INSERT INTO "dochannels" VALUES('0','100','0','0','0','','CurtinClose','do 1',0); -- CurtinClose bn100 kyte3
-- INSERT INTO "dochannels" VALUES('0','1','0','0','0','','CurtinOpen','relay 2',0); -- CurtinOpen bn100 kyte3 

-- mba1
INSERT INTO "dochannels" VALUES('1','0','8','0','0','','','valisvalgustus','',0); -- 
INSERT INTO "dochannels" VALUES('1','0','9','0','0','','','','',0); -- 
INSERT INTO "dochannels" VALUES('1','0','10','0','0','','','','',0); -- 
INSERT INTO "dochannels" VALUES('1','0','11','0','0','','','kab_lagi','',0); -- heli
INSERT INTO "dochannels" VALUES('1','0','12','0','0','','','','',0); -- 
INSERT INTO "dochannels" VALUES('1','0','13','0','0','','','','',0); -- 
INSERT INTO "dochannels" VALUES('1','0','14','0','0','','','kuur_valgus','',0); -- 
INSERT INTO "dochannels" VALUES('1','0','15','0','0','','','kytteruum_valgus','',0); -- 

-- mba2
INSERT INTO "dochannels" VALUES('2','0','8','0','0','','','hall_valgus','',0); -- 
INSERT INTO "dochannels" VALUES('2','0','9','0','0','','','saun_valgus','',0); 
INSERT INTO "dochannels" VALUES('2','0','10','0','0','','','wc+wcesik','',0); -- 
INSERT INTO "dochannels" VALUES('2','0','11','0','0','','','kab_kapp','',0); -- 
INSERT INTO "dochannels" VALUES('2','0','12','0','0','','','esikLEDpaneel','',0); -- rel 13
INSERT INTO "dochannels" VALUES('2','0','13','0','0','','','','',0); -- 
INSERT INTO "dochannels" VALUES('2','0','14','0','0','','','','',0); -- 
INSERT INTO "dochannels" VALUES('2','0','15','0','0','','','','',0); -- 

-- kilp 2 mba 21 pesuruum
INSERT INTO "dochannels" VALUES('21','0','8','0','0','','','rodu_valg','',0); -- rodu dekoratiivvalgus
INSERT INTO "dochannels" VALUES('21','0','9','0','0','','','garde_lagi','',0); -- 
INSERT INTO "dochannels" VALUES('21','0','10','0','0','','','v3?','',0); -- 
INSERT INTO "dochannels" VALUES('21','0','11','0','0','','','MB_sein','',0); -- 
INSERT INTO "dochannels" VALUES('21','0','12','0','0','','','pesuruum_lagi','',0); -- 
INSERT INTO "dochannels" VALUES('21','0','13','0','0','','','peegel_valg','',0); -- 
INSERT INTO "dochannels" VALUES('21','0','14','0','0','','','vent_hi-lo','',0); -- relee 230/120
INSERT INTO "dochannels" VALUES('21','0','15','0','0','','','vent_pwm','',0); -- 1s periood

-- kilp 3 mba 31 elutuba/kook
INSERT INTO "dochannels" VALUES('31','0','8','0','0','','','koogi_lagi','',0); -- K1
INSERT INTO "dochannels" VALUES('31','0','9','0','0','','','','',0); -- K2
INSERT INTO "dochannels" VALUES('31','0','10','0','0','','','elu_lagi','',0); -- K3
INSERT INTO "dochannels" VALUES('31','0','11','0','0','','','','',0); -- K4
INSERT INTO "dochannels" VALUES('31','0','12','0','0','','','diivan','',0); -- K5
INSERT INTO "dochannels" VALUES('31','0','13','0','0','','','','',0); -- K6
INSERT INTO "dochannels" VALUES('31','0','14','0','0','','','','',0); -- 
INSERT INTO "dochannels" VALUES('31','0','15','0','0','','','','',0); -- 

-- kilp 3 mba 32 elutuba/kook
INSERT INTO "dochannels" VALUES('32','0','8','0','0','','','venthi','',0); -- K7
INSERT INTO "dochannels" VALUES('32','0','9','0','0','','','vent','',0); -- K8
INSERT INTO "dochannels" VALUES('32','0','10','0','0','','','taime','',0); -- K9
INSERT INTO "dochannels" VALUES('32','0','11','0','0','','','tugitool','',0); -- K10
INSERT INTO "dochannels" VALUES('32','0','12','0','0','','','','',0); -- 
INSERT INTO "dochannels" VALUES('32','0','13','0','0','','','','',0); -- 
INSERT INTO "dochannels" VALUES('32','0','14','0','0','','','','',0); -- 
INSERT INTO "dochannels" VALUES('32','0','15','0','0','','','','',0); -- 


-- kilp 4 2k neeme ukse juures mba 41
INSERT INTO "dochannels" VALUES('41','0','8','0','0','','','m2','',0); -- janar
INSERT INTO "dochannels" VALUES('41','0','9','0','0','','','m3','',0); -- kyl
INSERT INTO "dochannels" VALUES('41','0','10','0','0','','','m1','',0); -- neeme
INSERT INTO "dochannels" VALUES('41','0','11','0','0','','','kor_lagi','',0); -- 
INSERT INTO "dochannels" VALUES('41','0','12','0','0','','','vent_kiirus','',0); -- 
INSERT INTO "dochannels" VALUES('41','0','13','0','0','','','vent_on','',0); -- 
INSERT INTO "dochannels" VALUES('41','0','14','0','0','','','','',0); -- 
INSERT INTO "dochannels" VALUES('41','0','15','0','0','','','','',0); -- 

INSERT INTO "dochannels" VALUES('42','0','8','0','0','','','reserv','',0); -- kuivati vent ei kasuta
INSERT INTO "dochannels" VALUES('42','0','9','0','0','','','dush','',0); -- 
INSERT INTO "dochannels" VALUES('42','0','10','0','0','','','wc','',0); -- 
INSERT INTO "dochannels" VALUES('42','0','11','0','0','','','rodu_prose','',0); -- 
INSERT INTO "dochannels" VALUES('42','0','12','0','0','','','','',0); -- 
INSERT INTO "dochannels" VALUES('42','0','13','0','0','','','','',0); -- 
INSERT INTO "dochannels" VALUES('42','0','14','0','0','','','','',0); -- 
INSERT INTO "dochannels" VALUES('42','0','15','0','0','','','','',0); -- 


CREATE UNIQUE INDEX do_mbaregbit on 'dochannels'(mba,regadd,bit); -- you need to put a name to the channel even if you do not plan to report it

-- the rules should probably be unique indexed too!
-- NB but register addresses and bits can be on different lines, to be members of different services AND to be controlled by different rules!!!

COMMIT;
