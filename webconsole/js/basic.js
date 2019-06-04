var browserType = getBrowser();

function scrollToTop() {
    window.scroll(0, 0);
}

//parse parameters within the url to an object
function parseUrlParam(url) {
    if (!url) return new Object();
    var str = url;
    var res = new Object();
    if (str && str.indexOf('?') > 0) {
        str = str.substr(str.indexOf('?') + 1);
        var arr = str.split('&');
        for (var i = 0; i < arr.length; i++) {
            var subarr = arr[i].split('=');
            if (subarr.length == 2) {
                res[subarr[0]] = subarr[1];
            }
        }
    }
    return res;
}

function GetXmlHttpObject() {
    try {
        if (window.ActiveXObject) {
            xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
        } else if (window.XMLHttpRequest) {
            xmlHttp = new XMLHttpRequest();
        }
    } catch (err) {
        return null;
    }
    return xmlHttp;
}

function BrowserType(btype) {
    this.type = btype;
    this.isIE = function () {
        return this.type.toLowerCase() == 'ie';
    }
    this.isChrome = function () {
        return this.type.toLowerCase() == 'chrome';
    }
    this.isFirefox = function () {
        return this.type.toLowerCase() == 'firefox';
    }
    this.isOpera = function () {
        return this.type.toLowerCase() == 'opera';
    }
    this.isSafari = function () {
        return this.type.toLowerCase() == 'safari';
    }
}

function getBrowser() {
    var userAgent = navigator.userAgent; // 取得浏览器的userAgent字符串
    var isOpera = userAgent.indexOf("Opera") > -1;
    if (isOpera) {
        return new BrowserType("Opera");
    }
    ; // 判断是否Opera浏览器
    if (userAgent.indexOf("Firefox") > -1) {
        return new BrowserType("Firefox");
    } // 判断是否Firefox浏览器
    if (userAgent.indexOf("Chrome") > -1) {
        return new BrowserType("Chrome");
    }
    if (userAgent.indexOf("Safari") > -1) {
        return new BrowserType("Safari");
    } // 判断是否Safari浏览器
    if (userAgent.indexOf("compatible") > -1 && userAgent.indexOf("MSIE") > -1 && !isOpera) {
        return new BrowserType("IE");
    }
    ; // 判断是否IE浏览器
}

// 对Date的扩展，将 Date 转化为指定格式的String
// 月(M)、日(d)、小时(h)、分(m)、秒(s)、季度(q) 可以用 1-2 个占位符，
// 年(y)可以用 1-4 个占位符，毫秒(S)只能用 1 个占位符(是 1-3 位的数字)
// 例子：
// (new Date()).Format("yyyy-MM-dd hh:mm:ss.S") ==> 2006-07-02 08:09:04.423
// (new Date()).Format("yyyy-M-d h:m:s.S") ==> 2006-7-2 8:9:4.18
Date.prototype.Format = function (fmt) { // author: meizz
    var o = {
        "M+": this.getMonth() + 1,
        // 月份
        "d+": this.getDate(),
        // 日
        "h+": this.getHours(),
        // 小时
        "m+": this.getMinutes(),
        // 分
        "s+": this.getSeconds(),
        // 秒
        "q+": Math.floor((this.getMonth() + 3) / 3),
        // 季度
        "S": this.getMilliseconds()
        // 毫秒
    };
    if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o) if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
}

//将秒数转为为timespan的字符数, 例如70秒转换为00:01:10
function sec2span(secstr) {
    if (!secstr)
        return '';
    var secs = parseInt(secstr);
    var h = parseInt(secs / 3600);
    secs -= h * 3600;
    var m = parseInt(secs / 60);
    secs -= h * 60;
    var s = secs;
    var res = (h < 10 ? '0' + h : '' + h) + ':';
    res += (m < 10 ? '0' + m : '' + m) + ':';
    res += (s < 10 ? '0' + s : '' + s);
    return res;
}

//将00:01:10这样的字符串转为秒数
function span2sec(spanstr) {
    if (!spanstr)
        return 0;
    var arr = spanstr.split(':');
    var h = parseInt(arr[0]);
    var m = parseInt(arr[1]);
    var s = parseInt(arr[2]);
    return 3600 * h + 60 * m + s;
}

