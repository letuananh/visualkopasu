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
 
function draw_label(paper, x, y, text, padding_x, padding_y){
    //paper.circle(x,y, 3);
    padding_x = (padding_x != undefined) ? padding_x : 10;
    padding_y = (padding_y != undefined) ? padding_y : 10;
    
    a_box = paper.rect(x, y, 10, 10, 2);
    a_box.attr({"fill" : "#AAAAAA"
                ,"stroke" : "black"
                ,"stroke-width" : "1px"});

    a_text = paper.text(x, y, text);
    a_text.attr({'font-color': 'black'});
    // Adjust font
    a_text.attr({'font-family': '"Courier New", Courier, "Nimbus Mono L", monospace;'
                ,'text-anchor': 'center'
                ,'font-size': '10px'
    });

    bbox = a_text.getBBox();
    // Adjust box's width and height
    node_width = bbox.width + padding_x;
    node_height = bbox.height + padding_y;
    // Adjust box's location
    a_box.attr({
         "x" : x - node_width / 2
        ,"y" : y - node_height / 2
        ,"width" : node_width
        ,"height" : node_height
    });

    return { 'box' : a_box
            ,'text' : a_text
            , width : node_width
            , height : node_height
            , 'x' : x
            , 'y' : y
            };
}

function draw_line(paper, from_x, from_y,to_x,to_y){
    l=paper.path("M" + from_x + "," + from_y + "L" + to_x + "," + to_y);
}

function draw_link(paper, from_x,from_y,to_x,to_y){
    l = paper.path("M" + from_x + "," + from_y + "L" + from_x + "," + to_y + "L" + to_x + "," + to_y + "L" + to_x + "," + from_y);
}

function draw_box(paper, x, y, text, padding_x, padding_y, min_width){
    padding_x = (padding_x != undefined) ? padding_x : 5;
    padding_y = (padding_y != undefined) ? padding_y : 5;
    min_width = (min_width != undefined) ? min_width : 15;

    var a_box = paper.rect(x, y, 10, 10, 2);
    a_box.attr({"fill" : "#0066CC"
                ,"stroke" : "black"
                ,"stroke-width" : "1px"});

    var a_text = paper.text(x, y, text);
    // Adjust font
    a_text.attr({'font-family': '"Courier New", Courier, "Nimbus Mono L", monospace;'
                ,'text-anchor': 'center'
                ,'font-size': '14px'
                ,'fill' : 'white'
    });

    var bbox = a_text.getBBox();
    // Adjust box's width and height
    node_width = bbox.width + padding_x;
    node_height = bbox.height + padding_y;
    if(node_width < min_width){
        node_width = min_width;
    }
    a_box.attr({
         "width" : node_width
        ,"height" : node_height
    });
    // Adjust text's location
    a_text.attr({
         "x" : x + node_width / 2
        ,"y" : y + (bbox.height + padding_y) / 2
    });

    return { 'box' : a_box
            ,'text' : a_text
            , width : node_width
            , height : node_height
            , 'x' : x
            , 'y' : y
            };
}

function draw_text(paper, text, from, to){
    parts = [];
}

/**
 * Split a string
 * If from == to then string will be cut into 2 parts
 * If text is empty or from or to contains invalid value then an empty array will be returned
 **/
function string_split(text, from, to){
    var a_list = [];
    if(from > to){
        var temp = from;
        from = to;
        to = temp;
    }
    // Validate parameters
    if (text == undefined || text.length == 0 || from < 0 || from > text.length || to < 0 || to > text.length){
            return a_list;
    }
    if(from == 0 && to == text.length){
        return [ text ];
    }
    
    
    // Split
    //~ if(from > 0){
        a_list.push(text.slice(0, from));
    //~ }
    //~ if( from != to){
        a_list.push(text.slice(from, to));
    //~ }
    //~ if( to < text.length){
        a_list.push(text.slice(to, text.length));
    //~ }
    return a_list;
}

function draw_border(paper, paper_border){
    if(paper_border != undefined){
        paper_border.remove();
    }
    paper_border = paper.rect(1,1, paper.width - 2, paper.height -2, 2);
    paper_border.attr({"stroke" : "black"
            ,"stroke-width" : "1px"
            //,"fill" : "#FFFFFF"
            });
    return paper_border;
}

function draw_text(paper, text, x, y, from, to){
    if(text == undefined){
        return undefined;
    }
    else if(from == undefined || to == undefined){
        var a_text = paper.text(x, y, text);
        //console.writeline("Trying to print: '" + text + '\'');
        //console.writeline("a_text: " + a_text);
        //console.writeline("x: " + x);
        //console.writeline("y: " + y);
        // Adjust font
        try{
            a_text.attr({'font-family': '"Courier New", Courier, "Nimbus Mono L", monospace;'
                        ,'text-anchor': 'start'
                        ,'font-size': '14px'
            });
        }
        catch(err){
            console.writeline("Error: " + err);
        }
        //console.writeline("'" + text + "'");
        return a_text;
    }
    else{
        var raw_pieces = string_split(text, from, to);
        var pieces = [];
        console.writeline("From: " + from + " To: " + to);
        if(raw_pieces.length == 3){
                //console.writeline(dump_array(raw_pieces));
                
                if(raw_pieces[0].length > 0){
                    a_text = draw_text(paper, raw_pieces[0], x, y);
                    if(a_text != undefined){
                        x += a_text.getBBox().width;
                        pieces.push(a_text);
                    }
                }
                
                if(raw_pieces[1].length > 0){
                    a_text = draw_text(paper, raw_pieces[1], x, y);
                    if(a_text != undefined){
                        a_text.attr({'fill' : 'blue'});
                        x += a_text.getBBox().width;
                        pieces.push(a_text);
                    }
                }
            
                if(raw_pieces[2].length > 0){
                    a_text = draw_text(paper, raw_pieces[2], x, y);
                    x += a_text.getBBox().width;
                    pieces.push(a_text);
                }
                
                return pieces;  
        }
        else{
            return [ draw_text(paper, text, x, y) ]
        }
    }
}
