-- android seadme setup tabel, baasi modbus_channels. systeem sama nagu barioneti muutujatega!
-- kindlasti vaja anda mon serverid, max teavitusintervall, obj nimetus jne
-- esialgu umon sarnaselt voi? 

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE asetup(register,value,ts,desc,comment); -- desc jaab UI kaudu naha,  comment on enda jaoks. ts on muutmise aeg s

INSERT INTO 'asetup' VALUES('AVV','acomm','','rakendustarkvara versioon','app soft versioon'); -- nagu bn

INSERT INTO 'asetup' VALUES('S100','','','','mida kaivitatakse rakendusena'); -- mingi default peaks ka olema
INSERT INTO 'asetup' VALUES('B0','10','','ip aadress B0','ip aadress B0'); -- nagu bn
INSERT INTO 'asetup' VALUES('B1','0','','ip aadress B1','ip aadress B1'); -- nagu bn
INSERT INTO 'asetup' VALUES('B2','0','','ip aadress B2','ip aadress B2'); -- nagu bn
INSERT INTO 'asetup' VALUES('B3','13','','ip aadress B3','ip aadress B3'); -- nagu bn

CREATE UNIQUE INDEX stp_register on 'asetup'(register);
COMMIT;
