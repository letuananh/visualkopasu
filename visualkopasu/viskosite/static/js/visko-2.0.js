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
var VisualKopasu;
if(VisualKopasu == undefined){
    VisualKopasu = new function(){
        
        /** Get connectible points of a shape (top, bottom, left, right) **/
        this.findConnectPoints = function(shape){
            if(shape == undefined){ return undefined; }
            return [
                new Point(shape.location.x, shape.location.y + shape.size.height / 2)
                ,new Point(shape.location.x + shape.size.width, shape.location.y + shape.size.height / 2)
                ,this.getTopMiddle(shape)
                ,this.getBottomMiddle(shape)
            ];
        }
        
        /**
         * Find shortest line to connect two shapes
         **/
        this.connect = function(fromShape, toShape){
            var fromPoints = this.findConnectPoints(fromShape);
            var toPoints = this.findConnectPoints(toShape);
            if(!fromPoints || !toPoints){ return undefined; }
            
            var currentPair = [];
            var min_distance = ChibiJS.Geometry.distance(fromPoints[0], toPoints[0]);
            
            for(var i = 0; i < fromPoints.length; i++){
                for(var j = 0; j < toPoints.length; j++){
                    current_distance = ChibiJS.Geometry.distance(fromPoints[i], toPoints[j]);
                    if(current_distance < min_distance){
                        currentPair = [fromPoints[i], toPoints[j]];
                        min_distance = current_distance;
                    }
                }
            }
            // end for
            return currentPair;
        }
        
        /** get top-middle point of a shape (x + width / 2, y) **/
        this.getTopMiddle = function(shape){
            return new Point(shape.location.x + shape.size.width / 2, shape.location.y);
        }
        
        /** get bottom-middle point of a shape (x + width / 2, y + height) **/
        this.getBottomMiddle = function(shape){
            return new Point(shape.location.x + shape.size.width / 2, shape.location.y + shape.size.height);
        }
        // VisualKopasu static
        
    }
}

// Channel allocator
VisualKopasu.ChannelAllocator = function(){
    this.allocated_slots={}
    this.allocated_count = 0;
    
    this.count = function(){
        return this.allocated_count;
    }
    
    this.reserve = function(i, from, to){
        if(this.allocated_slots[i] == undefined){
            this.allocated_count++;
            this.allocated_slots[i] = [];
        }
        this.allocated_slots[i][this.allocated_slots[i].length]=[from, to];
    }
    
    this.allocate = function(from,to){
        if(from > to){
            temp = from;
            from = to;
            to = temp;
        }
        var i = 1;
        do{
            if(i in this.allocated_slots){
                is_allocated=false;
                
                // Check all current slots
                for(si=0;si < this.allocated_slots[i].length;si++){
                    var slot=this.allocated_slots[i][si];
                    var slot_from=slot[0];
                    var slot_to=slot[1];
                    if(
                        (slot_from <= from && from <= slot_to)
                            || (slot_from <= to && to <= slot_to)
                            || (from <= slot_from && slot_from <= to)
                            || (from <= slot_to && slot_to <= to)
                    ) {
                        // Allocated
                        is_allocated=true;
                        i++;
                        break;
                    } 
                }
                
                // If not allocated then use this
                if(is_allocated == false){
                    this.reserve(i, from, to);
                    return i;
                }
            }
            else{
                this.reserve(i, from, to);
                return i;               
            }       
        }while(is_allocated);
    }
    
}

