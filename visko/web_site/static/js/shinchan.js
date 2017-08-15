/**
 * Copyright 2013, Le Tuan Anh (tuananh.ke@gmail.com)
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

var ChibiJS;
var ちび;

if(ChibiJS == undefined){
    // ChibiJS module
    ChibiJS = new function(){};
    if(ちび == undefined){
        ちび = ChibiJS;
    }
    ChibiJS.ShinChan = new function(){};
}

/**
 * A simple ID Generator 
 */
ChibiJS.IDGenerator = new function (){
    
    var current_id = 1;
    
    this.generate = function(){
        return current_id++;
    }
}

ChibiJS.newid = function(){
    return ChibiJS.IDGenerator.generate();
};


//
// Data structures
//
ChibiJS.Table = function(table_data){
    this.column_width = [];
    this.row_height = [];
    this.table_data = (table_data == undefined) ? [] : table_data;
}

ChibiJS.Table.prototype = {
        
    addRow : function(row_data){        
        this.table_data.push(row_data);
    }
    ,columnCount : function(){
        return this.column_width.length;        
    }
    ,rowCount : function(){
        return this.row_height.length;
    }
    ,getData : function(){
        return this.table_data;
    }
    ,getAllCells : function(){ // Get all cells of this ChibiJS.Table
        var all_cells = [];
        for(var rid =0; rid < this.table_data.length;rid++){
            for(var cid = 0; cid < this.table_data[rid].length; cid++){
                if(this.table_data[rid][cid]){
                    all_cells.push(this.table_data[rid][cid]);
                }
            }
        }
        return all_cells;
    }
    ,setCell : function(row_index, column_index, value){
        if(this.table_data[row_index] == undefined){
            this.table_data[row_index] = [];
        }
        this.table_data[row_index][column_index] = value;
    }
    ,getCell : function(row_index, column_index){
        if(this.table_data[row_index] == undefined){
            return undefined;
        }
        else{
            return this.table_data[row_index][column_index];
        }
    }
    ,setRowHeight : function (row_index, size){
        if((row_index >= 0) && size > 0){
            this.row_height[row_index] = size;
        }   
    }
    ,getRowHeight : function (row_index){
        if(this.row_height[row_index]){
            return this.row_height[row_index];
        }
        else{
            return 0;
        }
    }
    ,expandRowHeight : function (row_index, size){
        if(this.getRowHeight(row_index) < size){
            this.setRowHeight(row_index, size);
        }
    }
    ,setColumnWidth : function (column_index, size){
        if((column_index >= 0) && size > 0){
            this.column_width[column_index] = size;
        }   
    }
    ,getColumnWidth : function (column_index){
        if(this.column_width[column_index]){
            return this.column_width[column_index];
        }
        else{
            return 0;
        }
    }
    ,expandColumnWidth : function (column_index, size){
        if(this.getColumnWidth(column_index) < size){
            this.setColumnWidth(column_index, size);
        }
    }
    ,str : function(){
        return "A table object";
    }

}

//
// URL
//
ChibiJS.URL = function(text, url){
    this._text = text;
    this._url = url;
}
ChibiJS.URL.prototype = {
    text : function(){ return this._text; }
    ,url : function(){ return this._url; }
    ,str : function(){
        return '<a target="_blank" href="' + this._url + '">' + this._text + '</a>';
    }
}

//
// A simple canvas library
//

/**
 * Point class (contain location related information - x-axis and y-axis)
 * When used as location, normally represented the top-left point of a shape or a group
 **/
ChibiJS.ShinChan.Point = function (x,y){
    this.x = x;
    this.y = y;
}

ChibiJS.ShinChan.Point.prototype = {
    equals : function(another){
        if(another && another.x && another.y && this.x && this.y){
            return (this.x == another.x) && (this.y == another.y);
        }
    },
    
    str : function(){
        return "Point(x={0},y={1})".replace('{0}', this.x).replace('{1}', this.y);
    }
}

/**
 * Dimension class (contain size related information - width and height)
 **/
ChibiJS.ShinChan.Dimension = function(width, height){
    this.width = width;
    this.height = height;
}

ChibiJS.ShinChan.Dimension.prototype = {
    equals : function(another){
        if(another && another.width && another.height && this.width && this.height){
            return (this.width == another.width) && (this.height == another.height);
        }
    },
    
    str : function(){
        return "Dimension(width={0},height={1})".replace('{0}', this.width).replace('{1}', this.height);
    }
}
 
/**
 * Shape object, contains a Shape (Raphael-based in current version)
 **/
