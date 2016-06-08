/**
 * Copyright 2012, Le Tuan Anh (tuananh.ke@gmail.com)
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
 
-- DROP TABLES
DROP TABLE IF EXISTS dmrs_link_post;
DROP TABLE IF EXISTS dmrs_link_rargname;
DROP TABLE IF EXISTS dmrs_link;
DROP TABLE IF EXISTS dmrs_node;
DROP TABLE IF EXISTS dmrs_node_sortinfo;
DROP TABLE IF EXISTS dmrs_node_realpred;
DROP TABLE IF EXISTS dmrs_node_gpred;
DROP TABLE IF EXISTS dmrs;
DROP TABLE IF EXISTS representation;
DROP TABLE IF EXISTS sentence;
DROP TABLE IF EXISTS document;
DROP TABLE IF EXISTS corpus;

-- DROP INDICES
DROP INDEX IF EXISTS "realpred_lemma_index";
DROP INDEX IF EXISTS "dmrs_link_post_value_index";
DROP INDEX IF EXISTS "dmrs_link_rargname_value_index";
