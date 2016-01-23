--modbus di and do channels, read/write 1 modbus register at the time (LSW=AIasDI , MSW=DI). correct name should be didochannels...
-- member 1..n defines multivalue service content. mixed input and output channels in one service are also possible!
-- status and dsc are last known results, see timestamp ts as well when using
-- also power counting may be involved, see cfg 

-- CONF BITS
-- # 1 - value 1 = warningu (values can be 0 or 1 only)
-- # 2 - value 1 = critical, 
-- # 4 - value inversion before status
-- # 8 - input value to member value inversion
-- # 16 - immediate notification on value change (whole multivcalue service will be (re)reported)
-- # 32 - this channel is actually a writable coil output, not a bit from the register (takes value 0000 or FF00 as value to be written, function code 05 instead of 06!)
--     when reading coil, the output will be in the lowest bit, so 0 is correct as bit value

-- # block sending. 1 = read, but no notifications to server. 2=do not even read, temporarely register down or something...

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE dichannels(mba,regadd,bit,val_reg,member,cfg,block,value,status,ts,chg,desc,regtype,ts_msg,type integer,mbi integer); -- ts_msg =notif

-- di mba1 kytteruumis K1A. kuhugi ka valisvalgus, uks, varav jms. valisukse juurde oma laiendus?
-- adi kanalid on analoogsisendid, st voimalikud pinged 3.8, 4.0, 4.5 voi 0v. liikumine 3.8 ja liikumise puudumine 4.0V!
-- kuidas saada ai olek di sisendiks? eks ikka tarkvaralise teisendusmooduliga... samas ka ai olekuid vaja? katkestuse ja lyhise vastu. 
INSERT INTO "dichannels" VALUES('','','0','DA1W','1','17','0','0','','','','kytteruumi PIR','s','',0,0); -- tehakse ai kaudu
INSERT INTO "dichannels" VALUES('','','1','DA1W','2','17','0','0','','','','esiku PIR','s','',0,0); --  virtual, ai kaudu
INSERT INTO "dichannels" VALUES('','','2','DA1W','3','17','0','0','','','','halli PIR','s','',0,0); --  virtual
INSERT INTO "dichannels" VALUES('','','3','DA1W','4','17','0','0','','','','saunadush PIR','s','',0,0); -- virtual
INSERT INTO "dichannels" VALUES('1','1','4','DA1W','5','17','0','0','','','','','h','',0,0); -- vaba siit allapoole
INSERT INTO "dichannels" VALUES('1','1','5','DA1W','6','17','0','0','','','','','h','',0,0); -- 
INSERT INTO "dichannels" VALUES('1','1','6','DA1W','7','17','0','0','','','','','h','',0,0); -- 
INSERT INTO "dichannels" VALUES('1','1','7','DA1W','8','17','0','0','','','','','h','',0,0); -- 

INSERT INTO "dichannels" VALUES('1','1','8','DI1W','1','17','0','0','','0','','VALISVALGUS LYLITI','h','',0,0); -- enne relee1
INSERT INTO "dichannels" VALUES('1','1','9','DI1W','2','17','0','0','','0','','','h','',0,0); -- relee 2
INSERT INTO "dichannels" VALUES('1','1','10','DI1W','3','17','0','0','','0','','','h','',0,0); --
INSERT INTO "dichannels" VALUES('1','1','11','DI1W','4','17','0','0','','0','','lyl_heli','h','',0,0); -- heli
INSERT INTO "dichannels" VALUES('1','1','12','DI1W','5','17','0','0','','0','','','h','',0,0); --
INSERT INTO "dichannels" VALUES('1','1','13','DI1W','6','17','0','0','','0','','','h','',0,0); --
INSERT INTO "dichannels" VALUES('1','1','14','DI1W','7','17','0','0','','0','','lyl_kuur','h','',0,0); -- kuur
INSERT INTO "dichannels" VALUES('1','1','15','DI1W','8','17','0','0','','0','','kytteruumi valgus','h','',0,0); --