ChibiJS.ShinChan.Shape = function(obj, parent, shapeName){
    var id = ChibiJS.IDGenerator.generate();
    var parent = parent;
    var obj = obj;
    this.name = (shapeName == undefined) ? id : shapeName;

    this.translate = function(x,y){
        var from_x, from_y;
        var shift_x = x;
        var shift_y = y;
        if(from_x == undefined){ from_x = obj.getBBox().x; }
        if(from_y == undefined){ from_y = obj.getBBox().y; }
        var to_x = from_x + x;
        var to_y = from_y + y;
        var location = new ChibiJS.ShinChan.Point(from_x, from_y);
        var size = new ChibiJS.ShinChan.Dimension(obj.getBBox().width, obj.getBBox().height);
        if(typeof obj === "undefined"){ return; }
        if(obj.getBBox() == undefined){ //Object is destroyed, no bbox exist
            return;
        }
        else{
            //do{
                // TODO: Find root cause
                // Sometimes, the bbox fool us around so the move doesn't work like it should ???
                obj.transform("...T" + shift_x + "," + shift_y);
                this.findShapeInfo(true);
                shift_x = to_x - this.location.x;
                shift_y = to_y - this.location.y;
            //}
            //while(shift_x != 0 || shift_y != 0);
            
            this.findShapeInfo();
        }
    }
    
    this.moveTo = function(x,y){ //Shape.moveTo (move shape to x,y)
        //do{
            shift_x = x - this.location.x;
            shift_y = y - this.location.y;
            this.translate(shift_x, shift_y);   
        //}
        //while(false || this.location.x != x || this.location.y != y);
    }
    
    this.str = function(){
        return "Shape[id=" + id + "]" + ((this.name != id) ? " [name=" + this.name + "]" : "");
    }
    
    this.getObject = function(){
        return obj;
    }
    
    this.findShapeInfo = function(forceRefresh){ //Shape.findShapeInfo
        if(typeof obj == "undefined") { return; } // no Object
        var bbox = obj.getBBox();
        if(typeof bbox == "undefined"){
            // something is wrong with this SHAPE!!!
            return false;
        }
        
        this.location = new ChibiJS.ShinChan.Point(bbox.x, bbox.y);
        this.size = new ChibiJS.ShinChan.Dimension(bbox.width, bbox.height);
        this.centre = new ChibiJS.ShinChan.Point( bbox.x + bbox.width / 2, bbox.y + bbox.height / 2 );
        //this.centre = new ChibiJS.ShinChan.Point( bbox.x + (bbox.x2 - bbox.x) / 2, bbox.y + (bbox.y2 - bbox.y) / 2 );
        
        // Notify parent about changes
        if(!forceRefresh && this.getParent().findShapeInfo){
            this.getParent().findShapeInfo();
        }
    }
    
    this.setParent = function(_parent){
        parent = _parent;
    }
    
    this.getParent = function(){
        return parent;
    }
    
    this.findShapeInfo();
}

ChibiJS.ShinChan.Shape.prototype = {
    getSize : function(){
        return this.size;
    }
    
    ,getLocation : function(){
        return this.location;
    }
    
    ,getCentre : function(){
        return this.centre;
    }
    
    /** Remove child object from canvas **/
    ,deleteChildren : function(){
        // Call Raphael remove, object will be removed from canvas
        this.getObject().remove(); 
    }
    
    ,click : function(handler){ this.getObject().click(handler); }
    ,click_params : function(params, handler){ this.getObject().click(params, handler); }
    ,unclick : function(handler){ this.getObject().unclick(handler); }
    ,hide : function(){ this.getObject().hide(); }
    ,show : function(){ this.getObject().show(); }
    ,hover : function(f_in, f_out){ this.getObject().hover(f_in, f_out); }
}

/**
 * Group object, contains a group (Raphael-based in current version)
 * A group can contains sub-groups or shapes
 **/
ChibiJS.ShinChan.Group = function(parent, groupName){
    var id = ChibiJS.IDGenerator.generate();
    this.elements = [];
    var parent = parent;
    this.name = (groupName == undefined) ? id : groupName;
    
    /**
     * Return a Shape object wraps the given shape_object
     **/
    this.add = function(element){
        this.elements.push(element);
        this.findShapeInfo();
        return element;
    }
    
    /**
     * Translate the whole group
     **/
    this.translate = function(x,y){
        $.each(this.elements, function(index, element) {
            element.translate(x,y);
        });
        this.findShapeInfo();
    }
    
    this.moveTo = function(x,y){ //Group.moveTo (move a group to point x,y)
        shift_x = x - this.location.x;
        shift_y = y - this.location.y;
        this.translate(shift_x, shift_y);
    }
    
    this.findShapeInfo = function(forceRefresh) {
        if(forceRefresh){
            $.each(this.elements, function(idx, element){
                if(element.findShapeInfo){
                    element.findShapeInfo(true);
                }
            });
        }
        
        if(this.elements.length == 0){ return; } // No element
        if(!this.elements[0].location || !this.elements[0].size){ return false; }
        var min_x = this.elements[0].location.x;
        var min_y = this.elements[0].location.y;
        var max_x = this.elements[0].location.x + this.elements[0].size.width;
        var max_y = this.elements[0].location.y + this.elements[0].size.height;
        
        for(var i = 1; i < this.elements.length; i++){
            if(this.elements[i].location.x < min_x){ min_x = this.elements[i].location.x; }
            if(this.elements[i].location.y < min_y){ min_y = this.elements[i].location.y; }
            if(this.elements[i].location.y + this.elements[i].size.height > max_y){ 
                max_y = this.elements[i].location.y + this.elements[i].size.height; 
            }
            if(this.elements[i].location.x + this.elements[i].size.width > max_x){ 
                max_x = this.elements[i].location.x + this.elements[i].size.width; 
            }
        }
        this.size = new ChibiJS.ShinChan.Dimension(max_x - min_x, max_y - min_y);
        this.location = new ChibiJS.ShinChan.Point(min_x, min_y);
        //this.centre = new ChibiJS.ShinChan.Point( (max_x - min_x) / 2, (max_y - min_y) / 2 );
        this.centre = new ChibiJS.ShinChan.Point( min_x + this.size.width / 2, min_y + this.size.height / 2 );
        
        // Notify parent about changes
        if(!forceRefresh && this.getParent().findShapeInfo){
            this.getParent().findShapeInfo();
        }
    }
    
    this.indexOf = function(element){
        return this.elements.indexOf(element);
    }
    
    this.getElement = function(idx){
        return this.elements[idx];
    }
    
    this.getElements = function(){
        return this.elements;
    }

    this.setParent = function(_parent){
        parent = _parent;
    }
    
    this.getParent = function(){
        return parent;
    }

    this.str = function(){
        return "Group[id=" + id + "]" + ((this.name != id) ? " [name=" + this.name + "]" : "");
    }
}
/** Remove an element from group (but the element will still be on canvas) **/
ChibiJS.ShinChan.Group.prototype.remove = function(element){
    idx = this.elements.indexOf(element);
    if(idx >= 0){
        this.elements.splice(idx, 1);
        this.findShapeInfo();
        return true;
    }
    return false;
}
/** Remove an element from group and delete it from canvas as well **/
ChibiJS.ShinChan.Group.prototype.deleteElement = function(element){
    idx = this.elements.indexOf(element);
    if(idx >= 0){
        element.deleteChildren();
        this.elements.splice(idx, 1);
        this.findShapeInfo();
        return true;
    }
    return false;
}
/** Remove all children from current group and delete them from canvas as well **/
ChibiJS.ShinChan.Group.prototype.deleteChildren = function(){
    $.each(this.elements, function(idx, element){
        element.deleteChildren();
    });
}
/** Register click event handler with all children **/
ChibiJS.ShinChan.Group.prototype.click = function(handler){ 
    $.each(this.elements, function(idx, element){
            element.click(handler);
    });
}
/**
 * Set all children's attribute values  
 */
