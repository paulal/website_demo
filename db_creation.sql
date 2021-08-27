/* run this script with ".read db_creation.sql" when you are already connected to Sqlite and have the db open */
/* or, you can also do "cat db_creation.sql | sqlite3 fineli.db" in a terminal without connecting to Sqlite first. */

/* commands for creating the tables for fineli db */

CREATE TABLE food (
    FOODID INTEGER NOT NULL PRIMARY KEY,
    FOODNAME TEXT NOT NULL,
    FOODTYPE TEXT,
    PROCESS TEXT,
    EDPORT NUMBER,
    IGCLASS TEXT,
    IGCLASSP TEXT,
    FUCLASS TEXT,
    FUCLASSP TEXT,
    FOREIGN KEY (FOODTYPE)
    REFERENCES foodtype_FI (THSCODE)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    FOREIGN KEY (PROCESS)
    REFERENCES process_FI (THSCODE)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    FOREIGN KEY (IGCLASS)
    REFERENCES igclass_FI (THSCODE)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    FOREIGN KEY (FUCLASS)
    REFERENCES fuclass_FI (THSCODE)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE foodname_FI (
    FOODID INTEGER NOT NULL,
    FOODNAME TEXT NOT NULL,
    LANG TEXT,
    FOREIGN KEY (FOODID)
    REFERENCES food (FOODID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE foodname_TX (
    FOODID INTEGER NOT NULL,
    FOODNAME TEXT NOT NULL,
    LANG TEXT,
    FOREIGN KEY (FOODID)
    REFERENCES food (FOODID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE component (
    EUFDNAME TEXT NOT NULL,
    COMPUNIT TEXT,
    CMPCLASS TEXT,
    CMPCLASSP TEXT,
    FOREIGN KEY (EUFDNAME)
    REFERENCES eufdname_FI (THSCODE)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (COMPUNIT)
    REFERENCES compunit_FI (THSCODE)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (CMPCLASS)
    REFERENCES cmpclass_FI (THSCODE)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE component_value (
    FOODID INTEGER NOT NULL,
    EUFDNAME TEXT NOT NULL,
    BESTLOC NUMBER,
    ACQTYPE TEXT DEFAULT "X",
    METHTYPE TEXT DEFAULT "X",
    METHIND TEXT,
    FOREIGN KEY (FOODID)
    REFERENCES food (FOODID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (EUFDNAME)
    REFERENCES component (EUFDNAME)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (ACQTYPE)
    REFERENCES acqtype_FI (THSCODE)
        ON UPDATE CASCADE
        ON DELETE SET DEFAULT,
    FOREIGN KEY (METHTYPE)
    REFERENCES methtype_FI (THSCODE)
        ON UPDATE CASCADE
        ON DELETE SET DEFAULT,
    FOREIGN KEY (METHIND)
    REFERENCES methind_FI (THSCODE)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE contribfood (
    FOODID INTEGER NOT NULL,
    CONFDID INTEGER NOT NULL,
    AMOUNT NUMBER,
    FOODUNIT TEXT,
    MASS NUMBER,
    EVREMAIN NUMBER,
    RECYEAR TEXT,
    FOREIGN KEY (FOODID)
    REFERENCES food (FOODID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (CONFDID)
    REFERENCES food (FOODID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (FOODUNIT)
    REFERENCES foodunit_FI (THSCODE)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE foodaddunit (
    FOODID INTEGER NOT NULL,
    FOODUNIT TEXT,
    MASS NUMBER,
    FOREIGN KEY (FOODID)
    REFERENCES food (FOODID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (FOODUNIT)
    REFERENCES foodunit_FI (THSCODE)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE publication (
    PUBLID INTEGER NOT NULL PRIMARY KEY,
    CITATION TEXT,
    REFTYPE TEXT,
    ACQTYPE TEXT DEFAULT "X",
    DOI TEXT,
    FOREIGN KEY (ACQTYPE)
    REFERENCES acqtype_FI (THSCODE)
        ON UPDATE CASCADE
        ON DELETE SET DEFAULT
);

CREATE TABLE specdiet (
    FOODID INTEGER NOT NULL,
    SPECDIET TEXT,
    FOREIGN KEY (FOODID)
    REFERENCES food (FOODID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (SPECDIET)
    REFERENCES specdiet_FI (THSCODE)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE specdiet_FI (
    THSCODE TEXT NOT NULL PRIMARY KEY,
    DESCRIPT TEXT,
    LANG TEXT
);

CREATE TABLE eufdname_FI (
    THSCODE TEXT NOT NULL PRIMARY KEY,
    DESCRIPT TEXT,
    LANG TEXT
);

CREATE TABLE compunit_FI (
    THSCODE TEXT NOT NULL PRIMARY KEY,
    DESCRIPT TEXT,
    LANG TEXT
);

CREATE TABLE cmpclass_FI (
    THSCODE TEXT NOT NULL PRIMARY KEY,
    DESCRIPT TEXT,
    LANG TEXT
);

CREATE TABLE methdind_FI (
    THSCODE TEXT NOT NULL PRIMARY KEY,
    DESCRIPT TEXT,
    LANG TEXT
);

CREATE TABLE methtype_FI (
    THSCODE TEXT NOT NULL PRIMARY KEY,
    DESCRIPT TEXT,
    LANG TEXT
);

CREATE TABLE fuclass_FI (
    THSCODE TEXT NOT NULL PRIMARY KEY,
    DESCRIPT TEXT,
    LANG TEXT
);

CREATE TABLE igclass_FI (
    THSCODE TEXT NOT NULL PRIMARY KEY,
    DESCRIPT TEXT,
    LANG TEXT
);

CREATE TABLE process_FI (
    THSCODE TEXT NOT NULL PRIMARY KEY,
    DESCRIPT TEXT,
    LANG TEXT
);

CREATE TABLE foodtype_FI (
    THSCODE TEXT NOT NULL PRIMARY KEY,
    DESCRIPT TEXT,
    LANG TEXT
);

CREATE TABLE foodunit_FI (
    THSCODE TEXT NOT NULL PRIMARY KEY,
    DESCRIPT TEXT,
    LANG TEXT
);

/* commands for importing csv files into the tables created */

.mode csv
.separator ";"

.import db/publication_import.csv publication
.import db/methtype_FI_import.csv methtype_FI
.import db/igclass_FI_import.csv igclass_FI
.import db/component_import.csv component
.import db/fuclass_FI_import.csv fuclass_FI
.import db/process_FI_import.csv process_FI
.import db/food_import.csv food
.import db/eufdname_FI_import.csv eufdname_FI
.import db/component_value_import.csv component_value
.import db/cmpclass_FI_import.csv cmpclass_FI
.import db/foodunit_FI_import.csv foodunit_FI
.import db/contribfood_import.csv contribfood
.import db/foodname_FI_import.csv foodname_FI
.import db/foodname_TX_import.csv foodname_TX
.import db/specdiet_import.csv specdiet
.import db/foodaddunit_import.csv foodaddunit
.import db/specdiet_FI_import.csv specdiet_FI
.import db/acqtype_FI_import.csv acqtype_FI
.import db/methind_FI_import.csv methind_FI
.import db/foodtype_FI_import.csv foodtype_FI
.import db/compunit_FI_import.csv compunit_FI