INSERT INTO "dichannels" VALUES('1','0','8','DO1W','1','17','0','0','','0','','VALISVALGUS RELEE1','h','',0,0); -- relee1
INSERT INTO "dichannels" VALUES('1','0','9','DO1W','2','17','0','0','','0','','di1 p1 in','h','',0,0); -- relee 2
INSERT INTO "dichannels" VALUES('1','0','10','DO1W','3','17','0','0','','0','','di1 p1 in','h','',0,0); --
INSERT INTO "dichannels" VALUES('1','0','11','DO1W','4','17','0','0','','0','','kab _lagi','h','',0,0); -- heli
INSERT INTO "dichannels" VALUES('1','0','12','DO1W','5','17','0','0','','0','','di1 p1 in','h','',0,0); --
INSERT INTO "dichannels" VALUES('1','0','13','DO1W','6','17','0','0','','0','','di1 p1 in','h','',0,0); --
INSERT INTO "dichannels" VALUES('1','0','14','DO1W','7','17','0','0','','0','','kuur_lagi','h','',0,0); -- kuur
INSERT INTO "dichannels" VALUES('1','0','15','DO1W','8','17','0','0','','0','','kytteruumi valgus relee 8','h','',0,0); -- RELEE 8


INSERT INTO "dichannels" VALUES('2','1','8','DI2W','1','17','0','0','','0','','hall_valgus','h','',0,0); -- 0100
INSERT INTO "dichannels" VALUES('2','1','9','DI2W','2','17','0','0','','0','','saun_valgus','h','',0,0); -- 10
INSERT INTO "dichannels" VALUES('2','1','10','DI2W','3','17','0','0','','0','','','h','',0,0); -- 11
INSERT INTO "dichannels" VALUES('2','1','11','DI2W','4','17','0','0','','0','','','h','',0,0); -- 12
INSERT INTO "dichannels" VALUES('2','1','12','DI2W','5','17','0','0','','0','','esikLEDpaneel','h','',0,0); -- 1000
INSERT INTO "dichannels" VALUES('2','1','13','DI2W','6','17','0','0','','0','','','h','',0,0); --
INSERT INTO "dichannels" VALUES('2','1','14','DI2W','7','17','0','0','','0','','','h','',0,0); --
INSERT INTO "dichannels" VALUES('2','1','15','DI2W','8','17','0','0','','0','','','h','',0,0); --

INSERT INTO "dichannels" VALUES('2','0','8','DO2W','1','17','0','0','','0','','','h','',0,0); -- relee 9
INSERT INTO "dichannels" VALUES('2','0','9','DO2W','2','17','0','0','','0','','saun_valgus','h','',0,0); -- relee 10
INSERT INTO "dichannels" VALUES('2','0','10','DO2W','3','17','0','0','','0','','','h','',0,0); -- relee 11
INSERT INTO "dichannels" VALUES('2','0','11','DO2W','4','17','0','0','','0','','','h','',0,0); -- relee 12
INSERT INTO "dichannels" VALUES('2','0','12','DO2W','5','17','0','0','','0','','esiku_LEDpaneel','h','',0,0); -- relee 13
INSERT INTO "dichannels" VALUES('2','0','13','DO2W','6','17','0','0','','0','','','h','',0,0); --
INSERT INTO "dichannels" VALUES('2','0','14','DO2W','7','17','0','0','','0','','','h','',0,0); --
INSERT INTO "dichannels" VALUES('2','0','15','DO2W','8','17','0','0','','0','','','h','',0,0); -- RELEE 8

