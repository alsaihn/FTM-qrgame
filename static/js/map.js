
var map = L.map('map', {crs: L.CRS.Simple, attributionControl: false});
/* Instead of a tile layer, use a bitmap image */
var imageUrl = 'media/FtMMapFinal.jpg';
var scale = 9000 / 250;
var imageBounds = [[0.0 , 9000/scale], [6594/scale, 0.0]];
L.imageOverlay(imageUrl, imageBounds, {noWrap:true, maxZoom:3, minZoom:0}).addTo(map);
map.setView(new L.LatLng(94.5, 126.5), 1);

L.geoJson(geojson, {
	pointToLayer: function (feature, latlng) {
				return L.circleMarker(latlng, {
					radius: 8,
					fillColor: "#ff7800",
					color: "#000",
					weight: 1,
					opacity: 1,
					fillOpacity: 0.8
				});
	}
}).addTo(map);
