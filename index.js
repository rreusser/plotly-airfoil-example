var Plotly = require('plotly.js');
var h = require('h');
var gd = require('gd');
var mock = JSON.parse(fs.readFileSync('./airfoil.json', 'utf8'));

Plotly.plot(
