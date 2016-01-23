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

-- mba1 
INSERT INTO "aicochannels" VALUES('1','2','AI1W','1','26','0','100','0','100','3000','4000','1','','','3800','','','kytte PIR thre raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('1','3','AI1W','2','26','0','100','0','100','3000','4000','1','','','3800','','','esiku PIR thre raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('1','4','AI1W','3','26','0','100','0','100','3000','4000','1','','','3800','','','halli PIR thre raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('1','5','AI1W','4','26','0','100','0','100','3000','4000','1','','','3800','','','saun_dush thre raw 3440','h',3,0,1,'',''); -- ai 
INSERT INTO "aicochannels" VALUES('1','6','AI1W','5','26','0','100','0','100','3000','4000','1','','','4500','','','','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('1','7','AI1W','6','26','0','100','0','100','3000','4000','1','','','4500','','','','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('1','8','AI1W','7','26','0','100','0','100','3000','4000','1','','','4500','','','','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('1','9','AI1W','8','26','0','100','0','100','3000','4000','1','','','4500','','','','h',3,0,1,'',''); -- ai

-- mba 2
-- INSERT INTO "aicochannels" VALUES('2','2','AI2W','1','26','0','100','0','100','3000','4000','1','','','','','','','r',3,0,1,'',''); -- max voimalik 4095
-- INSERT INTO "aicochannels" VALUES('2','3','AI2W','2','26','0','100','0','100','3000','4000','1','','','','','','','r',3,0,1,'',''); -- 
-- INSERT INTO "aicochannels" VALUES('2','4','AI2W','3','26','0','100','0','100','3000','4000','1','','','','','','','r',3,0,1,'',''); -- 
-- INSERT INTO "aicochannels" VALUES('2','5','AI2W','4','26','0','100','0','100','3000','4000','1','','','','','','','r',3,0,1,'',''); -- 
-- INSERT INTO "aicochannels" VALUES('2','6','AI2W','5','26','0','100','0','100','3000','4000','1','','','160','','','','r',3,0,1,'',''); -- 
-- INSERT INTO "aicochannels" VALUES('2','7','AI2W','6','26','0','100','0','100','3000','4000','1','','','160','','','','r',3,0,1,'',''); -- 
-- INSERT INTO "aicochannels" VALUES('2','8','AI2W','7','26','0','100','0','100','3000','4000','1','','','160','','','','r',3,0,1,'',''); -- 
-- INSERT INTO "aicochannels" VALUES('','','AI2W','8','26','0','100','0','100','0','4595','1','','','0','','','230V OK','r',3,0,1,'',''); -- di

-- mba 21 2k pesuruum
INSERT INTO "aicochannels" VALUES('21','2','AI21W','1','26','0','100','0','100','3000','4000','1','','','3800','','','vannitoa PIR thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('21','3','AI21W','2','26','0','100','0','100','3000','4000','1','','','3800','','','MB PIR thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('21','4','AI21W','3','26','0','100','0','100','3000','4000','1','','','3800','','','rodu uks thresh raw 3440','h',3,0,1,'',''); -- ai / uks?
INSERT INTO "aicochannels" VALUES('21','5','AI21W','4','26','0','100','0','100','3000','4000','1','','','3800','','','garde PIR thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('21','6','AI21W','5','26','0','100','0','100','3000','4000','1','','','3800','','',' PIR thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('21','7','AI21W','6','26','0','100','0','100','3000','4000','1','','','3800','','',' PIR thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('21','8','AI21W','7','26','0','100','0','100','3000','4000','1','','','3800','','',' PIR thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('21','9','AI21W','8','26','0','100','0','100','3000','4000','1','','','3800','','','suitsuandur shahtis','h',3,0,1,'',''); -- suits, 13v /4095 ok, 1V alarm 


-- mba31 kilp 3 kook/elutuba
INSERT INTO "aicochannels" VALUES('31','2','AI31W','1','26','0','100','0','100','3000','4000','1','','','3800','','','soogilaua PIR thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('31','3','AI31W','2','26','0','100','0','100','3000','4000','1','','','3800','','','oueakna PIR thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('31','4','AI31W','3','26','0','100','0','100','3000','4000','1','','','3800','','',' PIR thresh raw 3440','h',3,0,1,'',''); -- ai / uks?
INSERT INTO "aicochannels" VALUES('31','5','AI31W','4','26','0','100','0','100','3000','4000','1','','','3800','','',' PIR thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('31','6','AI31W','5','26','0','100','0','100','3000','4000','1','','','3800','','',' PIR thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('31','7','AI31W','6','26','0','100','0','100','3000','4000','1','','','3800','','',' PIR thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('31','8','AI31W','7','26','0','100','0','100','3000','4000','1','','','3800','','',' PIR thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('31','9','AI31W','8','26','0','100','0','100','3000','4000','1','','','3800','','',' PIR thresh raw 3440','h',3,0,1,'',''); -- ai

-- mba41 2k kor
INSERT INTO "aicochannels" VALUES('41','2','AI41W','1','26','0','100','0','100','3000','4000','1','','','3800','','','kor_PIR_ots thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('41','3','AI41W','2','26','0','100','0','100','3000','4000','1','','','3800','','','M2 aken','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('41','4','AI41W','3','26','0','100','0','100','3000','4000','1','','','3800','','','M3_PIR thresh raw 3440','h',3,0,1,'',''); -- ai / uks?
INSERT INTO "aicochannels" VALUES('41','5','AI41W','4','26','0','100','0','100','3000','4000','1','','','3800','','','M3_aken thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('41','6','AI41W','5','26','0','100','0','100','3000','4000','1','','','3800','','','trepi_PIR thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('41','7','AI41W','6','26','0','100','0','100','3000','4000','1','','','3800','','','M1_aken','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('41','8','AI41W','7','26','0','100','0','100','3000','4000','1','','','3800','','','M2_uks thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('41','9','AI41W','8','26','0','100','0','100','3000','4000','1','','','3800','','','M2_PIR thresh raw 3440','h',3,0,1,'',''); -- ai

INSERT INTO "aicochannels" VALUES('42','2','AI42W','1','26','0','100','0','100','3000','4000','1','','','3800','','','M1_PIR thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('42','3','AI42W','2','26','0','100','0','100','3000','4000','1','','','3800','','','dush_uks thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('42','4','AI42W','3','26','0','100','0','100','3000','4000','1','','','3800','','','dush_PIR thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('42','5','AI42W','4','26','0','100','0','100','3000','4000','1','','','3800','','','2k_suits thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('42','6','AI42W','5','26','0','100','0','100','3000','4000','1','','','3800','','','M1_uks thresh raw 3440','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('42','7','AI42W','6','26','0','100','0','100','3000','4000','1','','','3800','','','','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('42','8','AI42W','7','26','0','100','0','100','3000','4000','1','','','3800','','','','h',3,0,1,'',''); -- ai
INSERT INTO "aicochannels" VALUES('42','9','AI42W','8','26','0','100','0','100','3000','4000','1','','','3800','','','','h',3,0,1,'',''); -- ai

INSERT INTO "aicochannels" VALUES('42','414','E4CV','1','1024','0','100','0','100','','','','','','','','','sp Wh kilp 4','h',3,0,2,'',''); -- en mootja sp k4
INSERT INTO "aicochannels" VALUES('42','414','P4W','1','448','0','100','0','100','0','3000','','','','','','','sp W kilp 4','h',3,0,2,'','2'); -- voimsus W, tarbides w
INSERT INTO "aicochannels" VALUES('','','P4W','2','','0','100','0','100','','','','','','3000','','','sp Wh kilp 4','s!',3,0,2,'',''); -- max voimsus

-- temp andurid mba 31 ['28583809070000C2', '281B45090700006F', '28B7FE410100005C']
INSERT INTO "aicochannels" VALUES('32','600','T3KW','1','6400','0','80','0','50','50','300','3','','','','','','kummi all','h',3,0,1,'',''); -- kubu all
INSERT INTO "aicochannels" VALUES('32','601','T3KW','2','6400','0','80','0','50','50','300','3','','','','','','kapi peal','h',3,0,1,'',''); -- kapi peal
INSERT INTO "aicochannels" VALUES('32','601','T3KW','3','0','0','80','30','80','80','330','1','','','','','','nihkes','h',3,0,1,'',''); -- kapi peal nihkes yles 3 deg

INSERT INTO "aicochannels" VALUES('','','V3W','1','20','0','50','0','100','0','100','1','','','0','','','pliit vent pwm act','r',3,0,1,'',''); -- pwm 0..1000
INSERT INTO "aicochannels" VALUES('','','V3W','2','20','0','50','0','100','0','1000','1','','','100','','','pliit vent pwm hi','s!',3,0,1,'',''); -- warn kui sees

INSERT INTO "aicochannels" VALUES('32','602','T3HW','1','6400','0','80','0','50','50','300','3','','','','','','kamina kohal','h',3,0,1,'',''); -- kamin lae all
INSERT INTO "aicochannels" VALUES('','','T3HW','2','0','0','80','0','50','50','300','3','','','400','','','klapi lylitusnivoo','s!',3,0,1,'',''); -- setpoint klapi pid/pwm kaudu


CREATE UNIQUE INDEX ai_regmember on 'aicochannels'(val_reg,member); -- iga liiget tohib olla vaid yks
COMMIT;