VisualKopasu.DMRSTheme = function(){
    this.NODE_SPACE = 10; // space between nodes
    this.NODE_VERTICAL_SPACE = 20; // vertical space between nodes (e.g. node with RSTR link)
    this.LINK_SPACE = 20; // space between links
    this.LINK_SLOT_SPACE = 15; // space between links' head & tail
    
    // Node style
    this.NODE_PADDING_X = 4;
    this.NODE_PADDING_Y = 2;
    
    // Link style
    this.LINK_LABEL_PADDING_X = 3;
    this.LINK_LABEL_PADDING_Y = 1;
    this.LINK_HEAD_TEE_WIDTH = 12;
    this.LINK_HEAD_TEE_HEIGHT = 3;
    this.LINK_HEAD_BOX_WIDTH = 12;
    this.LINK_HEAD_BOX_HEIGHT = 12;
    this.LINK_HEAD_DOT_RADIUS = 6;
    this.ARROW_DELTA_X = 3;
    this.ARROW_DELTA_Y = 7;
    
    this.DMRS_NODE_TO_TOOLTIP = 20; // Space between DMRS node and sentence text
    this.DMRS_TO_NODE = 20; // Space between DMRS node and sentence text
    this.PAGE_MARGIN = 10;
    
    // Node labels
    this.TOOLTIP_ACTIVE_ARROW_STYLE = {
        "stroke" : "red"
        ,"stroke-width" : 2
    };
    this.TOOLTIP_INACTIVE_ARROW_STYLE ={
        "stroke" : "black"
        ,"stroke-width" : 1
    }
    this.TOOLTIP_ACTIVE_BORDER_STYLE = {
        "stroke" : "red"
        ,"fill" : "#FF3300"
        ,"stroke-width" : 2
    };
    this.TOOLTIP_INACTIVE_BORDER_STYLE = {
        "stroke" : "black"
        ,"fill" : "#686868"
        ,"stroke-width" : 1
    };
    
    // Nodes & links
    this.DEFAULT_LINK_STYLE = {
        'stroke' : 'black'
    };
    this.LINK_LABEL_BOX_STYLE = {
        "fill" : "#AAAAAA"
        ,"stroke" : "black"
        ,"stroke-width" : "1px"
    };
    this.LINK_LABEL_TEXT_STYLE = {
        'fill': 'black'
        ,'font-family': '"Courier New", Courier, "Nimbus Mono L", monospace'
        //,'text-anchor': 'center'
        ,'font-size': '10px'
    };
    this.GPRED_NODE_BOX_STYLE = {
        //"fill" : "#4D94DB"
        "fill" : "#CCE0F5"
    };
    this.GPRED_NODE_TEXT_STYLE = {
        "fill" : "#222222"
    };
    this.CARG_NODE_BOX_STYLE = {
        //"fill" : "#4D94DB"
        //"fill" : "#CCE0F5"
        "stroke-width" : 2
    };
    this.CARG_NODE_TEXT_STYLE = {
        //"fill" : "#222222"
    };
    
    // Sentence style
    this.DMRS_SENTENCE_TEXT_STYLE = {
        'fill': 'black'
        ,'font-family': 'monospace, "Courier New", Courier, "Nimbus Mono L"'
        //,'text-anchor': 'center'
        ,'font-size': '14px'
    };
}

VisualKopasu.SentenceText = function(holder_id, text){
    this.holder = $("#" + holder_id);
    this.text = text;
    
    this.highlight = function(from,to){
        from = (from == undefined) ? 0 : from;
        to = (to == undefined) ? 0 : to;
        var text_pieces = this.string_split(from, to);
        this.holder.html('');
        if(text_pieces[0].length > 0){
            this.holder.append("<span class='sentence_text_normal'>" + text_pieces[0] + "</span>");
        }
        if(text_pieces[1].length > 0){
            this.holder.append("<span class='sentence_text_highlight'>" + text_pieces[1] + "</span>");
        }
        if(text_pieces[2].length > 0){
            this.holder.append("<span class='sentence_text_normal'>" + text_pieces[2] + "</span>");
        }
    }
    
    this.string_split = function(from, to){
        if(from == undefined || to == undefined){
            return [this.text, '', ''];
        }
        var a_list = [];
        if(from > to){
            var temp = from;
            from = to;
            to = temp;
        }
        // Validate parameters
        if (this.text == undefined || this.text.length == 0 
            || from < 0 || from > this.text.length 
            || to < 0 || to > this.text.length){
            return ['', '', a_list]; // Invalid => no highlight
        }
        if(from == 0 && to == this.text.length){
            return [ '', this.text, '' ];
        }
        
        a_list.push(this.text.slice(0, from));
        a_list.push(this.text.slice(from, to));
        a_list.push(this.text.slice(to, text.length));
        
        return a_list;
    }
}

