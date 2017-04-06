'use strict';

var Plotly = window.Plotly = require('plotly.js');
var gd = window.gd = document.createElement('div');
document.body.appendChild(gd);

fetch('./assets/airfoil.json', function (resp) {
  resp.json().then(function (mock) {
    window.mock = mock;
    Plotly.plot(gd, mock)
  });
});
