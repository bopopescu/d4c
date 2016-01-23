--analoogsuuruste konf lugemiseks modbusTCP kaudu. 
-- x1 ja x2 on sisendi diapasoon, y1 y2 valjundi oma (lineaarteisendus 2 punkti alusel)
-- value ja statud on viimased, arvatavasti hetkel kehtivad vaartused (kontrolli igaks juhuks ka ts vanust)
-- mitme muutujaga teenuste iga liikme jaoks on yks rida, liikme jark tahistab member. 
-- outlo ja outhi on lubatud piirid, millest yle tekib warning voi alarm vastavalt cfg sisule
-- mis asi oli block?? mis asi on avg, keskmistamise tugevus? jah, mitu korda vana vaartust tuleb votta rohkem kui uut. tekitab rc / eksponendi silumiseks.

-- # KONFIBAIDI BITTIDE SELGITUS
-- # siin ei ole tegemist ind ja grp teenuste eristamisega, ind teenused konfitakse samadel alustel eraldi!
-- # konfime poolbaidi vaartustega, siis hex kujul hea vaadata. vanem hi, noorem lo!
-- # x0 - alla outlo ikka ok, 0x - yle outhi ikka ok 
-- # x1 - alla outlo warning, 1x - yle outhi warning
-- # x2 - alla outlo critical, 2x - yle outhi critical
-- # x3 - alla outlo ei saada, 3x - yle outhi ei saada
-- # lisaks bit 2 lisamine asendab vaartuse nulliga / kas on vaja?
-- # lisaks bit 4 teeb veel midagi / reserv

-- x1 x2 y1 y2 vaartsed vaja ka etteandesuurustele, kus konversiooni ei toimu! pane kasvoi '0','100','0','100' !

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE aichannels(mba,regadd,val_reg,member,cfg,x1,x2,y1,y2,outlo,outhi,avg,block,raw,value,status,ts,desc,comment,type integer); 
-- grp is flagging channel usage - 0 for voltage, 1 for temperaturte, 2 for humidity

INSERT INTO "aichannels" VALUES('0','628','T0W','1','17','0','80','0','50','0','30','3','','','','','','cold_water_inlet','286EE441',3);
INSERT INTO "aichannels" VALUES('0','617','T0W','2','17','0','80','0','50','0','30','3','','','','','','warm_water_to_dist','28A29642',3);
INSERT INTO "aichannels" VALUES('0','630','T0W','3','17','0','80','0','50','0','30','3','','','','','','warm_water_return1','28A1DD41',3);
INSERT INTO "aichannels" VALUES('0','642','T0W','4','17','0','80','0','50','0','30','3','','','','','','warm_water_return2','28A75942',3);
INSERT INTO "aichannels" VALUES('0','633','T0W','5','17','0','80','0','50','-30','40','3','','','','','','roof?','28B5EB480100000F',3);
INSERT INTO "aichannels" VALUES('0','612','T0W','6','17','0','80','0','50','0','30','3','','','','','','tech_cellar_air','28C89342',3);
INSERT INTO "aichannels" VALUES('0','634','T0W','7','17','0','80','0','50','-30','30','3','','','','','','outside_air@groundlevel','28F57B1A',3);

INSERT INTO "aichannels" VALUES('0','634','T1W','1','17','0','80','0','50','-30','30','3','','','','','','outside_air@groundlevel','koopia',3);
INSERT INTO "aichannels" VALUES('0','805','T1W','2','17','0','100','0','100','10','90','1','','','','','','hot ette, paranda','virt',3);
INSERT INTO "aichannels" VALUES('0','604','T1W','3','17','0','80','0','50','0','30','3','','','','','','gas_heater_outputwater','10392A13',3);
INSERT INTO "aichannels" VALUES('0','620','T1W','4','17','0','80','0','50','0','30','3','','','','','','gas_heater_return','282A8842',3);
INSERT INTO "aichannels" VALUES('0','801','T1W','5','17','0','80','0','50','0','30','1','','','','','','madal_ette','paranda',3);
INSERT INTO "aichannels" VALUES('0','607','T1W','6','17','0','80','0','50','0','30','3','','','','','','floor_heatingwater_onflow','10DF2D13',3);
INSERT INTO "aichannels" VALUES('0','621','T1W','7','17','0','80','0','50','0','30','3','','','','','','floor_heatingwater_return','28AA7842',3);