VisualKopasu.DMRSCanvas = function(dmrs, canvas, text_holder, theme){
    var dmrs = dmrs;
    var nodes = dmrs.nodes;
    var links = dmrs.links;
    var sentence_text = dmrs.text;
    var canvas = (typeof canvas == 'string') ? new Canvas(canvas) : canvas;
    var text_holder = (typeof text_holder == 'string') ? new VisualKopasu.SentenceText(text_holder, dmrs.text) : text_holder;
    var theme = (theme == undefined) ? new VisualKopasu.DMRSTheme() : theme;
    // layers
    var layer_nodes = canvas.addLayer("Nodes layer");
    var layer_links = canvas.addLayer("Links layer");
    var layer_link_labels = canvas.addLayer("Link-label layer");
    var layer_text = canvas.addLayer("Text layer");
    var layer_tooltip = canvas.addLayer("Tooltip layer");
    var node_flow = new ChibiJS.ShinChan.HorizontalFlow(layer_nodes); // Reflow node after draw
    var node_vflow = []; // Vertical flow for nodes linked by RSTR
    
    this.clear = function(){
        var holder = $("#" + canvas.holder_name);
        if (holder.has('svg') && canvas.getLayers().length > 0){
            $("#" + canvas.holder_name).empty();
        }
        // canvas = new Canvas(canvas.holder_name);
    }
    
    this.visualise = function(){
        // this.clear();
        // Map links
        $.each(links, function(idx, a_link){
            if(a_link.from.linkTo == undefined){
                a_link.from.linkTo = [];
            }
            a_link.from.linkTo.push(a_link);
            
            if(a_link.to.linkFrom == undefined){
                a_link.to.linkFrom = [];
            }
            a_link.to.linkFrom.push(a_link);
        });
        this.draw_nodes();
        this.draw_tooltips();
        this.draw_links();
        if(text_holder != undefined){
            text_holder.highlight();
        }
        canvas.pack(theme.PAGE_MARGIN);
        return this;
    }

    /** Get DMRS data (compiled from JSON string?) **/
    this.get_data = function() {
        return dmrs;
    }
    /** get a pointer to Shinchan canvas object **/
    this.get_canvas = function(){
        return canvas;
    }
    
    this.draw_nodes = function(){
        // Draw nodes
        var prev_node;
        for(var idx = 0; idx < nodes.length; idx++){
            var current_node = nodes[idx];
            min_width = (current_node.link_count + 1) * theme.LINK_SLOT_SPACE;
            var node_style = 'rounded';
            //console.writeline(current_node.text + " - " + current_node.pos);
            switch(current_node.pos){
            case 'a':{ node_style = 'parallelogram'; break; }
            case 's':{ node_style = 'diagonals'; break; }
            case 'n':{ node_style = 'rect'; break; }
            case 'v':{ node_style = 'hexagon'; break; }
            }
            visual_node = layer_nodes.draw_label(0, 0, 
                                                 current_node.text, theme.NODE_PADDING_X, theme.NODE_PADDING_Y, current_node.text, min_width, node_style); // Draw a node at (0,0), we'll reflow the nodes later ...
            visual_node.node_info = current_node;
            current_node.visual_element = visual_node;
            if(current_node.type == "gpred"){
                // Change node style
                visual_node.getElements()[0].attr(theme.GPRED_NODE_BOX_STYLE);  
                visual_node.getElements()[1].attr(theme.GPRED_NODE_TEXT_STYLE);             
            }
            else if(current_node.type == "carg"){
                visual_node.getElements()[0].attr(theme.CARG_NODE_BOX_STYLE);   
                visual_node.getElements()[1].attr(theme.CARG_NODE_TEXT_STYLE);
            }
            
            /*
              if(prev_node != undefined){
              node_vflow.push(new ChibiJS.ShinChan.VerticalFlow(layer_nodes, [visual_node, prev_node]));
              }
              // If two nodes are linked by a RSTR link, move the fromNode beneath its next node
              prev_node = undefined;
              if(current_node.linkTo != undefined){
              for(var i = 0; i < current_node.linkTo.length; i++){
              if(current_node.linkTo[i].rargname == 'RSTR'
              && idx+1 < nodes.length){
              prev_node = visual_node;
              break;
              }
              } //end-for 
              } // end-if defined
              if(prev_node == undefined){
              node_flow.addElement(visual_node);
              }
            */
            node_flow.addElement(visual_node);
        }
        // Reflow node
        node_flow.rearrange(theme.NODE_SPACE);
        $.each(node_vflow, function(idx, vflow){
            vflow.rearrange(theme.NODE_VERTICAL_SPACE);
        });
    }
    
    this.draw_tooltips = function(){
        
        // Create tooltips & events
        $.each(nodes, function(idx, a_node){
            
            (function(){
                var current_node = a_node;
                var visual_node = current_node.visual_element;
                // Highlight sentence part
                visual_node.hover(
                    function(){ 
                        // highlight selected node
                        if(text_holder){
                            text_holder.highlight(current_node.from, current_node.to);
                        }
                    }
                    ,function(){}
                );
                // Create tooltip if needed
                if(current_node.tooltip == undefined || current_node.tooltip.length == 0){
                    return;
                }
                //layer_tooltip
                var tooltip_table = layer_nodes.draw_table(0, 0, current_node.tooltip, current_node.text + "_tooltip");
                CanvasUtil.moveDown(visual_node, tooltip_table, theme.DMRS_NODE_TO_TOOLTIP);
                CanvasUtil.alignCentre([visual_node, tooltip_table]);
                tooltip_table.text.attr({'fill': 'white'});
                // Connect tooltip to node
                var points = [
                    VisualKopasu.getBottomMiddle(visual_node)
                    , VisualKopasu.getTopMiddle(tooltip_table)
                ];
                var tooltip_arrow = layer_nodes.draw_arrow(points[0].x, points[0].y, points[1].x, points[1].y);
                var tooltip = layer_nodes.group([tooltip_table, tooltip_arrow]);
                
                // Hide tooltip by default and register events
                tooltip.hide();
                tooltip.Permanent = false;
                visual_node.click(function(){
                    tooltip.Permanent = !tooltip.Permanent;
                });
                visual_node.hover(
                    function(){ 
                        tooltip_arrow.attr(theme.TOOLTIP_ACTIVE_ARROW_STYLE);
                        tooltip_table.bound.attr(theme.TOOLTIP_ACTIVE_BORDER_STYLE);
                        tooltip.show();
                        tooltip.toFront(); 
                    }
                    ,function(){
                        tooltip_arrow.attr(theme.TOOLTIP_INACTIVE_ARROW_STYLE);
                        tooltip_table.bound.attr(theme.TOOLTIP_INACTIVE_BORDER_STYLE);
                        if(!(tooltip.Permanent)) {
                            tooltip.hide(); 
                        }
                        if(text_holder){ text_holder.highlight(); } // remove highlight
                    }
                );
            })();   
        }); // End with each node ...
    }
    
    this.getTheme = function(){
        return theme;
    }
    
    /**
     * Draw all links
     **/ 
    this.draw_links = function(){
        var allocator = new VisualKopasu.ChannelAllocator();
        //var below_allocator = new VisualKopasu.ChannelAllocator(); // links below
        
        node_slots = []
        for ( i = 0; i < nodes.length; i++) {
            nodes[i].slot = 1;
        }
        for ( i = 0; i < links.length; i++) {
            from_node = links[i].from;
            to_node = links[i].to;
            rargname = links[i].rargname;
            post = links[i].post;
            
            // Draw link (line) 
            // from_node.slot means a free slot ID of from_node
            from_x = from_node.visual_element.location.x + theme.LINK_SLOT_SPACE * from_node.slot;
            from_node.slot++;
            to_x = to_node.visual_element.location.x + theme.LINK_SLOT_SPACE * to_node.slot;
            to_node.slot++;
            channel = allocator.allocate(from_x, to_x);
            from_y = from_node.visual_element.location.y;
            to_y = from_y - theme.LINK_SPACE * (channel + 1);
            
            l = new Path().moveTo(from_x, from_y)
                .lineTo(from_x, to_y)
                .lineTo(to_x, to_y)
                .lineTo(to_x, from_y).drawTo(layer_links, "link");
            
            // Set link style based on rargname
            if (rargname == 'RSTR') {
                l.attr({'stroke-dasharray' : '- '});
            } else if (rargname == 'L-HNDL' || rargname == 'R-HNDL') {
                l.attr({'stroke-dasharray' : '.'});
            } else if (rargname == '') {
                c = layer_links.draw_circle(from_x, to_y, 3).attr({'fill' : 'black'});
                c = layer_links.draw_circle(to_x, to_y, 3).attr({'fill' : 'black'});
            }
            l.attr(theme.DEFAULT_LINK_STYLE);
            
            /* Draw link head
            //- H: tee, 
            //- EQ: none,
            //- NEQ: dot,
            //- HEQ: box. */
            if (post == "H") {
                draw_tee_tail(from_x, from_y);
            } else if (post == 'NEQ') {
                draw_circle_tail(from_x, from_y);
            } else if (post == 'HEQ') {
                draw_box_tail(from_x, from_y);
            } 
            if (['1', '2', '3', '4', 'A'].indexOf(rargname)){
                draw_arrow(to_x, from_y)    
            }
            
            // Draw link's label
            if(rargname.length > 0 && rargname != 'RSTR'){
                if (to_x < from_x) {
                    label_x = to_x + Math.abs(to_x - from_x) / 2;
                } else {
                    label_x = from_x + Math.abs(to_x - from_x) / 2;
                }
                label_y = to_y;
                
                link_label = layer_link_labels.draw_label(label_x, label_y, rargname, theme.LINK_LABEL_PADDING_X, theme.LINK_LABEL_PADDING_Y, '', 0, 'rect');
                link_label.toFront();
                // set link label style
                link_label.getElements()[0].attr(theme.LINK_LABEL_BOX_STYLE);
                link_label.getElements()[1].attr(theme.LINK_LABEL_TEXT_STYLE);
            }
        } // End for links
    }
    
    /**
     * Draw link tail: tee style (H)
     **/
    function draw_tee_tail(x, y){
        //- H: tee
        b_x = x - theme.LINK_HEAD_TEE_WIDTH / 2;
        b_y = y - theme.LINK_HEAD_TEE_HEIGHT - 1;
        r = layer_links.draw_rect(b_x, b_y, theme.LINK_HEAD_TEE_WIDTH, theme.LINK_HEAD_TEE_HEIGHT)
            .attr({'fill' : 'white'});
        return r;   
    }
    
    /**
     * Draw link tail: dot style (NEQ)
     **/
    function draw_circle_tail(x, y){
        c = layer_links.draw_circle(x, y - theme.LINK_HEAD_DOT_RADIUS, theme.LINK_HEAD_DOT_RADIUS)
            .attr({'fill' : 'red'});
        return c;
    }
    
    /**
     * Draw link tail: box style (HEQ)
     **/
    function draw_box_tail(x, y){
        b_x = x - theme.LINK_HEAD_BOX_WIDTH / 2;
        b_y = y - theme.LINK_HEAD_BOX_HEIGHT;
        c = layer_links.draw_rect(b_x, b_y, theme.LINK_HEAD_BOX_WIDTH, theme.LINK_HEAD_BOX_HEIGHT)
            .attr({'fill' : 'black'});
        return c;
    }
    
    /**
     * Draw link head: arrow
     **/
    function draw_arrow(x, y){
        return new Path().moveTo(x - theme.ARROW_DELTA_X, y - theme.ARROW_DELTA_Y)
            .lineTo(x,y)
            .lineTo(x + theme.ARROW_DELTA_X, y - theme.ARROW_DELTA_Y)
            .drawTo(layer_links);
    }   
    
}