ChibiJS.ShinChan.Group.prototype.attr = function(attr_map){ 
    $.each(this.elements, function(idx, element){
            element.attr(attr_map);
    });
}
/** Register click event handler with all children **/
ChibiJS.ShinChan.Group.prototype.toFront = function(){ 
    $.each(this.elements, function(idx, element){
            element.toFront();
    });
}
/** Register hover events handler with all children **/
ChibiJS.ShinChan.Group.prototype.hover = function(f_in, f_out){ 
    $.each(this.elements, function(idx, element){
            element.hover(f_in, f_out);
    });
}
/** Register unclick event handler with all children **/
ChibiJS.ShinChan.Group.prototype.unclick = function(handler){ 
    $.each(this.elements, function(idx, element){
            element.unclick(handler);
    });
}
/** Hide all children from canvas **/
ChibiJS.ShinChan.Group.prototype.hide = function(handler){ 
    $.each(this.elements, function(idx, element){
            element.hide(handler);
    });
}
/** Show all children from canvas **/
ChibiJS.ShinChan.Group.prototype.show = function(handler){ 
    $.each(this.elements, function(idx, element){
            element.show(handler);
    });
}

/**
 * Layer object, to represent a layer on canvas.
 * A layer only contains 1 group and can be accessed by calling method layer.getMainGroup()
 **/
ChibiJS.ShinChan.Layer = function(paper, canvas, layerName){
    var paper = paper;
    var canvas = canvas;
    var id = ChibiJS.IDGenerator.generate();
    this.name = (layerName == undefined) ? id : layerName;
    var mainGroup = new ChibiJS.ShinChan.Group(this, "LayerMainGroup-" + this.name);
    
    /**
     * Return a Shape object wraps the given shape_object
     **/
    this.add = function(shape_object, name){
        var _elem = new ChibiJS.ShinChan.Shape(shape_object, this.getMainGroup(), name);
        mainGroup.add(_elem);
        return _elem;
    }
    
    this.group = function(elements, name){
        $.each(elements, function(idx, elem){
            if(mainGroup.indexOf(elem) == -1){
                return false; // Element doesn't exist in the mainGroup
            }
        });
        // Add all of them to a new group & remove them from main group of this layer
        _newGroup = new ChibiJS.ShinChan.Group(this.getMainGroup(), name);
        $.each(elements, function(idx, elem){
            elem.setParent(_newGroup);
            mainGroup.remove(elem);
            _newGroup.add(elem);
        });
        
        // Add the new group to the main group
        mainGroup.add(_newGroup);
        return _newGroup;
    }
    
    this.remove = function(element){
        mainGroup.deleteElement(element);
    }
    
    /**
     * Move the whole layer
     **/
    this.translate = function(x,y){
        mainGroup.translate(x,y);
    }

    /**
     * Draw a path, then return a Shape object
     **/
    this.draw_path = function(path, name){
        if(typeof path === "object" && typeof path.str === "function"){
            _path = paper.path(path.str());
        }
        else{
            _path = paper.path(path);
        }
        
        return this.add(_path, name);
    }
    
    this.getCanvas = function(){
        return canvas;
    }
    
    this.getPaper = function(){
        return paper;
    }
    
    this.getMainGroup = function(){
        return mainGroup;
    }
    
    this.str = function(){
        return "Layer[id=" + id + "]" + ((this.name != id) ? " [name=" + this.name + "]" : "");
    }
}