INSERT INTO "aichannels" VALUES('0','624','T2W','1','17','0','80','0','50','0','30','3','','','','','','vent_valjatomme','2846F048',3);
INSERT INTO "aichannels" VALUES('0','603','T2W','2','17','0','80','0','50','0','30','3','','','','','','vent_sissepuhe1','10164287',3);
INSERT INTO "aichannels" VALUES('0','601','T2W','3','17','0','80','0','50','0','30','3','','','','','','vent_sissepuhe2','10744587',3);
INSERT INTO "aichannels" VALUES('0','605','T2W','4','17','0','80','0','50','0','30','3','','','','','','vent_sissetomme','104B6387',3);
INSERT INTO "aichannels" VALUES('0','600','T2W','5','17','0','80','0','50','0','30','3','','','','','','vent_valjapuhe','10706587',3);
INSERT INTO "aichannels" VALUES('0','634','T2W','6','17','0','80','0','50','-30','30','3','','','','','','outside_air@groundlevel','koopia',3);

INSERT INTO "aichannels" VALUES('0','799','T3W','1','17','0','100','0','100','10','30','1','','','','','','temp ette elutuba','virt',3);
INSERT INTO "aichannels" VALUES('0','507','T3W','2','17','0','80','0','50','15','30','3','','','','','','temp tegelik elutuba','andur puudu',3);
INSERT INTO "aichannels" VALUES('0','800','T3W','3','17','0','100','0','100','','','1','','','','','','porand tagasi abiette','virt',3);
INSERT INTO "aichannels" VALUES('0','614','T3W','4','17','0','80','0','50','0','30','3','','','','','','kitchen_floor_return1','28C4E248',3);
INSERT INTO "aichannels" VALUES('0','622','T3W','5','17','0','80','0','50','0','30','3','','','','','','kitchen_floor_return2','28BA1E42',3);
INSERT INTO "aichannels" VALUES('0','609','T3W','6','17','0','80','0','50','0','30','3','','','','','','living_floor_return1','28C0D648',3);
INSERT INTO "aichannels" VALUES('0','637','T3W','7','17','0','80','0','50','0','30','3','','','','','','living_floor_return2','28C3C248',3);
INSERT INTO "aichannels" VALUES('0','641','T3W','8','17','0','80','0','50','0','30','3','','','','','','living_floor_return3','2847E348',3);

INSERT INTO "aichannels" VALUES('0','799','T4W','1','17','0','100','0','100','','','','','','','','','heli ohutemp ette','virt',3);
INSERT INTO "aichannels" VALUES('0','510','T4W','2','17','0','80','0','50','','','','','','','','','heli ohk tegelik','andur puuduub',3);
INSERT INTO "aichannels" VALUES('0','800','T4W','3','17','0','100','0','100','','','','','','','','','heli porand tagasi abiette','virt',3);
INSERT INTO "aichannels" VALUES('0','627','T4W','4','17','0','80','0','50','0','30','3','','','','','','Heli_study_floor_return','2896F848',3);

INSERT INTO "aichannels" VALUES('0','512','T5W','1','17','0','100','0','100','','','','','','','','','talveaed ohk ette','virt',3);
INSERT INTO "aichannels" VALUES('0','602','T5W','2','17','0','80','0','50','0','30','3','','','','','','wintergarden_air','106A0A13',3);
INSERT INTO "aichannels" VALUES('0','513','T5W','3','17','0','100','0','100','','','','','','','','','talveaed tagasi abiette','virt',3);
INSERT INTO "aichannels" VALUES('0','625','T5W','4','17','0','80','0','50','0','30','3','','','','','','wintergarden_floor_return1','2816D848',3);
INSERT INTO "aichannels" VALUES('0','632','T5W','5','17','0','80','0','50','0','30','3','','','','','','wintergarden_floor_return2','2815FF48',3);
INSERT INTO "aichannels" VALUES('0','514','T5W','6','17','0','100','0','100','','','','','','','','','talveaed kalorif abiette ','virt',3);
INSERT INTO "aichannels" VALUES('0','618','T5W','7','17','0','80','0','50','0','30','3','','','','','','wintergarden_hitemp_heating_return','28520742',3);