function get_synset_link(synsetid){
    if (synsetid != undefined){
        return "http://compling.hss.ntu.edu.sg/omw/cgi-bin/wn-gridx.cgi?synset=" + sense.synsetid;
    }
    else {
        return "#";
    }
}

/*
 * Create a Visko object from a DMRS/JSON string
 */
function json2visko(json, synset_link_builder){
    if (synset_link_builder == undefined){
        synset_link_builder = get_synset_link;
    }

    var text = json.text;
    var nodes = [];
    var node_map = {};

    // Visko nodes require -> text, from, to, type, pos, linkcount
    // convert nodes
    $(json.nodes).each(function(idx, elem){
        var node = {'text': elem.predicate, 'from': elem.lnk.from, 'to': elem.lnk.to, 'type': elem.type, 'pos': elem.pos, linkcount: 0, 'nodeid': elem.nodeid, 'tooltip': [], 'senses': []};
        
        // build tooltip
        max_length = 3;
        colcount = 0;
        row = [];
        // get senses
        if (elem.senses != undefined && elem.senses.length > 0){
            sense = elem.senses[0];
            var sense_text = sense.synsetid + ": " + sense.lemma;
            var sense_url = (sense.url == undefined) ? synset_link_builder(sense.synsetid) : sense.url;
            colcount = 1;
            var sense_obj = new ChibiJS.URL(sense_text, sense_url);
            row = [sense_obj];
            node.tooltip.push(row);
            node.senses.push(sense_obj);
        }
        
        if (elem.sortinfo != undefined && Object.keys(elem.sortinfo).length > 0){
            if (node.tooltip.length == 0){
                node.tooltip.push(row);
            }
            for (k in elem.sortinfo){
                colcount++;
                if (colcount == 3){
                    colcount = 1;
                    row = [];
                    node.tooltip.push(row)
                }
                row.push(k + ":" + elem.sortinfo[k])
            }
            // console.writeline("Tooltip: " + node.tooltip + " | len: " + node.tooltip.length);
        }
        node_map[elem.nodeid] = node;
        nodes.push(node);
    });
    // convert links
    var links = [];
    $(json.links).each(function(idx, l){
        // create TOP node (id=0) if needed
        if (l.from == 0 || l.to == 0){
            if (node_map[0] == undefined){
                node_map[0] = {'text': 'TOP', 'from': 0, 'to': 0, 'type': 'realpred', 'pos': 'TOP', linkcount: 0, 'nodeid': 0, 'tooltip': []};
                nodes.unshift(node_map[0]);
            }
        }
        var fnode = node_map[l.from];
        fnode.linkcount++;
        var tonode = node_map[l.to];
        tonode.linkcount++;
        var lnk = {'from': fnode, 'to': tonode, 'post': l.post, 'rargname': (l.rargname != undefined) ? l.rargname : ''};
        
        links.push(lnk);
    });
    
    visko = { 'text': text, 'nodes': nodes, 'links': links, 'node_map':  node_map };
    return visko;
}