/**
 * A Raphael-based canvas. Can contain many layers.
 **/
ChibiJS.ShinChan.Canvas = function(holder_name, width, height, canvasName){
    var id = ChibiJS.IDGenerator.generate();
    this.name = (canvasName == undefined) ? holder_name : canvasName;
    var width = (width == undefined) ? 320 : width; // Default canvas width
    var height = (height == undefined) ? 240 : height; // Default canvas height
    var paper = Raphael(holder_name, width, height);
    var border = undefined;
    this.holder_name = holder_name;
    
    this.layers = [];
    
    function draw_border(){
        if(border != undefined){
            border.remove();
        }
        border = paper.rect(1,1, paper.width - 2, paper.height -2, 2);
        border.attr({"stroke" : "black" 
                ,"stroke-width" : "1px"
                , "fill" : "none"
                //,"fill" : "#FFFFFF"
                });
    }
    
    this.resize = function(new_width, new_height){
        if(width == new_width && height == new_height){
            return false;
        }
        else{
            paper.setSize(new_width, new_height);
            width = new_width;
            height = new_height;
            $.each(this.layers, function(idx, layer){
                layer.getMainGroup().findShapeInfo(true);
            });
            draw_border();
            return true;
        }
    };
    
    this.findShapeInfo = function(){
        if(this.layers.length == 0){ return; } // No element
        //this.layers[0].getMainGroup().findShapeInfo();
        var min_x = this.layers[0].getMainGroup().location.x;
        var min_y = this.layers[0].getMainGroup().location.y;
        var max_x = this.layers[0].getMainGroup().location.x 
                    + this.layers[0].getMainGroup().size.width;
        var max_y = this.layers[0].getMainGroup().location.y 
                    + this.layers[0].getMainGroup().size.height;
        
        for(var i = 1; i < this.layers.length; i++){
            layer = this.layers[i].getMainGroup();
            layer.findShapeInfo(true);
            if(layer.location) {
                //layer.findShapeInfo();
                if(layer.location.x < min_x){ min_x = layer.location.x; }
                if(layer.location.y < min_y){ min_y = layer.location.y; }
                if(layer.location.y + layer.size.height > max_y){ 
                    max_y = layer.location.y + layer.size.height; 
                }
                if(layer.location.x + layer.size.width > max_x){ 
                    max_x = layer.location.x + layer.size.width; 
                }   
            }           
        }
        
        // new size
        var size = new ChibiJS.ShinChan.Dimension(max_x - min_x, max_y - min_y);
        var location = new ChibiJS.ShinChan.Point(min_x, min_y);
        return { 'size' : size, 'location' : location };
    }
    
    this.pack = function(margin){
        if(margin == undefined){ margin = 20; } // TODO: Default margin

        var canvasInfo = this.findShapeInfo();
        var result;
        if (canvasInfo != undefined){
            result = this.resize(canvasInfo.size.width + 2 * margin, canvasInfo.size.height + 2 * margin);
            // If resize is performed
            if(result != undefined){
                // canvasInfo = this.findShapeInfo(); // update canvas info
            }
            // new size
            var shift_x = -(canvasInfo.location.x) + margin;
            var shift_y = -(canvasInfo.location.y) + margin;

            if(shift_x != 0 || shift_y != 0){
                $.each(this.layers, function(idx, layer){
                    //layer.getMainGroup().findShapeInfo(true); 
                    layer.translate(shift_x, shift_y);
                    //layer.getMainGroup().findShapeInfo(true);
                });
            } // end if shift's needed
        }   
    }
    
    this.addLayer = function(name){
        _layer = new Layer(paper, this, name);
        this.layers.push(_layer);
        return _layer;
    }
    
    this.clear = function(){
        $(this.getLayers()).each(function(idx, layer){
            // Delete layer's children
            layer.getMainGroup().deleteChildren();
            });
        // clear all layers
        this.layers = [];
    }
    
    this.getLayers = function(){
        return this.layers;
    }
    
    this.str = function(){
        return "Canvas [id=" + id + "]"  + ((this.name != id) ? " [name=" + this.name + "]" : "");
    }
    
    // Draw border after constructed
    draw_border();
}

ChibiJS.ShinChan.VerticalFlow = function(layer, elements){
    this.elements = (elements == undefined) ? [] : elements;
    this.layer = layer;
}

ChibiJS.ShinChan.VerticalFlow.prototype = {
    addElement : function(element){
        if(ChibiJS.ShinChan.CanvasUtil.isElement(element)){
            this.elements.push(element);
        }
    }
    
    ,rearrange : function(space){
        if(!space) { space = 5; }
        if(this.elements.length < 2){ return; }
        for(var i = 1; i < this.elements.length; i++){
            this_element = this.elements[i];
            prev_element = this.elements[i-1];
            if(ChibiJS.ShinChan.CanvasUtil.isElement(this_element) 
            && ChibiJS.ShinChan.CanvasUtil.isElement(prev_element)){
                ChibiJS.ShinChan.CanvasUtil.moveDown(prev_element, this_element, space);
            }
        }
    }
    
    ,getElements : function(){
        return this.elements;
    }
    
    ,str : function(){
        return "A vertical flow contains " + this.elements.length + " elements";
    }
}

ChibiJS.ShinChan.HorizontalFlow = function(layer, elements){
    this.elements = (elements == undefined) ? [] : elements;
    this.layer = layer;
}

