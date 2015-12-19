--analoogsuuruste konf lugemiseks modbusTCP kaudu, barionetist olinuxinosse. 
-- x1 ja x2 on sisendi diapasoon, y1 y2 valjundi oma (lineaarteisendus 2 punkti alusel)
-- value ja statud on viimased, arvatavasti hetkel kehtivad vaartused (kontrolli igaks juhuks ka ts vanust)
-- mitme muutujaga teenuste iga liikme jaoks on yks rida, liikme jark tahistab member. 
-- outlo ja outhi on lubatud piirid, millest yle tekib warning voi alarm vastavalt cfg sisule
-- mis asi oli block?? mis asi on avg, keskmistamise tugevus? jah, mitu korda vana vaartust tuleb votta rohkem kui uut. tekitab rc / eksponendi silumiseks.

-- CONFIG BIT MEANINGS
-- # 1 - below outlo warning, 4
-- # 2 - below outlo critical, 8 - above outhi critical
-- # 4 - above outhi warning
-- # 8   above outhi critical

-- 16 - immediate notification on status change (USED FOR STATE FROM POWER)
-- 32 - value "limits to status" inversion  - to defined forbidden area instead of allowed area
-- 64 - power flag, based on value increments, creates cp[] instance
-- 128 - state from power flag
-- 256 - notify on 20% value change (not only limit crossing that becomes activated by first 4 cfg bits)
-- 512 - do not report at all, for internal usage
-- 1024 - counter, unsigned, to be queried/restored from server on restart
    -- counters are normally located in 2 registers, but also ai values can be 32 bits.
    -- negative wcount means swapped words (barionet, npe imod)
-- 2048 ds18b20 sensor for 1wire, filter out raw 4096 and 1360 (256 and 85 degC)! signed, -127 = raw 4096 but illegal. 6400 is a good cfg value wo limit notif.
-- 4096 - signed value, all the rest are unsigned
-- 8192 - use hysteresis from block    -- counters are normally located in 2 registers, but also ai values can be 32 bits.


PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
-- CREATE TABLE aichannels(mba,regadd,val_reg,member,cfg,x1,x2,y1,y2,outlo,outhi,avg,block,raw,value,status,ts,desc,comment,type integer); -- see oli enne, acomm
CREATE TABLE aicochannels(mba,regadd,val_reg,member,cfg,x1,x2,y1,y2,outlo,outhi,avg,block,raw,value,status,ts,desc, regtype, grp integer,mbi integer,wcount integer,loref,hiref); 
-- grp is flagging channel usage - 0 for voltage, 1 for temperature, 2 for humidity

-- oma temp andurid kyttetorudel, hot ja floor_on. mbi 0, modbusrtu
-- peale ringitostmisi on  barioenti kylge jaanud 19 termoandurit

-- mba 1  9A00000709B20828 3C000007094EA4280
INSERT INTO "aicochannels" VALUES('1','601','TGW','1','6400','0','80','0','50','100','800','3','','','','','','hot water from boiler','h',3,0,1,'','4'); -- 28A44E090700003C hot
INSERT INTO "aicochannels" VALUES('0','610','TGW','2','6400','0','80','0','50','100','800','3','','','0','','','return to the boiler','h',3,1,1,'','4'); -- 282A8842 ret ???
INSERT INTO "aicochannels" VALUES('','','TGW','3','6400','0','80','0','50','100','800','3','','','380','','','hot water setpoint','s',3,0,1,'','4');  -- need some value!
INSERT INTO "aicochannels" VALUES('','','TGW','4','6400','0','80','0','50','','','3','','','800','','','hot hilim','s!',3,0,1,'','');

INSERT INTO "aicochannels" VALUES('1','600','THW','1','6400','0','80','0','50','100','320','3','','','','','','onflow to floors','h',3,0,1,'','4'); -- 2808B2090700009A floor
INSERT INTO "aicochannels" VALUES('0','611','THW','2','6400','0','80','0','50','100','320','3','','','','','','return from floors','h',3,1,1,'','4'); -- 28AA7842 
INSERT INTO "aicochannels" VALUES('','','THW','3','6400','0','80','0','50','100','320','3','','','250','','','floor onflow setpoint','s',3,1,1,'','4'); -- setpoint onfloor!
INSERT INTO "aicochannels" VALUES('','','THW','4','6400','0','80','0','50','','','3','','','370','','','floor onflow hilim','s!',3,0,1,'','');

