/*
*  Leaflet.wfst.js a WFS-T plugin for Leaflet.js
*  (c) 2013, Michael Moore
*
* Many thanks to georepublic.info for enough info to get up and running: http://blog.georepublic.info/2012/leaflet-example-with-wfs-t/
*/

L.WFST = L.GeoJSON.extend({
    // These functions overload the parent (GeoJSON) functions with some WFS-T
    // operations and then call the parent functions to do the Leaflet stuff
    initialize: function(geojson, options) {
        // These come from OL demo: http://openlayers.org/dev/examples/wfs-protocol-transactions.js
        var initOptions = L.extend({
            version: "1.0.0",           // WFS version 
            failure: function(msg) {
            }			
			// Function for handling initialization failures
            // geomField : <field_name> // The geometry field to use. Auto-detected if only one geom field 
            // url: <WFS service URL> 
            // featureNS: <Feature NameSpace>
            // featureType: <Feature Type>
            // primaryKeyField: <The Primary Key field for using when doing deletes and updates>
        }, options);

        this.self = this;


        if (typeof initOptions.url == 'undefined') {
            throw "ERROR: No WFST url declared";
        }
        if (typeof initOptions.featureNS == 'undefined') {
            throw "ERROR: featureNS not declared";
        }
        if (typeof initOptions.featureType == 'undefined') {
            throw "ERROR: featureType not declared";
        }

        initOptions.typename = initOptions.featureNS + ':' + initOptions.featureType;

        // Call to parent initialize
        L.GeoJSON.prototype.initialize.call(this, geojson, initOptions);

        // Now probably an ajax call to get existing features
        if (this.options.showExisting) {
            if (typeof this.options.featureId !== 'undefined') {
                this._loadExistingFeatureFromId();
            } else {
                this._loadExistingFeatures();
            }
        }
        this._loadFeatureDescription();
    },
    // Additional functionality for these functions
    addLayer: function(layer, options) {

        this.wfstAdd(layer, options);

        // Call to parent addLayer
        L.GeoJSON.prototype.addLayer.call(this, layer);
    },
    removeLayer: function(layer, options) {
        this.wfstRemove(layer, options);
        // Call to parent removeLayer
        L.GeoJSON.prototype.removeLayer.call(this, layer);
    },

    // These functions are unique to WFST
    // WFST Public functions

    /* 
    Save changes to one or more layers which we may or may not already have
    layer : a single layer or array of layers. Possibly an empty array
    */
    wfstAdd: function(layers, options) {
        options = options || {};
        layers = layers ? (L.Util.isArray(layers) ? layers : [layers]) : [];

        for (var i = 0, len = layers.length; i < len; i++) {
            this._wfstAdd(layers[i], options);
        }
    },
    wfstRemove: function(layers, options) {
        options = options || {};
        layers = layers ? (L.Util.isArray(layers) ? layers : [layers]) : [];

        for (var i = 0, len = layers.length; i < len; i++) {
            this._wfstRemove(layers[i], options);
        }
    },
    wfstSave: function(layers, options) {
        options = options || {};
        layers = layers ? (L.Util.isArray(layers) ? layers : [layers]) : [];

        var v;
        for (var i = 0, len = layers.length; i < len; i++) {
            if (typeof layers[i]._layers == 'object') {
                for (v in layers[i]._layers) {
                    this._wfstSave(layers[i]._layers[v], options);
                }
				//this._wfstSave(layers[i], options);
            } else {
                this._wfstSave(layers[i], options);
            }
        }
    },
    wfstTouch: function(layers, options) {
        // Touch a file so it needs to be saved again
        layers = layers ? (L.Util.isArray(layers) ? layers : [layers]) : [];
        console.log("Save layers now!");

        for (var i = 0, len = layers.length; i < len; i++) {
            layers[i].properties._wfstSaved = false;
        }
    },
    wfstSaveDirty: function() {
        for (var i = 0, len = layers.length; i < len; i++) {
            if (layers[i].properties._wfstSaved === false) {
                this.wfstSave(layers[i]);
            }
        }
    },

    // WFST Private functions

    // Interesting / real functions
    // Add a single layer with WFS-T
    _wfstAdd: function(layer, options) {
        if (typeof layer.feature != 'undefined' &&
            typeof layer.feature._wfstSaved == 'boolean' &&
            layer.feature._wfstSaved) {
            layer.feature = layer.feature || {};
            layer.feature.properties = layer.feature.properties || {};
            layer.feature.properties[this.options.primaryKeyField] = layer.feature.id || {};
            return true; // already saved
        }


		var realsuccess;
		var realfailure;
        if (typeof this.self.options.onSuccess == 'function') {
            realsuccess = this.self.options.onSuccess;
        }
        if (typeof this.self.options.failure == 'function') {
            realfailure = this.self.options.failure;
        }
		
		
        options = L.extend(options, {
            success: function(res) {
                var wfstResult = this.self._wfstSuccess(res);

                if (wfstResult) {
                    var wfstRealResult = this.self._wfstRealResult(wfstResult);

                    if (wfstRealResult) {
                        layer.feature = layer.feature || {};
                        layer.feature.properties = layer.feature.properties || {};
                        layer.feature.properties[this.self.options.primaryKeyField] = wfstRealResult[0] || {};
                        layer.feature._wfstSaved = true;
						
		                if (typeof realsuccess == 'function') {
							realsuccess('Objektet blev indsat');
						}
						
                    } else if (typeof realfailure == 'function') {
                        realfailure(res);
                    }
                } else if (typeof realfailure == 'function') {
                    realfailure(res);
                }
            }
        });

        var xml = this.options._xmlpre;

        xml += "<wfs:Insert>";
        xml += "<" + this.options.typename + ">";
        xml += this._wfstSetValues(layer);
        xml += "</" + this.options.typename + ">";
        xml += "</wfs:Insert>";
        xml += "</wfs:Transaction>";


        this._ajax(L.extend({ data: xml }, options));
    },

    // Remove a layers with WFS-T
    _wfstRemove: function(layer, options) {
        if (typeof this.options.primaryKeyField == 'undefined') {
            console.log("I can't do deletes without a primaryKeyField!");
            if (typeof options.failure == 'function') {
                options.failure();
            }
            return false;
        }

		var realsuccess;
		var realfailure;
        if (typeof this.self.options.onSuccess == 'function') {
            realsuccess = this.self.options.onSuccess;
        }
        if (typeof this.self.options.failure == 'function') {
            realfailure = this.self.options.failure;
        }

        options = L.extend(options, {
            success: function(res) {
                if (typeof realsuccess == 'function' && this.self._wfstSuccess(res)) {
                    layer.feature = layer.feature || {};
                    layer.feature._wfstSaved = true;
                    realsuccess('Objekt er slettet');
                } else if (typeof realfailure == 'function') {
                    realfailure(res);
                }
            }
        });

        var where = {};
        where[this.options.primaryKeyField] = layer.feature.id;//layer.feature.properties[this.options.primaryKeyField];

        var xml = this.options._xmlpre;
        xml += "<wfs:Delete typeName='" + this.options.typename + "'>";
        xml += this._whereFilter(where);
        xml += "</wfs:Delete>";
        xml += "</wfs:Transaction>";

        this._ajax(L.extend({ data: xml }, options));
    },


    //  Save changes to a single layer with WFS-T
    _wfstSave: function(layer, options) {

        if (typeof this.options.primaryKeyField == 'undefined') {
            console.log("I can't do saves without a primaryKeyField!");
            if (typeof options.failure == 'function') {
                options.failure();
            }
            return false;
        }

        options = options || {};

		var realsuccess;
		var realfailure;
        if (typeof this.self.options.onSuccess == 'function') {
            realsuccess = this.self.options.onSuccess;
        }
        if (typeof this.self.options.failure == 'function') {
            realfailure = this.self.options.failure;
        }

        options = L.extend(options, {
            success: function(res) {
                if (typeof realsuccess == 'function' && this.self._wfstSuccess(res)) {
                    layer.feature._wfstSaved = true;
                    realsuccess('Objektet blev gemt');
                } else if (typeof realfailure == 'function') {
                    realfailure(res);
                }
            }
        });

        var where = {};
		//Skal det ikke v�re layer.feature.Id fordi det skal v�re i det m�rkelige format.
        where[this.options.primaryKeyField] = layer.feature.id;//layer.feature.properties[this.options.primaryKeyField];

        var xml = this.options._xmlpre;
        xml += "<wfs:Update typeName='" + this.options.typename + "'>";
        xml += this._wfstUpdateValues(layer);
        xml += this._whereFilter(where);
        xml += "</wfs:Update>";
        xml += "</wfs:Transaction>";

        console.log("WfstSave");
        console.log(xml);

        this._ajax(L.extend({ data: xml }, options));
    },


    // Utility functions

    // Build the xml for setting/updating fields
	_wfstSetValues: function(layer){
        var xml = '';
        var field = this._wfstValueKeyPairs(layer);

        if(!field){
            return false;
        }
		
		if (!this.options.attributes) {
			return false;
		}
		
		//Attributv�rdier.
		for(var p = 0;p < this.options.attributes.length;p++) {
			att = this.options.attributes[p];
			if (att !== this.options.primaryKeyField) {
				var attValue = field[att];
				if (typeof attValue  != 'undefined' ) {		
					xml += "<" + this.options.featureNS + ":" + att+ ">";
					xml += attValue;
					xml += "</" + this.options.featureNS + ":" + att + ">";
				}
			}
		}

		//Geometri felt til sidst
		if (typeof field[this.options.geometryField]   != 'undefined' ) {
			xml += "<" + this.options.featureNS + ":" + this.options.geometryField+ ">";
			xml += field[this.options.geometryField];
			xml += "</" + this.options.featureNS + ":" + this.options.geometryField + ">";
		}
		
        return xml;
    },
    _wfstUpdateValues: function(layer) {
        var xml = '';
        var field = this._wfstValueKeyPairs(layer);

        if (!field) {
            return false;
        }

        for (var f in field) {
            if (f !== this.options.primaryKeyField) {
                xml += "<wfs:Property><wfs:Name>";
                xml += this.options.featureNS + ":" + f;
                xml += "</wfs:Name><wfs:Value>";
                xml += field[f];
                xml += "</wfs:Value></wfs:Property>";
            }
        }

        return xml;
    },
    _wfstValueKeyPairs: function(layer) {
        var field = {};
        var elems = this._fieldsByAttribute();
        var geomFields = [];

        for (var p = 0; p < elems.length; p++) {
            attr = elems[p].getAttribute('name');

            if (typeof layer.feature != 'undefined' &&
                typeof layer.feature.properties != 'undefined' &&
                typeof layer.feature.properties[attr] != 'undefined') {
                // Null value present, but not allowed
                if (layer.feature.properties[attr] === null && !elems[p].getAttribute('nillable')) {
                    console.log("Null value given for non nillable field: " + attr);
                    return false; // No value given for required field!
                } else if (layer.feature.properties[attr] !== null) {
                    field[attr] = layer.feature.properties[attr];
                } else {
                    // Not sure what to do with null values yet. 
                    // At the very least Geoserver isn't liking null where a date should be.
                }
            } else if (elems[p].getAttribute('type') == 'gml:GeometryPropertyType' || elems[p].getAttribute('type') == 'gml:SurfacePropertyType') {
                geomFields.push(elems[p]);
            } else if (elems[p].getAttribute('nillable') == 'false') {
                if (elems[p].getAttribute('maxOccurs') != "1" && elems[p].getAttribute('minOccurs') != "1") {
                    console.log("No value given for required field " + attr);
                    return false; // No value given for required field!
                }
            }
        }

        if (this.options.geomField || geomFields.length === 1) {
            this.options.geomFields = this.options.geomField || geomFields[0];
            field[attr] = layer.toGML();
        } else {
            console.log("No geometry field!");
            return false;
        }

        return field;
    },
    // Make WFS-T filters for deleting/updating specific items
    _whereFilter: function(where) {
        var xml = '<ogc:Filter>';
        for (var propertyName in where) {
            xml += '<ogc:FeatureId fid="' + where[propertyName] + '" />';
        }
        xml += '</ogc:Filter>';
        return xml;
    },

    /* Make an ajax request
    options: {
    url: url to fetch (required),
    method : GET, POST (optional, default is GET),
    success : function (optional), must accept a string if present
    failure: function (optional), must accept a string if present
    }
    */
    _ajax: function(options) {
        options = L.extend({
            method: 'POST',
            success: function (r) {
                console.log("AJAX Succes!");
                console.log(r);
            },
            failure: function(r) {
                console.log("AJAX Failure!");
                console.log(r);
            },
            self: this.self,
            url: this.options.url
        }, options);

        var xmlhttpreq = (window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject('Microsoft.XMLHTTP'));
        xmlhttpreq.onreadystatechange = function() {
            if (xmlhttpreq.readyState == 4) {
                if (xmlhttpreq.status == 200) {
                    //console.log("_ajax status 200 -> " + xmlhttpreq.responseText);
                    options.success(xmlhttpreq.responseText);
                } else {
                    console.log("_ajax fejl status " + xmlhttpreq.status + " -> " + xmlhttpreq.responseText);
                    options.failure(xmlhttpreq.responseText);
                }
            }
        };
        xmlhttpreq.open(options.method, options.url, true);
        xmlhttpreq.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xmlhttpreq.send(options.data);
    },

    /*
    Get existing object from the WFS service, based on feature id, and draws it
    */
    _loadExistingFeatureFromId: function () {
        var geoJsonUrl = this.options.url;

        this._xmlFeatureId();
        var xml = this.options._xmlfeatId;

        this._ajax({
            url: geoJsonUrl,
            data: xml,
            success: function (res) {
                res = this.self._parseXml(res);
                res = kiwfs2geojson.parce(res, this.self.options);
                res = JSON.parse(res);

                for (var i = 0; i < res.features.length; i++) {
                    res.features[i]._wfstSaved = true;
                }
				
				if (this.self.options.onLoadedById != null) {
					if (typeof this.self.options.onLoadedById == 'function') {			
						this.self.options.onLoadedById(res);
					}
				}

                this.self.addData(res.features);
            },
			error: function (xhr, textStatus, errorThrown) {
				if (this.self.options.onLoadedByIdError != null) {
					if (typeof this.self.options.onLoadedByIdError == 'function') {			
						this.self.options.onLoadedByIdError(textStatus, errorThrown);
					}
				}
			}
			
        });
    },
    
    /*
    Get all existing objects from the WFS service and draw them
    */
    _loadExistingFeatures: function() {
        var geoJsonUrl = this.options.url;
        
        this._xmlFeature();
        var xml = this.options._xmlfeat;
        
        this._ajax({
            url: geoJsonUrl,
            data: xml,
            success: function (res) {
                res = this.self._parseXml(res);
                res = kiwfs2geojson.parce(res, this.self.options);
                res = JSON.parse(res);
                
                for (var i = 0; i < res.features.length; i++) {
                    res.features[i]._wfstSaved = true;
                }
                
                this.self.addData(res.features);
            }
        });
    },
    /*
    Get the feature description
    */
    _loadFeatureDescription: function () {
        var geoJsonUrl = this.options.url;
        
        this._xmlFeatureDescription();
        var xml = this.options._xmlfeaturedesc;
        
        this._ajax({
            url: geoJsonUrl,
            data: xml,
            success: function(res){
                xml = this.self._wfstSuccess(res);
                if(xml !== false){
                    this.self.options.featureinfo = xml;
                    this.self._xmlPreamble();
                    this.self.ready = true;
                }else{
                    this.self.options.failure("There was an exception fetching DescribeFeatueType");
                }
            }
        });
    },
    // Deal with XML -- should probably put this into gml and do reading and writing there
    _parseXml: function (rawxml) {
        rawxml = rawxml.substr(1);
        rawxml = rawxml.substr(0, rawxml.length - 1);
        rawxml = rawxml.split("\\u000d\\u000a").join("");
        rawxml = rawxml.split("\\").join('');

        //return $.parseXML(rawxml);

        var xmlDoc;
        if (window.DOMParser)
        {
            var parser = new window.DOMParser();
            xmlDoc = parser.parseFromString(rawxml, "text/xml");
        }
        else // Internet Explorer
        {
            xmlDoc=new ActiveXObject("Microsoft.XMLDOM");
            xmlDoc.async=false;
            xmlDoc.loadXML(rawxml);
            //return xmlDoc;
        }

        return xmlDoc;

    },
    
    _xmlPreamble: function() {

        var xmlpre = '<wfs:Transaction service="WFS" version="' + this.options.version + '"'
            + ' xmlns:wfs="http://www.opengis.net/wfs"'
            + ' xmlns:gml="http://www.opengis.net/gml"'
            + ' xmlns:ugis="http://www.ugis.dk/wfs"'
            + ' xmlns:ogc="http://www.opengis.net/ogc"'
            + ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
            + ' xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.0.0/WFS-transaction.xsd"'
            + '>';

        this.options._xmlpre = xmlpre;
    },
    
    _xmlFeature: function() {
        var xmlfeature =  '  <wfs:GetFeature'
            + '  service="WFS"'
            + '  version="1.0.0"'
            + '  outputFormat="GML2"'
            + '  xmlns:wfs="http://www.opengis.net/wfs"'
            + '  xmlns:ugis="http://www.ugis.dk/wfs"'
            + '  xmlns:ogc="http://www.opengis.net/ogc"'
            + '  xmlns:gml="http://www.opengis.net/gml"'
            + '  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
            + '  xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.0.0/WFS-basic.xsd">'
            + '  <wfs:Query typeName="' + this.options.featureNS + ":" + this.options.featureType + '">'
            + '  </wfs:Query>'
            + '</wfs:GetFeature>';

        this.options._xmlfeat = xmlfeature;
    },
    
    _xmlFeatureId: function () {
        var xmlfeatureId = '  <wfs:GetFeature'
            + '  service="WFS"'
            + '  version="1.0.0"'
            + '  outputFormat="GML2"'
            + '  xmlns:wfs="http://www.opengis.net/wfs"'
            + '  xmlns:ugis="http://www.ugis.dk/wfs"'
            + '  xmlns:ogc="http://www.opengis.net/ogc"'
            + '  xmlns:gml="http://www.opengis.net/gml"'
            + '  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
            + '  xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.0.0/WFS-basic.xsd">'
            + '  <wfs:Query typeName="' + this.options.featureNS + ":" + this.options.featureType + '">'
            + '  <ogc:Filter>'
            + '  <ogc:FeatureId fid="' + this.options.featureType + "&amp;" + this.options.featureId + '"/>'
            + '  </ogc:Filter>'
            + '  </wfs:Query>'
            + '</wfs:GetFeature>';

        this.options._xmlfeatId = xmlfeatureId;
    },
    
    _xmlFeatureDescription: function () {
        var xmlfeaturedescription = '<wfs:DescribeFeatureType'
            + '  service="WFS"'
            + '  version="1.0.0"'
            + '  outputFormat="GML2"'
            + '  xmlns:wfs="http://www.opengis.net/wfs"'
            + '  xmlns:ugis="http://www.ugis.dk/wfs"'
            + '  xmlns:ogc="http://www.opengis.net/ogc"'
            + '  xmlns:gml="http://www.opengis.net/gml"'
            + '  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
            + '  xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.0.0/WFS-basic.xsd">'
            + '  <wfs:Query typeName="' + this.options.featureNS + ":" + this.options.featureType + '">'
            + '  </wfs:Query>'
            + '</wfs:DescribeFeatureType>';

        this.options._xmlfeaturedesc = xmlfeaturedescription;
    },
    

    // A compatibility layer because browsers argue about the right way to do getElementsByTagName when namespaces are involved
    _getElementsByTagName: function (xml, name) {
        var tag = xml.getElementsByTagName(name);
        if(!tag || tag.length === 0){
            tag = xml.getElementsByTagName(name.replace(/.*:/,''));
        }
        if (!tag || tag.length === 0) {
            tag = xml.getElementsByTagNameNS('', name.replace(/.*:/,''));
        }
        return tag;
    },

    _fieldsByAttribute: function (attribute, value, max) {
        var seq = this._getElementsByTagName(this.options.featureinfo, 'xsd:sequence')[0];
        if(typeof seq == 'undefined'){
            return [];
        }
        
        var elems = this._getElementsByTagName(seq,'xsd:element');
        var found = [];
        
        for(var e = 0;e < elems.length;e++){
            if (typeof attribute == 'undefined') {
                found.push(elems[e]);
            } else if (elems[e].getAttribute(attribute) == value) {
                found.push(elems[e]);
                if(typeof max == 'number' && found.length == max){
                    return found;
                }
            }
        }

        return found;
    },

    // Because with WFS-T even success can be failure
    _wfstSuccess: function(xml){
        if (typeof xml == 'string') {
            xml = this._parseXml(xml);
        }
        var exception = this._getElementsByTagName(xml, 'ows:ExceptionReport');
        if (exception.length > 0) {
            console.log(this._getElementsByTagName(xml, 'ows:ExceptionText')[0].firstChild.nodeValue);
            return false;
        }
        return xml;
    },
    

    _wfstRealResult: function(xml) {
        var success = this._getElementsByTagName(xml, 'SUCCESS')[0];

        if (typeof success == 'undefined' || success == null) {
            return false;
        }

        var elem = this._getElementsByTagName(xml, 'ogc:FeatureId')[0];
        var found = [];

        found.push(elem.getAttribute('fid'));

        return found;
    }
});

L.wfst = function(geojson,options){
    return new L.WFST(geojson,options);
};