ChibiJS.ShinChan.HorizontalFlow.prototype = {
    addElement : function(element){
        if(ChibiJS.ShinChan.CanvasUtil.isElement(element)){
            this.elements.push(element);
        }
    }
    
    ,rearrange : function(space){
        if(!space) { space = 5; }
        if(this.elements.length < 2){ return; }
        for(var i = 1; i < this.elements.length; i++){
            prev_element = this.elements[i-1];
            if(this.elements[i].location.y == prev_element.location.y){
                ChibiJS.ShinChan.CanvasUtil.moveNextTo(prev_element, this.elements[i], space);
            }
        }
    }
    
    ,getElements : function(){
        return this.elements;
    }
}
 
//
// Canvas Utilities
//

ChibiJS.Geometry = new function(){
    this.distance = function(p1, p2){
        if(!p1 || !p2){ return undefined; }
        else{
            return Math.sqrt( Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2) );
        }
    }
    
    this.rotate = function(deg, p, centre){
        if(!deg || !p){ return false; }
        else{
            deg = Math.PI * (deg / 180); // to radian
            cos_t = Math.cos(deg);
            sin_t = Math.sin(deg);
            new_x = cos_t * (p.x - centre.x) - sin_t * (p.y - centre.y) + centre.x;
            new_y = sin_t * (p.x - centre.x) + cos_t * (p.y - centre.y) + centre.y;
            return new ChibiJS.ShinChan.Point(new_x, new_y);
        }
    }
}

ChibiJS.ShinChan.CanvasUtil = new function(){
    
    this.alignTop = function(groups){
        if(groups.length <= 1){
            return; // No need to align
        }
        baseGroup = groups[0];
        for(var i = 1; i < groups.length; i++){
            shift_y = groups[0].location.y - groups[i].location.y;
            groups[i].translate(0, shift_y);
        }
    }
    //
    this.alignLeft = function(groups){
        if(groups.length <= 1){
            return; // No need to align
        }
        baseGroup = groups[0];
        for(var i = 1; i < groups.length; i++){
            shift_x = groups[0].location.x - groups[i].location.x;
            groups[i].translate(shift_x, 0);
        }
    }
    
    this.alignCentre = function(groups){
        if(groups == undefined || groups.length <= 1){
            return; // No need to align
        }
        baseGroup = groups[0];
        for(var i = 1; i < groups.length; i++){
            shift_x = groups[0].centre.x - groups[i].centre.x;
            groups[i].translate(shift_x, 0);
        }

    }
    
    /**
     * Move [shapeBelow] to beneath of shapeAbove, align left
     **/
    this.moveDown = function(shapeAbove, shapeBelow, space){
        if(this.isElement(shapeAbove) && this.isElement(shapeBelow)){
            shapeBelow.moveTo(shapeAbove.location.x, shapeAbove.location.y + shapeAbove.size.height + space);       
        }
    }
    
    /**
     * Move [nextShape] to the right of [shape]
     **/
    this.moveNextTo = function(shape, nextShape, space){
        nextShape.moveTo(shape.location.x + shape.size.width + space, shape.location.y);
    }
        
    this.isColor = function(color){
        //TODO: Check color code here
        return true;
    }

    this.sign = function(num){
        return (num > 0) ? 1 : ((num < 0) ? -1 : 0);
    }

    this.isElement = function(element){
            return (element != undefined) && (typeof element.moveTo === "function")
            && (element.size) && (element.location) && (element.centre);
    }

    this.validateBBox = function(obj, location, size){
        var _bbox = obj.getBBox();
        if (_bbox == undefined){ return false; }
        else{
            var result = true;
            if(location){
                result = result && (_bbox.x == location.x);
                result = result && (_bbox.y == location.y);
            }
            if(size){
                result = result && (_bbox.width  == size.width );
                result = result && (_bbox.height == size.height);
            }
            if(location && size){
                result = result && (_bbox.x2 == location.x + size.width);
                result = result && (_bbox.y2 == location.y + size.height);
            }
            return result;
        }
    }
}

ChibiJS.ShinChan.Path = function(){
    this.step = "";
    
    this.str = function(){
        return this.step;
    }
}

ChibiJS.ShinChan.Path.prototype = {

    moveTo : function(x,y){
        this.step += "M" + x + "," + y;
        return this;
    }
    
    ,lineTo : function(x,y){
        this.step += "L" + x + "," + y;
        return this;
    }
    
    ,append : function(anotherPath){
        if(!anotherPath){
            return this;
        }
        else if(anotherPath.str){
            this.step += anotherPath.str();
        }
        else{
            this.step += anotherPath;
        }
        return this;
    }
    
    ,drawTo : function(layer, name){
        return layer.draw_path(this.str(), name);
    }
}

//
// Shinchan extensions
//

/* Use short names if possible */
if(typeof Point === "undefined"){
    var Point = ChibiJS.ShinChan.Point;
    var Dimension = ChibiJS.ShinChan.Dimension;
    var Group = ChibiJS.ShinChan.Group;
    var Shape = ChibiJS.ShinChan.Shape;
    var Layer = ChibiJS.ShinChan.Layer;
    var Canvas = ChibiJS.ShinChan.Canvas;
    var CanvasUtil = ChibiJS.ShinChan.CanvasUtil;
    var Path = ChibiJS.ShinChan.Path;
    var HorizontalFlow = ChibiJS.ShinChan.HorizontalFlow;
    var VerticalFlow = ChibiJS.ShinChan.VerticalFlow;
}

