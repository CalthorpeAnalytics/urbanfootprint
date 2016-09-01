if (!org) var org = {};
if (!org.leaflet) org.leaflet = {};

(function(po) {
  po.mcmap = function() {
    var mcmap = po.map();

    function mcmapmove() {
        if (!mcmap) return;
        mcmap.savestate();
    }

    mcmap.loadstate = function (clon, clat, czoom) {
        var value = getCookie('mapstate'),
            centerlon = clon,
            centerlat = clat,
            centerzoom = czoom;
        if (value) {
            var tokens = value.split('|');
            centerlon  = parseFloat(tokens[0]);
            centerlat  = parseFloat(tokens[1]);
            centerzoom = parseInt(tokens[2]);
        }
        mcmap.center({lon: centerlon, lat: centerlat})
             .zoom(centerzoom);
        return mcmap;
    }

    mcmap.savestate = function () {
        setCookie('mapstate', mcmap.center().lon + '|' + 
                              mcmap.center().lat + '|' + 
                              mcmap.zoom());
    }

    mcmap
        .on("move", mcmapmove)
        .loadstate(0, 0, 3);

    return mcmap;
  };
})(org.leaflet);


(function(po) {
  po.legend = function(map) {
    var legend = {};

    legend.container = function (elt) {
        console.log("legend " + elt);
        return legend;
    }

    return legend;
  };
})(org.leaflet);


(function(po) {
  po.switcher = function(m, l, o) {
    var self = {},
        map,
        layers,
        current,
        options;

    map = m;
    layers = l;
    options = o ? o : {};
    if (!options.title) options.title = 'Base Layer';

    /* switch to layer */
    self.switchto = function (name) {
        var l = layers[name];
        if (l.map()) {
            l.visible(true);
        }
        else {
            map.add(l);
        }
        if (current) {
            current.visible(false);            
        }
        current = l;
    }

    self.container = function (elt) {
        // Create Legend manipulating the DOM
        var main = elt;
        var list = document.createElement('div');
        list.setAttribute('id', 'switcher-list');
        // For each layer, create a <input> 
        for (name in layers) {
            var layerid = layers[name].id();
            var input = document.createElement('input');
            input.setAttribute('id', 'switcher-' + layerid);
            input.setAttribute('name', 'switcher-radio');
            input.setAttribute('type', 'radio');
            input.setAttribute('value', name);
            if (layers[name].map()) input.setAttribute('checked', '');
            
            // Link onChange event on radio
            input.onchange = function () { 
                self.switchto(this.getAttribute('value')); 
            };
            var label = document.createElement('label');
            label.setAttribute('for', 'switcher-' + layerid);
            label.innerHTML = name;
            
            var item = document.createElement('div');
            item.appendChild(input);
            item.appendChild(label);
            list.appendChild(item);
        }
        var title = document.createElement('div');
        title.setAttribute('id', 'switcher-title');
        title.innerHTML = options.title;
        main.appendChild(title);
        main.appendChild(list);
        return self;
    }

    return self;
  };
})(org.leaflet);



(function(po) {
  po.toggler = function(m, l, o) {
    var self = {},
        map,
        layers,
        inputs,
        options;

    map = m;
    layers = l;
    options = o ? o : {};
    if (!options.title) options.title = 'Vector Layers';

    /* toggle layer */
    self.toggle = function (name) {
        var l = layers[name];
        if (!l.map()) {
            map.add(l);
            l.visible(true);
        }
        else {
            var visible = l.visible();
            l.visible(!visible);
        }
        if (l && l.visible()) inputs[name].setAttribute('checked', '');
    }

    self.container = function (elt) {
        // Create Legend manipulating the DOM
        var main = elt;
        var list = document.createElement('div');
        list.setAttribute('id', 'togglelayer-list');
        // For each layer, create a <input>
        inputs = $.mapObjectToObject(layers, function(name) {
            var layerid = layers[name].id();
            var input = document.createElement('input');
            input.setAttribute('id', 'togglelayer-' + layerid);
            input.setAttribute('name', 'togglelayer');
            input.setAttribute('type', 'checkbox');
            input.setAttribute('value', name);
            if (layers[name].map() && layers[name].visible()) input.setAttribute('checked', '');

            // Link onChange event on checkbox
            input.onchange = function () {
                self.toggle(this.getAttribute('value'));
            };
            var label = document.createElement('label');
            label.setAttribute('for', 'togglelayer-' + layerid);
            label.innerHTML = name;

            var item = document.createElement('div');
            item.appendChild(input);
            item.appendChild(label);
            list.appendChild(item);
            return [name, input];
        });
        var title = document.createElement('div');
        title.setAttribute('id', 'togglelayer-title');
        title.innerHTML = options.title;
        main.appendChild(title);
        main.appendChild(list);
        return self;
    }

    return self;
  };
})(org.leaflet);


