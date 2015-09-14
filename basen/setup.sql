-- LINUX version, longer watchdog delay. NEW PIC! starmani io 3.31, sisse progetud 3.28
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE setup(register,value,ts,desc,comment,type integer); -- type vt chantypes. maarab kas loetav holding voi input registrist, bitikaaluga 8
-- desc jaab UI kaudu naha,  comment on enda jaoks. ts on muutmise aeg s, MIKS mitte mba, reg value? setup muutuja reg:value...
-- count oleks vaja lisada et korraga sygavuti saaks lugeda!

-- R... values will only be reported during channelconfiguration()
INSERT INTO 'setup' VALUES('R9.256','','','dev type','',0); -- read only
INSERT INTO 'setup' VALUES('R9.257','','','fw version','',0); -- start with this, W1.270,271,275 depend on this !
INSERT INTO 'setup' VALUES('R9.258','','','ser nr partii','',0); -- start with this, W1.270,271,275 depend on this !
INSERT INTO 'setup' VALUES('R9.259','','','ser nr plaat','',0); -- start with this, W1.270,271,275 depend on this !

-- INSERT INTO 'setup' VALUES('R2.53666','','','fw version','',0); -- vent1 serial MSB
-- INSERT INTO 'setup' VALUES('R3.53666','','','fw version','',0); -- vent2 serial MSB

INSERT INTO 'setup' VALUES('S400','http://www.itvilla.ee','','supporthost','for pull, push cmd',0);
INSERT INTO 'setup' VALUES('S401','upload.php','','requests.post','for push cmd',0);
INSERT INTO 'setup' VALUES('S402','Basic cHlhcHA6QkVMYXVwb2E=','','authorization header','for push cmd',0);
INSERT INTO 'setup' VALUES('S403','support/pyapp/$mac','','upload/dnload directory','for pull and push cmd',0); --  $mac will be replaced by wlan mac


CREATE UNIQUE INDEX reg_setup on 'setup'(register);
COMMIT;