//
// Extend Shape features

/**
 * Set fill color of current shape
 * @return Current shape for chaining
 **/
ChibiJS.ShinChan.Shape.prototype.fill = function(color){
    this.getObject().attr('fill', color);
    return this;
}

/**
 * Bring current shape to front
 **/
ChibiJS.ShinChan.Shape.prototype.toFront = function(){
    this.getObject().toFront();
    return this;
}

/**
 * Send current shape to back
 **/
ChibiJS.ShinChan.Shape.prototype.toBack = function(){
    this.getObject().toBack();
    return this;
}

/**
 * Set fill color of current shape
 * @return Current shape for chaining
 **/
ChibiJS.ShinChan.Shape.prototype.stroke = function(stroke_dasharray){
    this.getObject().attr('stroke-dasharray', stroke_dasharray);
    return this;
}

/**
 * Rotate by degree (e.g. 0-360) around a point (x,y)
 * @return Current shape for chaining
 **/
ChibiJS.ShinChan.Shape.prototype.rotate = function(deg, x, y){
    this.getObject().transform("r" + deg + "," + x + "," + y);
    this.findShapeInfo();
    return this;
}

/**
 * Set object attributes
 * @return Current shape for chaining
 **/
ChibiJS.ShinChan.Shape.prototype.attr = function(attr_map){
    this.getObject().attr(attr_map);
    this.findShapeInfo();
    return this;
}


//
// Extend Layer features
//

/**
 * Draw a line
 **/
ChibiJS.ShinChan.Layer.prototype.draw_line = function(from_x, from_y,to_x,to_y, name){
    return this.draw_path("M" + from_x + "," + from_y + "L" + to_x + "," + to_y, name);
}

/** 
 * Draw a circle
 * x: centre's x-axis
 * y: centre's y-axis
 * radius
 * name: Shape's name (can be ignored)
 * @return: A Shape object
 **/
ChibiJS.ShinChan.Layer.prototype.draw_circle = function(x, y, radius, name){
    var paper = this.getPaper();
    c = paper.circle(x, y, radius);
    c.attr('fill', 'red');
    return this.add(c, name);
}

/**
 * Draw a circle
 * x: top-left point x-axis
 * y: top-left point y-axis
 * width
 * height
 * name: Shape's name (can be ignored)
 * @return: A Shape object
 **/
ChibiJS.ShinChan.Layer.prototype.draw_rect = function(x, y, width, height, name){
    var paper = this.getPaper();
    r = paper.rect(x, y, width, height);
    this.fixBBox(r, x+width/2, y+height/2);
    return this.add(r, name);
}

/**
 * Draw a link
 **/
ChibiJS.ShinChan.Layer.prototype.draw_link = function(from_x, from_y, to_x, to_y, name){
    return this.draw_path("M" + from_x + "," + from_y + "L" + from_x + "," + to_y + "L" + to_x + "," + to_y + "L" + to_x + "," + from_y, name);
}

/**
 * Fix BBox problem in Raphael 2.1.0
 **/
ChibiJS.ShinChan.Layer.prototype.fixBBox = function(a_shape, centre_x, centre_y){
    var a_shape_bbox = a_shape.getBBox();
    var actual_centre_x = a_shape_bbox.x + a_shape_bbox.width  / 2;
    var actual_centre_y = a_shape_bbox.y + a_shape_bbox.height / 2;
    if(actual_centre_x != centre_x || actual_centre_y != centre_y){
        // work-around for bbox problem
        var shift_x = centre_x - actual_centre_x;
        var shift_y = centre_y - actual_centre_y;
        a_shape.transform("...T" + shift_x + "," + shift_y);
        return this.fixBBox(a_shape, centre_x, centre_y);
    }
    return a_shape; 
}

/**
 * Draw a text object
 **/
ChibiJS.ShinChan.Layer.prototype.draw_text = function(x, y, text, name){
    var paper = this.getPaper();
    
    var raf_text = paper.text(x, y, text);
    this.fixBBox(raf_text, x, y);
    // Adjust font
    raf_text.attr({
                'font-family': 'Courier New", Courier, monospace, "Nimbus Mono L"'
                ,'font-size': 12
                ,'text-anchor': 'center'
                ,'fill' : 'red'
    });
    var a_text_shape = this.add(raf_text, name + "_text");
    a_text_shape.findShapeInfo();
    a_text_shape.text = text;
    return a_text_shape;
}
    
/**
 * Draw a label wrapped within a box
 * x, y: Coordinates of the centre point of the label 
 * (translate size / 2 after drawing if (x, y) is top-left point)
 * shape_type: 'rounded', 'diagonals', 'rect'
 * @return: A group which the first element is the box object
 * the second element is text object
 **/