function spanCheckValid(spanstr) {
    var arr = "0123456789:";
    for (var i = 0; i < spanstr.length; i++) {
        var char = spanstr.charAt(i);
        if (arr.indexOf(char) < 0)
            return false;
    }
    return true;
}

//将date转为为yyyy-MM-dd-HH-mm-ss格式
function date2str(d) {
    if (!d) {
        return '';
    }
    return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate() + '-'
        + d.getHours() + '-' + d.getMinutes() + '-' + d.getSeconds();
}

//将date转为为yyyy-MM-dd HH:mm:ss格式
function date2str2(d) {
    if (!d) {
        return '';
    }
    return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate() + ' '
        + d.getHours() + ':' + d.getMinutes() + ':' + d.getSeconds();
}

function randInt(n) {
    var r = Math.random();
    for (var i = 0; i < n; i++) r *= 10;
    return parseInt(r);
}

function isString(obj){
    return obj && (typeof obj == 'string') && obj.constructor == String;
}


function uuid(len, radix) {
    var chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.split('');
    var uuid = [], i;
    if (!len) len = 8;
    if (!radix) radix = 16;
    radix = radix || chars.length;

    if (len) {
        // Compact form
        for (i = 0; i < len; i++) uuid[i] = chars[0 | Math.random() * radix];
    } else {
        // rfc4122, version 4 form
        var r;

        // rfc4122 requires these characters
        uuid[8] = uuid[13] = uuid[18] = uuid[23] = '-';
        uuid[14] = '4';

        // Fill in random data.  At i==19 set the high bits of clock sequence as
        // per rfc4122, sec. 4.1.5
        for (i = 0; i < 36; i++) {
            if (!uuid[i]) {
                r = 0 | Math.random() * 16;
                uuid[i] = chars[(i == 19) ? (r & 0x3) | 0x8 : r];
            }
        }
    }

    return uuid.join('');
}


var DATE_FMT = "yyyy-MM-dd hh:mm:ss";
// 对Date的扩展，将 Date 转化为指定格式的String
// 月(M)、日(d)、小时(h)、分(m)、秒(s)、季度(q) 可以用 1-2 个占位符，
// 年(y)可以用 1-4 个占位符，毫秒(S)只能用 1 个占位符(是 1-3 位的数字)
// 例子：
// (new Date()).Format("yyyy-MM-dd hh:mm:ss.S") ==> 2006-07-02 08:09:04.423
// (new Date()).Format("yyyy-M-d h:m:s.S")      ==> 2006-7-2 8:9:4.18
Date.prototype.format = function(fmt)
{ //author: meizz
    var o = {
        "M+" : this.getMonth()+1,                 //月份
        "d+" : this.getDate(),                    //日
        "h+" : this.getHours(),                   //小时
        "m+" : this.getMinutes(),                 //分
        "s+" : this.getSeconds(),                 //秒
        "q+" : Math.floor((this.getMonth()+3)/3), //季度
        "S"  : this.getMilliseconds()             //毫秒
    };
    if(/(y+)/.test(fmt))
        fmt=fmt.replace(RegExp.$1, (this.getFullYear()+"").substr(4 - RegExp.$1.length));
    for(var k in o)
        if(new RegExp("("+ k +")").test(fmt))
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length==1) ? (o[k]) : (("00"+ o[k]).substr((""+ o[k]).length)));
    return fmt;
}


String.prototype.trim=function(){
    return this.replace(/(^\s*)|(\s*$)/g, "");
}
String.prototype.ltrim=function(){
    return this.replace(/(^\s*)/g,"");
}
String.prototype.rtrim=function(){
    return this.replace(/(\s*$)/g,"");
}
String.prototype.endWith=function(str){
    if(str==null||str==""||this.length==0||str.length>this.length)
        return false;
    if(this.substring(this.length-str.length)==str)
        return true;
    else
        return false;
    return true;
}
String.prototype.startWith=function(str){
    if(str==null||str==""||this.length==0||str.length>this.length)
        return false;
    if(this.substr(0,str.length)==str)
        return true;
    else
        return false;
    return true;
}
