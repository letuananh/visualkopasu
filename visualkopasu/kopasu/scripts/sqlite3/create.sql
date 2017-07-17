/**
 * Copyright 2013, Le Tuan Anh (tuananh.ke@gmail.com)
 * This file is part of VisualKopasu.
 * VisualKopasu is free software: you can redistribute it and/or modify 
 * it under the terms of the GNU General Public License as published by 
 * the Free Software Foundation, either version 3 of the License, or 
 * (at your option) any later version.
 * VisualKopasu is distributed in the hope that it will be useful, but 
 * WITHOUT ANY WARRANTY; without even the implied warranty of 
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
 * See the GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License 
 * along with VisualKopasu. If not, see http://www.gnu.org/licenses/.
 **/

CREATE TABLE IF NOT EXISTS "corpus" (
    "ID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE 
    , "name" text NOT NULL 
);

CREATE TABLE IF NOT EXISTS "document" (
    "ID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE 
    , "name" TEXT NOT NULL
    , "title" TEXT
    , "corpusID" INTEGER NOT NULL 
    , FOREIGN KEY(corpusID) REFERENCES corpus(ID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "sentence" (
    "ID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE 
    , "ident" VARCHAR
    , "text" TEXT
    , "documentID" INTEGER
    , FOREIGN KEY(documentID) REFERENCES document(ID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "interpretation" (
    "ID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE 
    , "ident" VARCHAR NOT NULL 
    , "mode" VARCHAR
    , "sentenceID" INTEGER NOT NULL 
    , FOREIGN KEY(sentenceID) REFERENCES sentence(ID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "parse_raw" (
    "ID" INTEGER PRIMARY KEY  NOT NULL 
    , "ident" VARCHAR 
    , "text" TEXT
    , "rtype" VARCHAR NOT NULL
    , "interpretationID" INTEGER NOT NULL
    , FOREIGN KEY(interpretationID) REFERENCES interpretation(ID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "dmrs" (
    "ID" INTEGER PRIMARY KEY  NOT NULL 
    , "ident" VARCHAR NOT NULL 
    , "cfrom" INTEGER NOT NULL  DEFAULT (-1) 
    , "cto" INTEGER NOT NULL  DEFAULT (-1) 
    , "surface" TEXT
    , "interpretationID" INTEGER NOT NULL
    , FOREIGN KEY(interpretationID) REFERENCES interpretation(ID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "dmrs_link" (
    "ID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE 
    , "fromNodeID" INTEGER NOT NULL 
    , "toNodeID" INTEGER NOT NULL
    , "dmrsID" INTEGER NOT NULL
    , "post" TEXT NOT NULL
    , "rargname" TEXT NOT NULL
    , FOREIGN KEY(dmrsID) REFERENCES dmrs(ID) ON DELETE CASCADE ON UPDATE CASCADE
);

--
-- DMRS NODE
--
CREATE TABLE IF NOT EXISTS "dmrs_node" (
    "ID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE 
    , "nodeID" INTEGER NOT NULL 
    , "cfrom" INTEGER NOT NULL  DEFAULT (-1)
    , "cto" INTEGER NOT NULL  DEFAULT (-1)
    , "surface" TEXT
    , "base" VARCHAR
    , "carg" VARCHAR
    , "dmrsID" INTEGER NOT NULL
    -- realpred
    , "rplemmaID" INTEGER
    , "rppos" VARCHAR
    , "rpsense" VARCHAR
    --gpred
    , gpred_valueID VARCHAR
    -- wordnet synsets
    , synsetid CHARACTER(10)
    , synset_score INTEGER
    , FOREIGN KEY(dmrsID) REFERENCES dmrs(ID) ON DELETE CASCADE ON UPDATE CASCADE
);

--
-- SORT INFORMATION
--
CREATE TABLE IF NOT EXISTS "dmrs_node_sortinfo" (
    "ID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE 
    , "cvarsort" VARCHAR
    , "number" VARCHAR
    , "person" VARCHAR
    , "gender" VARCHAR
    , "sentence_force" VARCHAR
    , "tense" VARCHAR
    , "mood" VARCHAR
    , "pronoun_type" VARCHAR
    , "progressive" VARCHAR
    , "perfective_aspect" VARCHAR
    , "ind" VARCHAR 
    ,"dmrs_nodeID" INTEGER NOT NULL
    , FOREIGN KEY(dmrs_nodeID) REFERENCES dmrs_node(ID) ON DELETE CASCADE ON UPDATE CASCADE
);

--
-- REAL PREDICATE
--
CREATE TABLE IF NOT EXISTS "dmrs_node_realpred_lemma" (
    "ID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE
    ,"lemma" VARCHAR
);

--
-- GRAMMAR PREDICATE
-- 
CREATE TABLE IF NOT EXISTS "dmrs_node_gpred_value" (
    "ID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE
    , "value" VARCHAR 
);

CREATE INDEX IF NOT EXISTS "sentence_|_documentID" ON "sentence" ("documentID" ASC);
CREATE INDEX IF NOT EXISTS "interpretation_|_sentenceID" ON "interpretation" ("sentenceID" ASC);
CREATE INDEX IF NOT EXISTS "parse_raw_|_interpretationID" ON "parse_raw" ("interpretationID" DESC);
CREATE INDEX IF NOT EXISTS "dmrs_|_interpretationID" ON "dmrs" ("interpretationID" DESC);
CREATE INDEX IF NOT EXISTS "dmrs_node_|_dmrsID" ON "dmrs_node" ("dmrsID" ASC);

-- DMRS_NODE_SORTINFO INDICES
CREATE INDEX IF NOT EXISTS "dmrs_node_sortinfo|cvarsort" ON "dmrs_node_sortinfo"("cvarsort");
--CREATE INDEX IF NOT EXISTS "dmrs_node_sortinfo|number" ON "dmrs_node_sortinfo"("number");
--CREATE INDEX IF NOT EXISTS "dmrs_node_sortinfo|person" ON "dmrs_node_sortinfo"("person");
--CREATE INDEX IF NOT EXISTS "dmrs_node_sortinfo|gender" ON "dmrs_node_sortinfo"("gender");
--CREATE INDEX IF NOT EXISTS "dmrs_node_sortinfo|sentence_force" ON "dmrs_node_sortinfo"("sentence_force");
CREATE INDEX IF NOT EXISTS "dmrs_node_sortinfo|tense" ON "dmrs_node_sortinfo"("tense");
CREATE INDEX IF NOT EXISTS "dmrs_node_sortinfo|mood" ON "dmrs_node_sortinfo"("mood");
CREATE INDEX IF NOT EXISTS "dmrs_node_sortinfo|pronoun_type" ON "dmrs_node_sortinfo"("pronoun_type");
--CREATE INDEX IF NOT EXISTS "dmrs_node_sortinfo|progressive" ON "dmrs_node_sortinfo"("progressive");
--CREATE INDEX IF NOT EXISTS "dmrs_node_sortinfo|perfective_aspect" ON "dmrs_node_sortinfo"("perfective_aspect");
--CREATE INDEX IF NOT EXISTS "dmrs_node_sortinfo|ind" ON "dmrs_node_sortinfo"("ind");
CREATE INDEX IF NOT EXISTS "dmrs_node_sortinfo|dmrs_nodeID" ON "dmrs_node_sortinfo"("dmrs_nodeID");

-- INDEX CARG OF NODE
CREATE INDEX IF NOT EXISTS "dmrs_node_|_carg" ON "dmrs_node" ("carg");
CREATE INDEX IF NOT EXISTS "dmrs_node_|_synsetid" ON "dmrs_node" ("synsetid");

-- DMRS_NODE_GPRED INDICES
CREATE INDEX IF NOT EXISTS "dmrs_node_|_gpred_value" ON "dmrs_node"("gpred_valueID");

-- dmrs_node_gpred_value
CREATE INDEX IF NOT EXISTS "dmrs_node_gpred_value_|_value" ON "dmrs_node_gpred_value"("value");

-- DMRS_NODE_REALPRED INDICES
CREATE INDEX IF NOT EXISTS "dmrs_node_|_lemma_index" ON "dmrs_node"("rplemmaID");

-- DMRS_NODE_REALPRED_LEMMA INDICES
CREATE INDEX IF NOT EXISTS "dmrs_node_realpred_lemma_|_lemma" ON "dmrs_node_realpred_lemma"("lemma");

--DMRS_LINK INDICES
CREATE INDEX IF NOT EXISTS "dmrs_link_|_fromNodeID" ON "dmrs_link" ("fromNodeID" ASC);
CREATE INDEX IF NOT EXISTS "dmrs_link_|_toNodeID" ON "dmrs_link" ("toNodeID" ASC);
CREATE INDEX IF NOT EXISTS "dmrs_link_|_dmrsID" ON "dmrs_link" ("dmrsID" ASC);

CREATE INDEX IF NOT EXISTS "dmrs_link_|_post" ON "dmrs_link"("post");
CREATE INDEX IF NOT EXISTS "dmrs_link_|_rargname" ON "dmrs_link"("rargname");