ChibiJS.ShinChan.Layer.prototype.draw_label = function(x, y, text, padding_x, padding_y, name, min_width, shape_type, corner){
    var paper = this.getPaper();
    var corner = (corner != undefined) ? corner : 5;
    var padding_x = (padding_x != undefined) ? padding_x : 2;
    var padding_y = (padding_y != undefined) ? padding_y : 2;
    var min_width = (min_width != undefined) ? min_width : 2;
    var shape_type = (shape_type != undefined) ? shape_type : "rounded";
    
    // First, draw text
    var a_text = paper.text(x, y, text);
    // Adjust font
    a_text.attr({'font-family': '"Courier New", Courier, "Nimbus Mono L", monospace;'
                ,'text-anchor': 'center'
                ,'font-size': '14px'
                ,'fill' : 'white' //text's colour
                ,'white-space':'pre'
    });
    var bbox = a_text.getBBox();
    // Adjust box's width and height to cover the text
    var node_width = bbox.width + padding_x;// + corner * 2;
    if(node_width < min_width){
        node_width = min_width;
    }
    var node_height = bbox.height + padding_y;// + corner * 2;
    var node_x = x - node_width / 2;
    var node_y = y - node_height / 2;
    
    // Now draw the border
    var a_box;
    switch(shape_type){
        case "rounded":{
            a_box = paper.rect(node_x, node_y, node_width, node_height, corner);
            a_box.attr({"fill" : "#0066CC"
                        ,"stroke" : "black"
                        ,"stroke-width" : "1px"});
            break;
        }
        
        case 'hexagon':{
            shape_path = (new ChibiJS.ShinChan.Path())
                            .moveTo(node_x - corner, node_y + node_height / 2)
                            .lineTo(node_x, node_y)
                            .lineTo(node_x + node_width, node_y)
                            .lineTo(node_x + node_width + corner, node_y + node_height / 2)
                            .lineTo(node_x + node_width, node_y + node_height)
                            .lineTo(node_x, node_y + node_height)
                            .lineTo(node_x - corner, node_y + node_height / 2)
                            ;
            
            a_box = paper.path(shape_path.str());
            a_box.attr({"fill" : "#0066CC"
                        ,"stroke" : "black"
                        ,"stroke-width" : "1px"});
            break;          
        }
        
        case "diagonals":{
            diagonal_path = (new ChibiJS.ShinChan.Path())
                            .moveTo(node_x+corner, node_y)
                            .lineTo(node_x+node_width-corner, node_y)
                            .lineTo(node_x+node_width, node_y+corner)
                            .lineTo(node_x+node_width, node_y+node_height-corner)
                            .lineTo(node_x+node_width-corner, node_y+node_height)
                            .lineTo(node_x+corner, node_y+node_height)
                            .lineTo(node_x, node_y+node_height-corner)
                            .lineTo(node_x, node_y+corner)
                            .lineTo(node_x+corner, node_y);
            
            a_box = paper.path(diagonal_path.str());
            a_box.attr({"fill" : "#0066CC"
                        ,"stroke" : "black"
                        ,"stroke-width" : "1px"});
            break;
        }
        case "rect":{
            a_box = paper.rect(node_x, node_y, node_width, node_height, 0);
            a_box.attr({"fill" : "#0066CC"
                        ,"stroke" : "black"
                        ,"stroke-width" : "1px"});
            break;
        }
        case 'parallelogram':{
            shape_path = (new ChibiJS.ShinChan.Path())
                            .moveTo(node_x+corner, node_y)
                            .lineTo(node_x+corner+node_width, node_y)
                            .lineTo(node_x+node_width,node_y+node_height)
                            .lineTo(node_x, node_y+node_height)
                            .lineTo(node_x+corner, node_y);
            a_box = paper.path(shape_path.str());
            a_box.attr({"fill" : "#0066CC"
                        ,"stroke" : "black"
                        ,"stroke-width" : "1px"});
            break;
        }
        default:{
            a_box = paper.rect(node_x, node_y, node_width, node_height, corner);
            a_box.attr({"fill" : "#0066CC"
                        ,"stroke" : "black"
                        ,"stroke-width" : "1px"});
            break;
        }
    }
    
    a_box = this.add(a_box, name + "_box");
    a_text = this.add(a_text, name + "_text");
    a_text.toFront();
    a_text.text = text;
    _group = this.group([a_box, a_text], name);
    _group.text = text;
    return _group;
}

/**
 * Build an arrow path
 * @return: Return a ChibiJS.ShinChan.Path object
 **/
ChibiJS.ShinChan.Layer.prototype.build_arrow = function(from_x, from_y, to_x, to_y, arrow_head_length, arrow_head_angle){
        if(!arrow_head_length){ arrow_head_length = 10; }
        if(!arrow_head_angle){ arrow_head_angle = 12; }
        if(from_x == to_x){
            delta_x = 0;
            delta_y = arrow_head_length;
        }
        else{
            slope = (from_y - to_y) / (from_x - to_x);
            delta_x = arrow_head_length / Math.sqrt(1 + Math.pow(slope,2));
            delta_y = Math.abs(slope * delta_x);
        }
        
        head_tail_x = ChibiJS.ShinChan.CanvasUtil.sign(from_x - to_x) * delta_x + to_x;
        head_tail_y = ChibiJS.ShinChan.CanvasUtil.sign(from_y - to_y) * delta_y + to_y;
        
        head_root = new ChibiJS.ShinChan.Point(head_tail_x, head_tail_y);
        arrow_head = new ChibiJS.ShinChan.Point(to_x, to_y);
        head_left = ChibiJS.Geometry.rotate(-arrow_head_angle, head_root, arrow_head);
        head_right = ChibiJS.Geometry.rotate(arrow_head_angle, head_root, arrow_head);
        /*
        aline = this.draw_circle(from_x, from_y, 5, "arrow_from").fill("none");
        aline = this.draw_circle(to_x, to_y, 5, "arrow_to").fill("cyan");
        aline = this.draw_circle(head_tail_x, head_tail_y, 5, "arrow_head").fill("none");
        */
        // Draw arrow to this layer
        return new ChibiJS.ShinChan.Path().moveTo(from_x, from_y).lineTo(to_x, to_y)
                    .lineTo(head_left.x, head_left.y).moveTo(to_x, to_y).lineTo(head_right.x, head_right.y);
}