-- kilp 2 mba 21
INSERT INTO "dichannels" VALUES('21','0','8','DO21W','1','17','0','0','','0','','rodu_lyl','h','',0,0); -- RELEE 1
INSERT INTO "dichannels" VALUES('21','0','9','DO21W','2','17','0','0','','0','','_lyl','h','',0,0); -- RELEE 2
INSERT INTO "dichannels" VALUES('21','0','10','DO21W','3','17','0','0','','0','','_lyl','h','',0,0); -- RELEE 3
INSERT INTO "dichannels" VALUES('21','0','11','DO21W','4','17','0','0','','0','','_lyl','h','',0,0); -- RELEE 4
INSERT INTO "dichannels" VALUES('21','0','12','DO21W','5','17','0','0','','0','','_lyl','h','',0,0); -- RELEE 5
INSERT INTO "dichannels" VALUES('21','0','13','DO21W','6','17','0','0','','0','','_lyl','h','',0,0); -- RELEE 6
INSERT INTO "dichannels" VALUES('21','0','14','DO21W','7','17','0','0','','0','','','h','',0,0); -- Reserv
INSERT INTO "dichannels" VALUES('21','0','15','DO21W','8','17','0','0','','0','','','h','',0,0); -- Reserv

-- kilp3 mba31
INSERT INTO "dichannels" VALUES('31','1','8','DI31W','1','17','0','0','','0','','','h','',0,0); -- lyl
INSERT INTO "dichannels" VALUES('31','1','9','DI31W','2','17','0','0','','0','','','h','',0,0); -- lyl
INSERT INTO "dichannels" VALUES('31','1','10','DI31W','3','17','0','0','','0','','','h','',0,0); -- lyl
INSERT INTO "dichannels" VALUES('31','1','11','DI31W','4','17','0','0','','0','','','h','',0,0); -- lyl
INSERT INTO "dichannels" VALUES('31','1','12','DI31W','5','17','0','0','','0','','','h','',0,0); -- lyl
INSERT INTO "dichannels" VALUES('31','1','13','DI31W','6','17','0','0','','0','','','h','',0,0); -- lyl
INSERT INTO "dichannels" VALUES('31','1','14','DI31W','7','17','0','0','','0','','','h','',0,0); -- lyl
INSERT INTO "dichannels" VALUES('31','1','15','DI31W','8','17','0','0','','0','','','h','',0,0); -- lyl

-- kilp3 mba32
INSERT INTO "dichannels" VALUES('32','1','8','DI32W','1','17','0','0','','0','','','h','',0,0); -- lyl
INSERT INTO "dichannels" VALUES('32','1','9','DI32W','2','17','0','0','','0','','','h','',0,0); -- lyl
INSERT INTO "dichannels" VALUES('32','1','10','DI32W','3','17','0','0','','0','','','h','',0,0); -- lyl
INSERT INTO "dichannels" VALUES('32','1','11','DI32W','4','17','0','0','','0','','','h','',0,0); -- lyl
INSERT INTO "dichannels" VALUES('32','1','12','DI32W','5','17','0','0','','0','','','h','',0,0); -- lyl
INSERT INTO "dichannels" VALUES('32','1','13','DI32W','6','17','0','0','','0','','','h','',0,0); -- lyl
INSERT INTO "dichannels" VALUES('32','1','14','DI32W','7','17','0','0','','0','','','h','',0,0); -- lyl
INSERT INTO "dichannels" VALUES('32','1','15','DI32W','8','17','0','0','','0','','','h','',0,0); -- lyl


-- kilp4 lylitid
INSERT INTO "dichannels" VALUES('41','1','8','DI41W','1','17','0','0','','0','','m2_sein','h','',0,0); -- janar lyl
INSERT INTO "dichannels" VALUES('41','1','9','DI41W','2','17','0','0','','0','','m3_sein','h','',0,0); -- kyl
INSERT INTO "dichannels" VALUES('41','1','10','DI41W','3','17','0','0','','0','','m1_lagi','h','',0,0); -- dimmer!
INSERT INTO "dichannels" VALUES('41','1','11','DI41W','4','17','0','0','','0','','2k_koridor_lagi','h','',0,0); -- kor halogeenid
INSERT INTO "dichannels" VALUES('41','1','12','DI41W','5','17','0','0','','0','','','h','',0,0); -- 
INSERT INTO "dichannels" VALUES('41','1','13','DI41W','6','17','0','0','','0','','','h','',0,0); -- 
INSERT INTO "dichannels" VALUES('41','1','14','DI41W','7','17','0','0','','0','','','h','',0,0); -- reserv
INSERT INTO "dichannels" VALUES('41','1','15','DI41W','8','17','0','0','','0','','','h','',0,0); -- reserv 