-- edasi temp andurid barioneti kaudu. mbi 1. modbustcp
INSERT INTO "aicochannels" VALUES('0','613','T0W','1','6400','0','80','0','50','0','300','3','','','','','','cold_water_inlet 286EE441','h',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('0','608','T0W','2','6400','0','80','0','50','0','300','3','','','','','','warm_water_to_dist 28A29642','h',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('0','614','T0W','3','6400','0','80','0','50','0','300','3','','','','','','warm_water_return1 28A1DD41','h',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('0','617','T0W','4','6400','0','80','0','50','0','300','3','','','','','','warm_water_return2 28A75942','h',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('0','615','T0W','5','6400','0','80','0','50','-300','400','3','','','','','','roof? 28B5EB480100000F','h',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('0','607','T0W','6','6400','0','80','0','50','0','300','3','','','','','','tech_cellar_air 28C89342','h',3,1,1,'',''); -- oli 612
INSERT INTO "aicochannels" VALUES('0','616','T0W','7','6400','0','80','0','50','-300','300','3','','','','','','outside_air@groundlevel 28F57B1A','h',3,1,1,'','');

INSERT INTO "aicochannels" VALUES('0','616','T1W','1','6400','0','80','0','50','-300','300','3','','','','','','outside_air@groundlevel koopia','h',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('','','T1W','2','6400','0','100','0','100','100','900','1','','','330','','','hot ette, paranda virt','s',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('0','604','T1W','3','6400','0','80','0','50','0','300','3','','','','','','gas_heater_outputwater 10392A13','h',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('0','610','T1W','4','6400','0','80','0','50','0','300','3','','','','','','gas_heater_return 282A8842','h',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('','','T1W','5','6400','0','80','0','50','0','300','1','','','222','','','madal_ette paranda','s',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('0','607','T1W','6','6400','0','80','0','50','0','300','3','','','','','','floor_heatingwater_onflow 10DF2D13','h',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('0','611','T1W','7','6400','0','80','0','50','0','300','3','','','','','','floor_heatingwater_return 28AA7842','h',3,1,1,'','');

INSERT INTO "aicochannels" VALUES('0','612','T2W','1','6400','0','80','0','50','0','300','3','','','','','','vent_valjatomme 2846F048','h',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('0','603','T2W','2','6400','0','80','0','50','0','300','3','','','','','','vent_sissepuhe1 10164287','h',3,1,1,'',''); -- 1016428700080051
INSERT INTO "aicochannels" VALUES('0','601','T2W','3','6400','0','80','0','50','0','300','3','','','','','','vent_sissepuhe2 10744587','h',3,1,1,'',''); -- 10744587000800AD
INSERT INTO "aicochannels" VALUES('0','605','T2W','4','6400','0','80','0','50','0','300','3','','','','','','vent_sissetomme 104B6387','h',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('0','600','T2W','5','6400','0','80','0','50','0','300','3','','','','','','vent_valjapuhe 10706587','h',3,1,1,'',''); -- 1070658700080089
INSERT INTO "aicochannels" VALUES('0','616','T2W','6','6400','0','80','0','50','-300','300','3','','','','','','outside_air@groundlevel koopia','h',3,1,1,'','');

INSERT INTO "aicochannels" VALUES('','','T3W','1','6400','0','100','0','100','100','300','1','','','210','','','temp ette elutuba virt','s',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('','','T3W','2','6400','0','80','0','50','150','300','3','','','200','','','temp tegelik elutuba andur puudu','s',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('','','T3W','3','6400','0','100','0','100','','','1','','','240','','','porand tagasi abiette virt','s',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('2','602','T3W','4','6400','0','80','0','50','0','300','3','','','','','','kitchen_floor_return1 28C4E248','h',3,0,1,'',''); -- 106A0A130008008C
INSERT INTO "aicochannels" VALUES('2','603','T3W','5','6400','0','80','0','50','0','300','3','','','','','','kitchen_floor_return2 28BA1E42','h',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('3','600','T3W','6','6400','0','80','0','50','0','300','3','','','','','','living_floor_return1 28C0D648','h',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('3','604','T3W','7','6400','0','80','0','50','0','300','3','','','','','','living_floor_return2 28C3C248','h',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('3','605','T3W','8','6400','0','80','0','50','0','300','3','','','','','','living_floor_return3 2847E348','h',3,0,1,'','');

-- INSERT INTO "aicochannels" VALUES('0','799','T4W','1','6400','0','100','0','100','','','','','','','','','heli ohutemp ette virt','h',3,1,1,'','');
-- INSERT INTO "aicochannels" VALUES('0','510','T4W','2','6400','0','80','0','50','','','','','','','','','heli ohk tegelik andur puuduub','h',3,1,1,'','');
-- INSERT INTO "aicochannels" VALUES('0','800','T4W','3','6400','0','100','0','100','','','','','','','','','heli porand tagasi abiette virt','h',3,1,1,'','');
-- INSERT INTO "aicochannels" VALUES('0','627','T4W','4','6400','0','80','0','50','0','30','3','','','','','','Heli_study_floor_return 2896F848','h',3,1,1,'','');

INSERT INTO "aicochannels" VALUES('','','T5W','1','6400','0','100','0','100','','','','','','180','','','talveaed ohk ette virt','s!',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('0','602','T5W','2','6400','0','80','0','50','0','300','3','','','','','','wintergarden_air 106A0A13','h',3,1,1,'',''); -- 
INSERT INTO "aicochannels" VALUES('','','T5W','3','6400','0','100','0','100','','','','','','190','','','talveaed tagasi abiette virt','s!',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('3','602','T5W','4','6400','0','80','0','50','0','300','3','','','','','','wintergarden_floor_return1 2816D848','h',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('3','603','T5W','5','6400','0','80','0','50','0','300','3','','','','','','wintergarden_floor_return2 2815FF48','h',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('','','T5W','6','6400','0','100','0','100','','','','','','210','','','talveaed kalorif abiette  virt','a!',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('0','609','T5W','7','6400','0','80','0','50','0','300','3','','','','','','wintergarden_hitemp_heating_return 28520742','h',3,1,1,'','');

INSERT INTO "aicochannels" VALUES('','','T6W','1','6400','0','100','0','100','','','','','','210','','','saun tagasi abiette virt','s!',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('3','601','T6W','2','6400','0','80','0','50','0','300','3','','','','','','sauna-shower_floor_return 285C0A49','h',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('3','606','T6W','3','6400','0','80','0','50','0','300','3','','','','','','wc&sauna_floor_return 281FC748','h',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('','','T6W','4','6400','0','100','0','100','','','','','','900','','','leiliruum ohk max virt','s!',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('','','T6W','5','6400','0','80','0','50','','','','','','900','','','leiliruum ohk tegelik andur puudub','s',3,1,1,'','');

INSERT INTO "aicochannels" VALUES('','','T7W','1','6400','0','100','0','100','','','','','','220','','','hall porand abiette virt','s!',3,1,0,'','');
INSERT INTO "aicochannels" VALUES('2','601','T7W','2','6400','0','80','0','50','0','300','3','','','','','','hall_floor_return1 28180949','h',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('2','600','T7W','3','6400','0','80','0','50','0','300','3','','','','','','hall_floor_return2 28C0E648','h',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('2','604','T7W','4','6400','0','80','0','50','0','300','3','','','','','','hallway_floor_return 2816D748','h',3,0,1,'','');

INSERT INTO "aicochannels" VALUES('','','T8W','1','6400','0','100','0','100','','','','','','210','','','MB ohk ette virt','s!',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('5','604','T8W','2','6400','0','80','0','50','0','300','3','','','','','','MB_air@wall 28E9FB48','h',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('','','T8W','3','6400','0','100','0','100','','','','','','270','','','MB porand tagasi abiette virt','s!',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('5','600','T8W','4','6400','0','80','0','50','0','300','3','','','','','','MBloop1_floor_return 28F09442','h',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('5','601','T8W','5','6400','0','80','0','50','0','300','3','','','','','','MBloop2_floor_return 28F07542','h',3,0,1,'','');

INSERT INTO "aicochannels" VALUES('','','T9W','1','6400','0','100','0','100','','','','','','230','','','MB vannituba ohk ette virt','s!',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('','','T9W','2','6400','0','80','0','50','','','','','','220','','','MB vannituba ohk andur puudu','s',3,1,1,'',''); -- FIXME!
INSERT INTO "aicochannels" VALUES('','','T9W','3','6400','0','100','0','100','','','','','','280','','','MB vanni por tagasi abiette virt','s!',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('5','605','T9W','4','6400','0','80','0','50','0','300','3','','','','','','MBbath_floor_return 28C33C42','h',3,0,1,'','');

INSERT INTO "aicochannels" VALUES('','','TAW','1','6400','0','100','0','100','','','','','','200','','','MB garde ohk ette virt','s!',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('5','602','TAW','2','6400','0','80','0','50','0','300','3','','','','','','MBgarde_air@wall 28069F9B0400009F','h',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('','','TAW','3','6400','0','100','0','100','','','','','','250','','','MB garde por tag abiette virt','s',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('5','603','TAW','4','6400','0','80','0','50','0','300','3','','','','','','MBgarde_floor_return 281EFD48','h',3,0,1,'','');



INSERT INTO "aicochannels" VALUES('0','618','TFW','1','6400','0','80','0','50','0','900','3','','','','','','fireplace_airconvection_out 28B7FE41','h',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('','','TFW','2','6400','0','80','0','50','0','900','','','','700','','','kamin ohkuvahemaksnivoo virt','s!',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('','','TFW','3','6400','0','80','0','50','0','900','','','','600','','','kamin sundventnivoo virt','s!',3,1,1,'','');

-- pwm
INSERT INTO "aicochannels" VALUES('','','PWW','1','17','0','50','0','50','50','950','','','','','','','gaasiseadme nupule pwm d%','s',3,0,1,'3','4');
INSERT INTO "aicochannels" VALUES('','','PWW','2','17','0','50','0','50','50','950','','','','','','','3t ventiilile pwm d%','s',3,0,1,'3','4');
INSERT INTO "aicochannels" VALUES('','','PWW','3','0','0','50','0','50','0','','','','','50','','','min pwm d%','s!',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('','','PWW','4','0','0','50','0','50','0','','','','','950','','','max pwm d%','s!',3,0,1,'','');

-- 
-- counters
INSERT INTO "aicochannels" VALUES('1','404','GVCV','1','1024','0','10','0','10','0','1000000000','1','','','','','','gas counter dL','h',3,0,2,'',''); -- dL, to be restored
INSERT INTO "aicochannels" VALUES('','','WVCV','1','0','0','10','0','10','','','1','','','','','','water counter l','s',3,0,2,'',''); -- L via mbus, no need to restore

-- pid debug
INSERT INTO "aicochannels" VALUES('','','KGPW','1','0','0','10','0','10','','','1','','','5','','','gaasiseadme KP G','s!',3,0,1,'',''); -- pid param p x 10
INSERT INTO "aicochannels" VALUES('','','KGPW','2','0','0','10','0','10','','','1','','','5','','','gaasiseadme KP H','s!',3,0,1,'',''); -- pid param p

INSERT INTO "aicochannels" VALUES('','','KGIW','1','0','0','10','0','10','','','1','','','5','','','gaasiseadme KI G','s!',3,0,1,'',''); -- pid param i x 1000
INSERT INTO "aicochannels" VALUES('','','KGIW','2','0','0','10','0','10','','','1','','','5','','','gaasiseadme KI H','s!',3,0,1,'',''); -- pid param i

INSERT INTO "aicochannels" VALUES('','','KGDW','1','0','0','10','0','10','','','1','','','0','','','gaasiseadme KD G','s!',3,0,1,'',''); -- pid param d x 1
INSERT INTO "aicochannels" VALUES('','','KGDW','2','0','0','10','0','10','','','1','','','0','','','gaasiseadme KD H','s!',3,0,1,'',''); -- pid param d

INSERT INTO "aicochannels" VALUES('','','LGGW','1','0','0','10','0','10','','','1','','','0','','','gaasiseadme error G','s',3,0,1,'',''); -- pid debug G
INSERT INTO "aicochannels" VALUES('','','LGGW','2','0','0','10','0','10','','','1','','','0','','','gaasiseadme P G','s',3,0,1,'',''); -- pid debug G
INSERT INTO "aicochannels" VALUES('','','LGGW','3','0','0','10','0','10','','','1','','','0','','','gaasiseadme I G','s',3,0,1,'',''); -- pid debug G
INSERT INTO "aicochannels" VALUES('','','LGGW','4','0','0','10','0','10','','','1','','','0','','','gaasiseadme D G','s',3,0,1,'',''); -- pid debug G

INSERT INTO "aicochannels" VALUES('','','LGHW','1','0','0','10','0','10','','','1','','','0','','','gaasiseadme error  H','s',3,0,1,'',''); -- pid debug H
INSERT INTO "aicochannels" VALUES('','','LGHW','2','0','0','10','0','10','','','1','','','0','','','gaasiseadme P  H','s',3,0,1,'',''); -- pid debug H
INSERT INTO "aicochannels" VALUES('','','LGHW','3','0','0','10','0','10','','','1','','','0','','','gaasiseadme I  H','s',3,0,1,'',''); -- pid debug H
INSERT INTO "aicochannels" VALUES('','','LGHW','4','0','0','10','0','10','','','1','','','0','','','gaasiseadme D  H','s',3,0,1,'',''); -- pid debug H

-- laiendus mba4 kyte 2k m1, m2, m3
INSERT INTO "aicochannels" VALUES('','','TBW','1','6400','0','100','0','100','','','','','','210','','','M1 ohk ette','s!',3,1,1,'','');  -- setpoint air
INSERT INTO "aicochannels" VALUES('4','604','TBW','2','6400','0','80','0','50','0','300','3','','','','','','M1_air@wall 28AB6B42','h',3,0,1,'',''); -- 604
INSERT INTO "aicochannels" VALUES('','','TBW','3','6400','0','100','0','100','','','','','','250','','','M1 por tag abiette virt','s',3,1,1,'',''); -- setpoint por
INSERT INTO "aicochannels" VALUES('4','600','TBW','4','6400','0','80','0','50','0','300','3','','','','','','M1_floor_return 28343042','h',3,0,1,'','');-- 600

INSERT INTO "aicochannels" VALUES('','','TKW','1','6400','0','100','0','100','','','','','','210','','','M2 ohk ette','s!',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('4','602','TKW','2','6400','0','80','0','50','0','300','3','','','','','','M2_air@wall 2886A01A','h',3,0,1,'',''); -- 602 
INSERT INTO "aicochannels" VALUES('','','TKW','3','6400','0','100','0','100','','','','','','250','','','M2 por tag ette','s',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('4','606','TKW','4','6400','0','80','0','50','0','300','3','','','','','','M2_floor_return 287F0E42','h',3,0,1,'',''); -- 606

INSERT INTO "aicochannels" VALUES('','','TDW','1','6400','0','100','0','100','','','','','','210','','','M3 ohk ette','s!',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('','','TDW','2','6400','0','80','0','50','0','300','3','','','200','','','M3_air@wall 28479A42','s',3,0,1,'',''); -- missing ??
INSERT INTO "aicochannels" VALUES('','','TDW','3','6400','0','100','0','100','','','','','','250','','','M3 por tag ette','s',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('4','601','TDW','4','6400','0','80','0','50','0','300','3','','','','','','M3_floor_return 28B2B241','h',3,0,1,'',''); -- 601

INSERT INTO "aicochannels" VALUES('','','TEW','1','6400','0','100','0','100','','','','','','250','','','gallery por tagasi ette','s',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('','','TEW','2','6400','0','80','0','50','0','300','','','','180','','','dush_actual','s',3,0,1,'',''); -- missing!
INSERT INTO "aicochannels" VALUES('','','TEW','3','6400','0','100','0','100','','','','','','255','','','dush 2k por tagasi ette ','s',3,1,1,'','');
INSERT INTO "aicochannels" VALUES('4','605','TEW','4','6400','0','80','0','50','0','300','3','','','','','','showerM12_floor_return 2843E141010000E1','h',3,0,1,'',''); -- 605

INSERT INTO "aicochannels" VALUES('','','TRW','1','0','0','100','0','100','','','','','','250','','','gallery ohk ette','s',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('','','TRW','2','6400','0','80','0','50','0','300','3','','','220','','','showerM12_actual','s',3,0,1,'',''); -- missing!
INSERT INTO "aicochannels" VALUES('','','TRW','3','0','0','100','0','100','','','','','','250','','','gallery por tagasi ette','s',3,0,1,'','');
INSERT INTO "aicochannels" VALUES('4','603','TRW','4','6400','0','80','0','50','0','300','3','','','','','','gallery_floor_return 2807F64101000065','h',3,0,1,'',''); -- 603

-- mba2 00000148E6C028 CF00000149091828 5300000148E2C428 44000001421EBA28 AF00000148D71628 D200000148F89628
INSERT INTO "aicochannels" VALUES('2','600','TH2W','1','6400','0','80','0','50','0','300','3','','','','','','temp debug','h',3,0,1,'',''); -- 28C0E648010000 
INSERT INTO "aicochannels" VALUES('2','601','TH2W','2','6400','0','80','0','50','0','300','3','','','','','','temp debug','h',3,0,1,'',''); -- 28180949010000CF 
INSERT INTO "aicochannels" VALUES('2','602','TH2W','3','6400','0','80','0','50','0','300','3','','','','','','temp debug','h',3,0,1,'',''); -- 28C4E24801000053 
INSERT INTO "aicochannels" VALUES('2','603','TH2W','4','6400','0','80','0','50','0','300','3','','','','','','temp debug','h',3,0,1,'',''); -- 28BA1E4201000044 
INSERT INTO "aicochannels" VALUES('2','604','TH2W','5','6400','0','80','0','50','0','300','3','','','','','','temp debug','h',3,0,1,'',''); -- 2816D748010000AF 
INSERT INTO "aicochannels" VALUES('2','605','TH2W','6','6400','0','80','0','50','0','300','3','','','','','','temp debug','h',3,0,1,'',''); -- 2896F848010000D2 

-- mba 3  1400000148D6C028 28000001490A5C28 C000000148D81628 3000000148FF1528 2E00000148C2C328 2D00000148E34728 4500000148C71F28
INSERT INTO "aicochannels" VALUES('3','600','TH3W','1','6400','0','80','0','50','0','300','3','','','','','','temp debug','h',3,0,1,'',''); -- 28C0D64801000014 
INSERT INTO "aicochannels" VALUES('3','601','TH3W','2','6400','0','80','0','50','0','300','3','','','','','','temp debug','h',3,0,1,'',''); -- 285C0A4901000028 
INSERT INTO "aicochannels" VALUES('3','602','TH3W','3','6400','0','80','0','50','0','300','3','','','','','','temp debug','h',3,0,1,'',''); -- 2816D848010000C0 
INSERT INTO "aicochannels" VALUES('3','603','TH3W','4','6400','0','80','0','50','0','300','3','','','','','','temp debug','h',3,0,1,'',''); -- 2815FF4801000030 
INSERT INTO "aicochannels" VALUES('3','604','TH3W','5','6400','0','80','0','50','0','300','3','','','','','','temp debug','h',3,0,1,'',''); -- 28C3C2480100002E 
INSERT INTO "aicochannels" VALUES('3','605','TH3W','6','6400','0','80','0','50','0','300','3','','','','','','temp debug','h',3,0,1,'',''); -- 2847E3480100002D 
INSERT INTO "aicochannels" VALUES('3','606','TH3W','7','6400','0','80','0','50','0','300','3','','','','','','temp debug','h',3,0,1,'',''); -- 281FC74801000045 

-- mba 4 2k2  E700000142303428 7F00000141B2B228 FD0000011AA08628 E100000141E14328 97000001426BAB28 6500000141F60728 4C000001420E7F28   mba4 it5888
INSERT INTO "aicochannels" VALUES('4','600','TH4W','1','6400','0','80','0','50','0','300','3','','','','','','M1_floor_return 28343042','h',3,0,1,'',''); -- 28343042010000E7 
INSERT INTO "aicochannels" VALUES('4','601','TH4W','2','6400','0','80','0','50','0','300','3','','','','','','M3 floor ret','h',3,0,1,'',''); -- 28B2B2410100007F 
INSERT INTO "aicochannels" VALUES('4','602','TH4W','3','6400','0','80','0','50','0','300','3','','','','','','M2_air@wall 2886A01A','h',3,0,1,'',''); -- 2886A01A010000FD 
INSERT INTO "aicochannels" VALUES('4','603','TH4W','4','6400','0','80','0','50','0','300','3','','','','','','showerM12_floor_return','h',3,0,1,'',''); -- 2843E141010000E1 
INSERT INTO "aicochannels" VALUES('4','604','TH4W','5','6400','0','80','0','50','0','300','3','','','','','','M1_air@wall 28AB6B42','h',3,0,1,'',''); -- 28AB6B4201000097 
INSERT INTO "aicochannels" VALUES('4','605','TH4W','6','6400','0','80','0','50','0','300','3','','','','','','gallery_floor_return','h',3,0,1,'',''); -- 2807F64101000065 
INSERT INTO "aicochannels" VALUES('4','606','TH4W','7','6400','0','80','0','50','0','300','3','','','','','','M2_floor_return 287F0E42','h',3,0,1,'',''); -- 287F0E420100004C 
INSERT INTO "aicochannels" VALUES('','','TH4W','8','6400','0','80','0','50','0','300','3','','','0','','','temp debug','h',3,0,1,'',''); -- M3 airwall puudu?? 
INSERT INTO "aicochannels" VALUES('','','TH4W','9','6400','0','80','0','50','0','300','3','','','0','','','temp debug','h',3,0,1,'',''); -- shower air puudu?

-- mba5  2k pesuruumis ylemine kilp dc4888 - ilma vannitoa andurita esialgu!
-- 880000014294F028 9F0000014275F028 9F0000049B9F0628 4B00000148FD1E28 2000000148FBE928 31000001423CC328
INSERT INTO "aicochannels" VALUES('5','600','TH5W','1','6400','0','80','0','50','100','400','3','','','','','','temp debug 2k1','h',3,0,1,'',''); -- 28F0944201000088
INSERT INTO "aicochannels" VALUES('5','601','TH5W','2','6400','0','80','0','50','100','400','3','','','','','','temp debug 2k1','h',3,0,1,'',''); -- 28F075420100009F
INSERT INTO "aicochannels" VALUES('5','602','TH5W','3','6400','0','80','0','50','100','400','3','','','','','','temp debug 2k1','h',3,0,1,'',''); -- 28069F9B0400009F
INSERT INTO "aicochannels" VALUES('5','603','TH5W','4','6400','0','80','0','50','100','400','3','','','','','','temp debug 2k1','h',3,0,1,'',''); -- 281EFD480100004B
INSERT INTO "aicochannels" VALUES('5','604','TH5W','5','6400','0','80','0','50','100','400','3','','','','','','temp debug 2k1','h',3,0,1,'',''); -- 28E9FB4801000020
INSERT INTO "aicochannels" VALUES('5','605','TH5W','6','6400','0','80','0','50','100','400','3','','','','','','temp debug 2k1','h',3,0,1,'',''); -- 28C33C4201000031
INSERT INTO "aicochannels" VALUES('','','TH5W','7','6400','0','80','0','50','100','400','3','','','100','','','temp debug 2k1','s',3,0,1,'',''); -- 


INSERT INTO "aicochannels" VALUES('11','1','V1VV','1','0','0','10','0','10','100','2000','1','','','','','','voc test bio2000 voc','h',3,2,1,'',''); -- 10.0.0.4 kaudu
INSERT INTO "aicochannels" VALUES('11','2','V1TV','1','0','0','10','0','10','100','300','1','','','','','','voc test bio2000 temp','h',3,2,1,'',''); -- 10.0.0.4 kaudu


CREATE UNIQUE INDEX ai_regmember on 'aicochannels'(val_reg,member); -- iga liiget tohib olla vaid yks
COMMIT;