/**
 * Draw arrow
 **/
ChibiJS.ShinChan.Layer.prototype.draw_arrow = function(from_x, from_y, to_x, to_y, name, arrow_head_length, arrow_head_angle){
    return this.build_arrow(from_x, from_y, to_x, to_y, arrow_head_length, arrow_head_angle).drawTo(this, name);
}

/**
 * Draw an u-shape link
 *    ---------
 *    |       |
 *    |       V
 *  [=x=]   [=y=]
 **/
ChibiJS.ShinChan.Layer.prototype.draw_link_u = function(from_x, from_y, to_x, to_y, name, arrow_head_length, arrow_head_angle){
    path = new ChibiJS.ShinChan.Path().moveTo(from_x, from_y).lineTo(from_x, to_y)
                .lineTo(to_x, to_y)
                .append(
                    this.build_arrow(to_x, to_y, to_x, from_y, arrow_head_length, arrow_head_angle)
                );
    return path.drawTo(this, name);
}

function gotourl(event){
     console.writeline(event.data.url); 
};

ChibiJS.ShinChan.Layer.prototype.draw_table = function(x, y, table_data, name, padding){
    if(!table_data || table_data.length == 0){ return undefined; }
    if(!padding){ padding = 5; }
    
    var visual_table = new ChibiJS.Table();
    var table_data = table_data;
    // Render cell text
    for(var row_id = 0; row_id < table_data.length; row_id++){
        for(var col_id = 0; col_id < table_data[row_id].length; col_id++){
            cell_data = table_data[row_id][col_id];
            cell_url = undefined;
            var cell_text = undefined;
            if ((cell_data.url == undefined) || (cell_data.text == undefined)){
                cell_text = new String(cell_data);
            }
            else{
                cell_text = cell_data.text();
                cell_url = cell_data.url();
            }
            // Draw this cell text to table
            var visual_cell = this.draw_text(0, 0, cell_text, cell_text);//, cell_text);
            visual_cell.text = cell_text;
            visual_cell.url = cell_url;
            visual_table.setCell(row_id, col_id, visual_cell);
            visual_table.expandColumnWidth(col_id, visual_cell.size.width);
            visual_table.expandRowHeight(row_id, visual_cell.size.height);
            
            // make links clickable
            if (typeof cell_url == 'string'){
                visual_cell.click(function(url){ return function(){ window.open(url, '_blank');} }(cell_url));
            }
            else if(typeof cell_url == 'function'){
                visual_cell.click(cell_url);
            }
        }       
    }
    // Draw text to correct location
    var table_x = x + padding; var table_y = y + padding; //top-left position of the table
    for(var row_id = 0; row_id < table_data.length; row_id++){
        for(var col_id = 0; col_id < table_data[row_id].length; col_id++){
            var visual_cell = visual_table.getCell(row_id, col_id);
            visual_cell.moveTo(table_x, table_y);
            table_x += visual_table.getColumnWidth(col_id) + padding * 2;
        }
        table_x = x + padding;
        table_y += visual_table.getRowHeight(row_id) + padding * 2;
    }
    
    var table_text = this.group(visual_table.getAllCells(), name + "_table_text");

    var w = 0; var h = 0;
    for(var i = 0; i < visual_table.row_height.length; i++){
        h += visual_table.row_height[i] + padding * 2;
    }
    for(var i = 0; i < visual_table.column_width.length; i++){
        w += visual_table.column_width[i] + padding * 2;
    }
    var table_bound = this.draw_rect(x,y,w,h, name + "_bound").attr({'stroke' : 'black', 'fill' : '#BBBBBB'});  

    if(visual_table.columnCount() > 1 || visual_table.rowCount() > 1){
        var lines = new ChibiJS.ShinChan.Path(); 
        
        var current_x = x; var current_y = y;
        for(var i = 0; i < visual_table.column_width.length - 1; i++){
            current_x += visual_table.getColumnWidth(i) + padding * 2; 
            lines.moveTo(current_x, y)
            .lineTo(current_x, y + table_bound.size.height);
        }
        for(var j = 0; j < visual_table.row_height.length - 1; j++){
            current_y += visual_table.getRowHeight(j) + padding * 2;
            lines.moveTo(x , current_y)
            .lineTo(x + table_bound.size.width, current_y);
        }
        var table_lines = lines.drawTo(this, name + "_table_lines");
        table_border = this.group([table_bound, table_lines], name + "_table_border");
    }
    else{
        table_border = table_bound;
    }
    
    var _table_group = this.group([table_border, table_text], name);
    table_text.toFront();
    _table_group.bound = table_bound;
    _table_group.text = table_text;
    
    return _table_group;
}