INSERT INTO "dichannels" VALUES('42','1','8','DI42W','1','17','0','0','','0','','','h','',0,0); -- puudub, kuivati vent?
INSERT INTO "dichannels" VALUES('42','1','9','DI42W','2','17','0','0','','0','','2k_dush_valgus','h','',0,0); -- 
INSERT INTO "dichannels" VALUES('42','1','10','DI42W','3','17','0','0','','0','','wc2k_valgus','h','',0,0); -- 
INSERT INTO "dichannels" VALUES('42','1','11','DI42W','4','17','0','0','','0','','rodu_prose','h','',0,0); -- 
INSERT INTO "dichannels" VALUES('42','1','12','DI42W','5','17','0','0','','0','','','h','',0,0); -- 
INSERT INTO "dichannels" VALUES('42','1','13','DI42W','6','17','0','0','','0','','','h','',0,0); -- 
INSERT INTO "dichannels" VALUES('42','1','14','DI42W','7','17','0','0','','0','','','h','',0,0); -- 
INSERT INTO "dichannels" VALUES('','','15','DI42W','8','0','0','0','','0','','reserv4sp_energia','s','',0,0); -- ainus pullup!

--          releed
INSERT INTO "dichannels" VALUES('41','0','8','DO41W','1','17','0','0','','0','','m2_sein','h','',0,0); -- ei kasuta
INSERT INTO "dichannels" VALUES('41','0','9','DO41W','2','17','0','0','','0','','m3_sein','h','',0,0); -- 
INSERT INTO "dichannels" VALUES('41','0','10','DO41W','3','17','0','0','','0','','m1_lagi','h','',0,0); --
INSERT INTO "dichannels" VALUES('41','0','11','DO41W','4','17','0','0','','0','','2k_koridor_lagi','h','',0,0); --
INSERT INTO "dichannels" VALUES('41','0','12','DO41W','5','17','0','0','','0','','vent_hi_lo','h','',0,0); --
INSERT INTO "dichannels" VALUES('41','0','13','DO41W','6','17','0','0','','0','','vent_on_off','h','',0,0); --
INSERT INTO "dichannels" VALUES('41','0','14','DO41W','7','17','0','0','','0','','','h','',0,0); --
INSERT INTO "dichannels" VALUES('41','0','15','DO41W','8','17','0','0','','0','','','h','',0,0); --

INSERT INTO "dichannels" VALUES('42','0','8','DO42W','1','17','0','0','','0','','kuivati_vent','h','',0,0); -- ei kasuta
INSERT INTO "dichannels" VALUES('42','0','9','DO42W','2','17','0','0','','0','','2k_dush_valgus','h','',0,0); -- 
INSERT INTO "dichannels" VALUES('42','0','10','DO42W','3','17','0','0','','0','','wc2k_valgus','h','',0,0); --
INSERT INTO "dichannels" VALUES('42','0','11','DO42W','4','17','0','0','','0','','rodu_prose','h','',0,0); --
INSERT INTO "dichannels" VALUES('42','0','12','DO42W','5','17','0','0','','0','','','h','',0,0); --
INSERT INTO "dichannels" VALUES('42','0','13','DO42W','6','17','0','0','','0','','','h','',0,0); --
INSERT INTO "dichannels" VALUES('42','0','14','DO42W','7','17','0','0','','0','','','h','',0,0); --
INSERT INTO "dichannels" VALUES('42','0','15','DO42W','8','17','0','0','','0','','','h','',0,0); -- 



CREATE UNIQUE INDEX di_regmember on 'dichannels'(val_reg,member);
-- NB bits and registers are not necessarily unique!

COMMIT;