INSERT INTO "aichannels" VALUES('0','800','T6W','1','17','0','100','0','100','','','','','','','','','saun tagasi abiette','virt',3);
INSERT INTO "aichannels" VALUES('0','616','T6W','2','17','0','80','0','50','0','30','3','','','','','','sauna-shower_floor_return','285C0A49',3);
INSERT INTO "aichannels" VALUES('0','644','T6W','3','17','0','80','0','50','0','30','3','','','','','','wc&sauna_floor_return','281FC748',3);
INSERT INTO "aichannels" VALUES('0','517','T6W','4','17','0','100','0','100','','','','','','','','','leiliruum ohk max','virt',3);
INSERT INTO "aichannels" VALUES('0','518','T6W','5','17','0','80','0','50','','','','','','','','','leiliruum ohk tegelik','andur puudub',3);

INSERT INTO "aichannels" VALUES('0','800','T7W','1','17','0','100','0','100','','','','','','','','','hall porand abiette','virt',3);
INSERT INTO "aichannels" VALUES('0','613','T7W','2','17','0','80','0','50','0','30','3','','','','','','hall_floor_return1','28180949',3);
INSERT INTO "aichannels" VALUES('0','608','T7W','3','17','0','80','0','50','0','30','3','','','','','','hall_floor_return2','28C0E648',3);
INSERT INTO "aichannels" VALUES('0','626','T7W','4','17','0','80','0','50','0','30','3','','','','','','hallway_floor_return','2816D748',3);

INSERT INTO "aichannels" VALUES('0','799','T8W','1','17','0','100','0','100','','','','','','','','','MB ohk ette','virt',3);
INSERT INTO "aichannels" VALUES('0','631','T8W','2','17','0','80','0','50','0','30','3','','','','','','MB_air@wall','28E9FB48',3);
INSERT INTO "aichannels" VALUES('0','800','T8W','3','17','0','100','0','100','','','','','','','','','MB porand tagasi abiette','virt',3);
INSERT INTO "aichannels" VALUES('0','610','T8W','4','17','0','80','0','50','0','30','3','','','','','','MBloop1_floor_return','28F09442',3);
INSERT INTO "aichannels" VALUES('0','611','T8W','5','17','0','80','0','50','0','30','3','','','','','','MBlopp2_floor_return','28F07542',3);

INSERT INTO "aichannels" VALUES('0','799','T9W','1','17','0','100','0','100','','','','','','','','','MB vannituba ohk ette','virt',3);
INSERT INTO "aichannels" VALUES('0','523','T9W','2','17','0','80','0','50','','','','','','','','','MB vannituba ohk','andur puudu',3);
INSERT INTO "aichannels" VALUES('0','800','T9W','3','17','0','100','0','100','','','','','','','','','MB vanni por tagasi abiette','virt',3);
INSERT INTO "aichannels" VALUES('0','636','T9W','4','17','0','80','0','50','0','30','3','','','','','','MBbath_floor_return','28C33C42',3);

INSERT INTO "aichannels" VALUES('0','799','TAW','1','17','0','100','0','100','','','','','','','','','MB garde ohk ette','virt',3);
INSERT INTO "aichannels" VALUES('0','606','TAW','2','17','0','80','0','50','0','30','3','','','','','','MBgarde_air@wall','10CF3987',3);
INSERT INTO "aichannels" VALUES('0','800','TAW','3','17','0','100','0','100','','','','','','','','','MB garde por tag abiette','virt',3);
INSERT INTO "aichannels" VALUES('0','629','TAW','4','17','0','80','0','50','0','30','3','','','','','','MBgarde_floor_return','281EFD48',3);

INSERT INTO "aichannels" VALUES('0','799','TBW','1','17','0','100','0','100','','','','','','','','','M1 ohk ette','virt',3);
INSERT INTO "aichannels" VALUES('0','638','TBW','2','17','0','80','0','50','0','30','3','','','','','','M1_air@wall','28AB6B42',3);
INSERT INTO "aichannels" VALUES('0','800','TBW','3','17','0','100','0','100','','','','','','','','','M1 por tag abiette','virt',3);
INSERT INTO "aichannels" VALUES('0','615','TBW','4','17','0','80','0','50','0','30','3','','','','','','M1_floor_return','28343042',3);

