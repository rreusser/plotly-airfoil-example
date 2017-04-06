'use strict';

var fs = require('fs');
var Plotly = window.Plotly = require('plotly.js');
var gd = window.gd = document.createElement('div');
document.body.appendChild(gd);

var mock = window.mock = JSON.parse(fs.readFileSync(__dirname + '/../assets/airfoil.json', 'utf8'));

Plotly.plot(gd, mock)