/**
 * Create a visko canvas for a given DMRS/JSON
 **/
function json2canvas(json, dmrs_id, synset_link_builder) {
    dmrs_obj = json2visko(json, synset_link_builder);
    canvas = new VisualKopasu.DMRSCanvas(dmrs_obj, dmrs_id + "_canvas", dmrs_id + "_text_holder");
    return canvas;
}

var rawblock = _.template('<pre><code id="dmrs<%=pid%>_json"><%=json%></code></pre>');

/**
 * Render a DMRS using Visko
 **/
function render_visko(parse, parseid, container){
    if (parseid == undefined) { parseid = 1; }
    if (container == undefined) { container = 'dmrses'; }
    // Create a h2 for canvas
    var div_parse = $('<h3></h3>');
    div_parse.text('Parse #' + parseid);
    div_parse.attr('id', 'parse' + parseid);
    $('#' + container).append(div_parse);
    // Create a div for canvas
    var div_canvas = $('<div></div>');
    div_canvas.attr('id', 'dmrs' + parseid + '_canvas');
    $('#dmrses').append(div_canvas);
    dmrs_visko = json2visko(parse, find_synset);
    var dmrs_canvas = new VisualKopasu.DMRSCanvas(dmrs_visko, 'dmrs' + parseid + '_canvas', 'sentence_text');
    dmrs_canvas.visualise();
}

