/**
 * Copyright 2012, Le Tuan Anh (tuananh.ke@gmail.com)
 * This file is part of ChibiJS project.
 * ChibiJS is free software: you can redistribute it and/or modify 
 * it under the terms of the GNU General Public License as published by 
 * the Free Software Foundation, either version 3 of the License, or 
 * (at your option) any later version.
 * ChibiJS is distributed in the hope that it will be useful, but 
 * WITHOUT ANY WARRANTY; without even the implied warranty of 
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
 * See the GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License 
 * along with ChibiJS. If not, see http://www.gnu.org/licenses/.
 **/

function dump_bbox(obj, prefix){
    if(prefix != undefined){
        console.write(prefix);
    }
    var _bbox = obj.getBBox();
    if(typeof _bbox != "undefined"){
        console.write(" [BBOX ");
        console.write(" x=" + _bbox.x);
        console.write(" y=" + _bbox.y);
        console.write(" x2=" + _bbox.x2);
        console.write(" y2=" + _bbox.y2);
        console.write(" width=" + _bbox.width);
        console.write(" height=" + _bbox.height);
        console.writeline(" ]");
    }
    else{
        console.writeline("No bbox was found!");
    }
}

function dump_element(element){
    console.write(dump_object(element));
    info = '';
    if(element.size){ info += ' Size=' + element.size.str(); }
    if(element.centre){ info += ' Centre=' + element.centre.str(); }
    if(element.location){ info += ' TopLeft=' + element.location.str(); }
    console.writeline(info);
}

/**
 * Dump a canvas structure to console 
 **/
function displayInformation(a_canvas){
    if(a_canvas == null){
        a_canvas = canvas;
    }
    // console.clear("- Test Console -");
    console.writeline();
    console.writeline(dump_object(a_canvas), "red");
    var layers = a_canvas.getLayers();
    $.each(layers, function(idx,layer){
        console.writeline("-- " + dump_object(layer), "yellow");
        // Display all children tree
        travelStack = [[layer.getMainGroup(),1]]
        while(travelStack.length > 0){
            stackItem = travelStack.pop();
            element = stackItem[0];
            level = stackItem[1];
            prefix = "";
            for(i=0;i <= level;i++){ prefix += "--"; }
            console.write(prefix + " " + dump_object(element));
            
            info = '';
            if(element.size){ info += ' Size=' + element.size.str(); }
            if(element.centre){ info += ' Centre=' + element.centre.str(); }
            if(element.location){ info += ' TopLeft=' + element.location.str(); }
            console.writeline(info);
            
            if(typeof element.getElements === "function"){
                $.each(element.getElements(), function(idx, child){
                    item = [child, level+1];
                    travelStack.push(item);
                });
            }
        }
        // End each layer
        console.writeline();
    });
}