INSERT INTO "aichannels" VALUES('0','799','TCW','1','17','0','100','0','100','','','','','','','','','M2 ohk ette','virt',3);
INSERT INTO "aichannels" VALUES('0','623','TCW','2','17','0','80','0','50','0','30','3','','','','','','M2_air@wall','2886A01A',3);
INSERT INTO "aichannels" VALUES('0','800','TCW','3','17','0','100','0','100','','','','','','','','','M2 por tag abiette','virt',3);
INSERT INTO "aichannels" VALUES('0','645','TCW','4','17','0','80','0','50','0','30','3','','','','','','M2_floor_return','287F0E42',3);

INSERT INTO "aichannels" VALUES('0','799','TDW','1','17','0','100','0','100','','','','','','','','','M3 ohk ette','virt',3);
INSERT INTO "aichannels" VALUES('0','640','TDW','2','17','0','80','0','50','0','30','3','','','','','','M3_air@wall','28479A42',3);
INSERT INTO "aichannels" VALUES('0','800','TDW','3','17','0','100','0','100','','','','','','','','','M3 por tag abiette','virt',3);
INSERT INTO "aichannels" VALUES('0','619','TDW','4','17','0','80','0','50','0','30','3','','','','','','M3_floor_return','28B2B241',3);

INSERT INTO "aichannels" VALUES('0','800','TEW','1','17','0','100','0','100','','','','','','','','','gallery por tagasi abi ette','virt',3);
INSERT INTO "aichannels" VALUES('0','639','TEW','2','17','0','80','0','50','0','30','','','','','','','gallery_floor_return','2807F641',3);
INSERT INTO "aichannels" VALUES('0','800','TEW','3','17','0','100','0','100','','','','','','','','','dush 2k por tagasi abiette','virt',3);
INSERT INTO "aichannels" VALUES('0','635','TEW','4','17','0','80','0','50','0','30','3','','','','','','showerM12_floor_return','2843E141010000E1',3);

INSERT INTO "aichannels" VALUES('0','643','TFW','1','17','0','80','0','50','0','90','3','','','','','','fireplace_airconvection_out','28B7FE41',3);
INSERT INTO "aichannels" VALUES('0','535','TFW','2','17','0','80','0','50','0','90','','','','','','','kamin ohkuvahemaksnivoo','virt',3);
INSERT INTO "aichannels" VALUES('0','536','TFW','3','17','0','80','0','50','0','90','','','','','','','kamin sundventnivoo','virt',3);

-- abigraafikud 15.10.2013 
INSERT INTO "aichannels" VALUES('0','800','TLW','1','17','0','80','0','80','0','90','3','','','','','','etteanne ohk','',3); -- lin teisendust siin ei tee
INSERT INTO "aichannels" VALUES('0','801','TLW','2','17','0','80','0','80','0','90','3','','','','','','etteanne por_vesi','',3);
INSERT INTO "aichannels" VALUES('0','806','TLW','3','17','0','80','0','80','0','90','3','','','','','','etteannet_hot','',3);
INSERT INTO "aichannels" VALUES('0','624','TLW','4','17','0','80','0','50','0','90','3','','','','','','vent valjatomme e tegelik keskmine toatemp','',3);
INSERT INTO "aichannels" VALUES('0','621','TLW','5','17','0','80','0','50','0','90','3','','','','','','porandast tagastuv vesi','',3);
INSERT INTO "aichannels" VALUES('0','620','TLW','6','17','0','80','0','50','0','90','3','','','','','','gaasikyttest valjuv vesi','',3);

INSERT INTO "aichannels" VALUES('0','901','PWW','1','17','0','80','0','80','0','90','3','','','','','','termoajam kyttevesi','',3); -- loopide PWM
INSERT INTO "aichannels" VALUES('0','905','PWW','2','17','0','80','0','80','0','90','3','','','','','','termoajam ohkkyte','',3); -- loopide PWM
INSERT INTO "aichannels" VALUES('0','906','PWW','3','17','0','80','0','80','0','90','3','','100','','','','termoajam hot_max','',3); -- loopide PWM
INSERT INTO "aichannels" VALUES('0','999','PWW','4','17','0','80','0','80','0','90','3','','0','','','','pwm_min','',3); -- loopide PWM - ei funka?? see soft ei toeta jooni
INSERT INTO "aichannels" VALUES('0','999','PWW','5','17','0','80','0','80','0','90','3','','100','','','','pwm_max','',3); -- loopide PWM



CREATE UNIQUE INDEX ai_regmember on 'aichannels'(val_reg,member); -- iga liiget tohib olla vaid yks
COMMIT;