/**
 * Display XML raw data
 **/
function display_xml(content) {
    $('#xmlcontent').text(content);
    highlight('#xml');
}

/**
 * Display MRS and DMRS raw data (pyDelphin format)
 **/
function display_raw(parse, parseid, container){
    if (container == undefined) { container = 'raws'; }
    // Header
    var div_rparse = $('<h3></h3>');
    div_rparse.text('Parse #' + parseid);
    div_rparse.attr('id', 'rparse' + parseid);
    $('#' + container).append(div_rparse);
    // MRS JSON
    $('#' + container).append($('<h4>MRS</h4>'));
    var div_raw = $(rawblock({'pid': parseid, 'json': parse.mrs_raw}));
    $('#' + container).append(div_raw);
    // DMRS JSON
    $('#' + container).append($('<h4>DMRS</h4>'));
    var div_raw = $(rawblock({'pid': parseid, 'json': parse.dmrs_raw}));
    $('#' + container).append(div_raw);
}

/**
 * Display raw JSON data (to a pre/code block)
 **/
function display_json(parse, parseid, container){
    if (container == undefined) { container = 'jsons'; }
    // Header
    var div_rparse = $('<h3></h3>');
    div_rparse.text('Parse #' + parseid);
    div_rparse.attr('id', 'rparse' + parseid);
    $('#' + container).append(div_rparse);
    // MRS JSON
    $('#' + container).append($('<h4>MRS</h4>'));
    var div_raw = $(rawblock({'pid': parseid, 'json': JSON.stringify(parse.mrs)}));
    $('#' + container).append(div_raw);
    // DMRS JSON
    $('#' + container).append($('<h4>DMRS</h4>'));
    var div_raw = $(rawblock({'pid': parseid, 'json': JSON.stringify(parse.dmrs)}));
    $('#' + container).append(div_raw);
}