(function(po) {
  po.checkbrowser = function(eltid) {

    function isBrowserCompatible() {
        ev = getInternetExplorerVersion();
        cv = getChromeVersion();
        fv = getFirefoxVersion();
        sv = getSafariVersion();
        ov = getOperaVersion();
        return ((ev >= 9) || (cv >= 5) || (sv >= 3) || (fv >= 3) || (ov >= 11));
    }

    if (isBrowserCompatible()) {
        hide(eltid);
    }
  };
})(org.leaflet);


function hide(eltid){
    document.getElementById(eltid).style.display='none';
}

/*
 * 
 * Browsers Versions Detection
 * 
 */
function getInternetExplorerVersion() {
    //Returns the version of Internet Explorer or a -1
    //(indicating the use of another browser).
    var rv = -1; // Return value assumes failure.
    if (navigator.appName == 'Microsoft Internet Explorer')
    {
        var ua = navigator.userAgent;
        var re  = new RegExp("MSIE ([0-9]{1,}[\.0-9]{0,})");
        if (re.exec(ua) != null)
            rv = parseFloat( RegExp.$1 );
    }
    return rv;
}
function getFirefoxVersion() {
    var rv = -1;
    var ua = navigator.userAgent;
    var re  = new RegExp("Firefox\\/([0-9]{1,}[\.0-9]{0,})");
    if (re.exec(ua) != null)
        rv = parseFloat( RegExp.$1 );
    return rv;
}
function getChromeVersion() {
    var rv = -1;
    var ua = navigator.userAgent;
    var re  = new RegExp("Chrome\\/([0-9]{1,}[\.0-9]{0,})");
    if (re.exec(ua) != null)
        rv = parseFloat( RegExp.$1 );
    return rv;
}
function getSafariVersion() {
    var rv = -1;
    var ua = navigator.userAgent;
    var re  = new RegExp(".*AppleWebKit.*Version\\/([0-9]{1,}[\.0-9]{0,})");
    if (re.exec(ua) != null)
        rv = parseFloat( RegExp.$1 );
    return rv;
}
function getOperaVersion() {
    var rv = -1;
    var ua = navigator.userAgent;
    var re  = new RegExp("Opera.*Presto.*Version\\/([0-9]{1,}[\.0-9]{0,})");
    if (re.exec(ua) != null)
        rv = parseFloat( RegExp.$1 );
    return rv;
}

/*
 * 
 * Cookies Handling
 * 
 */
function getCookie( name ) {
    var start = document.cookie.indexOf( name + "=" );
    var len = start + name.length + 1;
    if ( ( !start ) && ( name != document.cookie.substring( 0, name.length ) ) ) {
        return null;
    }
    if ( start == -1 ) return null;
    var end = document.cookie.indexOf( ';', len );
    if ( end == -1 ) end = document.cookie.length;
    return unescape( document.cookie.substring( len, end ) );
}

function setCookie( name, value, expires, path, domain, secure ) {
    var today = new Date();
    today.setTime( today.getTime() );
    if ( expires ) {
        expires = expires * 1000 * 60 * 60 * 24;
    }
    var expires_date = new Date( today.getTime() + (expires) );
    document.cookie = name+'='+escape( value ) +
        ( ( expires ) ? ';expires='+expires_date.toGMTString() : '' ) + //expires.toGMTString()
        ( ( path ) ? ';path=' + path : '' ) +
        ( ( domain ) ? ';domain=' + domain : '' ) +
        ( ( secure ) ? ';secure' : '' );
}

function deleteCookie( name, path, domain ) {
    if ( getCookie( name ) ) document.cookie = name + '=' +
            ( ( path ) ? ';path=' + path : '') +
            ( ( domain ) ? ';domain=' + domain : '' ) +
            ';expires=Thu, 01-Jan-1970 00:00:01 GMT';
}
