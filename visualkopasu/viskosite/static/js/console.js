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
 
 /**
  * Just a simple console to throw debug info in
  **/
function Console(id){
    this.holder = $('#'+id);
    this.color = "lightgreen";
    this.holder.css({
    "color" : "lightgreen"
    ,"background-color" : "black"
    ,"font-family" : "monospace, 'Courier New'"
    ,"font-size" : '12px'
        ,"padding": '5px'
    });
    var mode = true;
    
    this.setEnable = function(_mode){
    mode = _mode;
    };
    
    this.setColor = function(color){
    if(!mode){ return; }
    this.color = color;
    return this;
    }
    
    this.write = function(text, color){
    if(!mode){ return; }
    
    if(text == undefined){ text = ''; }
    if(color == undefined) { color = this.color; }
    if(typeof text.str === "function"){ 
        text = text.str(); 
    }
    
    if(color != undefined){
        // this.holder.add('span').css('color', color);
        this.holder.append("<span style='color:" + color + "'>" + text + "</span>");
    }
    else{
        this.holder.append("<span>" + text + "</span>");
    }
    return this;
    }
    
    this.writeline = function(text, color){
    if(!mode){ return; }
    this.write(text, color);
    this.holder.append("</br>");
    return this;
    };
    
    this.header = function(text){
    if(!mode){ return; }
    header_color = "yellow";
    var hr_line = ''
    for(i = 0; i < text.length + 4; i++){
        hr_line += '='
    }
    
    this.writeline("");
    this.writeline(hr_line, header_color);
    this.writeline("| " + text + " |", header_color);
    this.writeline(hr_line, header_color);
    this.writeline("");
    
    return this;
    };
    
    this.exec = function(command, prefix){
    if(!mode){ return; }
        
    var result = '';
    if (typeof prefix == 'string') {
        result += prefix;
    }
    result += command + " -> " + eval(command);
    this.writeline(result);
    
    return this;
    };
    
    this.clear = function(initialText){
    if(!mode){ return; }
    if(initialText == undefined) {
        this.holder.html('<br/>');
    }
    else{
        this.holder.html('');
        this.writeline(initialText);
    }
    
    return this;
    };
}

/**
 * Dump an object to a string
 **/
function dump_object(obj){
    if(typeof obj === "undefined"){
    return "NULL";
    }
    else if(typeof obj.str === "function"){
    return obj.str();
    }
    else{
    return obj;
    }
}

/**
 * Dump an array to a string
 * @return String
 **/
function dump_array(a_list){
    if(a_list == undefined){
    return "NULL";
    }
    if(a_list.length == 0){
    return "[]";
    }
    
    str = '';
    a_new_list = []
    $(a_list).each(function(){
    a_new_list.push("'" + dump_object(this) + "'");
    });
    return "[ " + a_new_list.join(", ") + " ]"
}

/**
 * Dump a dictionary to a string
 * @return String
 **/
function dump_dict(a_dict){
    if(a_dict == undefined){
    return "NULL";
    }
    if(a_dict.length == 0){
    return "[]";
    }
    
    str = '';
    a_new_list = []
    $.each(a_dict, function(key, value){
    a_new_list.push("'" + key + "' : '" + dump_object(value) +"'");
    });
    return "[ " + a_new_list.join(", ") + " ]"
}
