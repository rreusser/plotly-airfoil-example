#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.3f')
import numpy as np

def sanitize1d(data):
  return map(lambda x: 'null' if np.isnan(x) else x, data.tolist())

alpharange = (10.0 * np.sin(np.pi * 0.5 * np.linspace(-1, 1, 41))).tolist()
#alpharange = range(-10, 11, 1)
alpha0 = 10

def makedata (alphadeg):
  # Input parameters:
  mu = -0.08 + 0.08j
  n = 1.94
  vinf = 1.0
  alpha = alphadeg * np.pi / 180.0
  rot = np.exp(-1.0j * alpha)

  # Grid layout:
  r0 = np.abs(1.0 - mu)
  r = np.linspace(r0, 5, 31)
  th = np.linspace(0, np.pi * 2, 71)
  rr, thth = np.meshgrid(r, th)
  zeta = rr * np.exp(1.0j * thth)

  # Potential and stream function:
  circ = 2.0j * vinf * r0 * np.sin(alpha + np.arcsin(np.imag(mu) / r0))
  wt = vinf * (rot - (r0 / zeta)**2.0 / rot) + circ / zeta
  F = vinf * (zeta * rot + r0**2 / zeta / rot) + circ * np.log(zeta)

  # Karman-Trefftz transformation:
  k1 = (1.0 + 1.0 / (mu + zeta))**n
  k2 = (1.0 - 1.0 / (mu + zeta))**n
  z = n * (k1 + k2) / (k1 - k2) * rot
  dzdzeta = 4.0 * n * n / ((mu + zeta)**2.0 - 1.0) * k1 * k2 / (k1 - k2)**2.0

  # Pressure coefficient:
  cp = 1.0 - (np.abs(wt / dzdzeta) / vinf)**2

  # Extract the inner boundary:
  xy = z[:-1, 0]
  normal = np.exp(0.5j * np.pi) * (np.roll(xy, 1) - np.roll(xy, -1))
  normal /= np.abs(normal)
  offset = 7.0
  cpoffset = normal * 0.1 * (offset + cp[:-1, 0])

  surfacepressurefill = np.r_[xy + cpoffset, [np.NaN], xy[::-1]]

  pressurelines = []
  for i in range(1, xy.shape[0], 3):
    pressurelines.extend([xy[i], xy[i] + cpoffset[i], np.NaN])

  return [
    dict(
      type='carpet',
      a=r.tolist(),
      b=th.tolist(),
      x=np.real(z).tolist(),
      y=np.imag(z).tolist(),
      aaxis=dict(
        showgrid=False,
        startline=True,
        startlinewidth=2,
        endlinewidth=2,
        endline=True,
        showticklabels='none',
        smoothing=0,
      ),
      baxis=dict(
        showticklabels='none',
        startline=False,
        endline=False,
        showgrid=False,
        smoothing=0,
      )
    ),
    dict(
      type='contourcarpet',
      name='Pressure',
      z=cp.tolist(),
      autocontour=False,
      autocolorscale=False,
      contours=dict(
        showlines=False,
        start=-1,
        end=1.0,
        size=0.025
      ),
      colorscale='Viridis',
      colorbar=dict(
        len=0.65,
        y=0,
        yanchor='bottom',
        title='Pressure coefficient, c<sub>p</sub>',
        titleside='right'
      ),
      line=dict(
        smoothing=0
      ),
      zauto=False,
      zmin=-8,
      zmax=1,
    ),
    dict(
      type='contourcarpet',
      name='Streamlines',
      showlegend=True,
      z=np.imag(F).tolist(),
      autocontour=True,
      ncontours=50,
      opacity=0.3,
      contours=dict(
        coloring='none'
      ),
      line=dict(
        width=1,
        color='white'
      )
    ),
    dict(
      type='contourcarpet',
      name='Pressure<br>contours',
      showlegend=True,
      z=cp.tolist(),
      autocontour=False,
      contours=dict(
        showlines=True,
        coloring='none',
        start=-4,
        end=1.0,
        size=0.25,
      ),
      line=dict(
        color='rgba(0, 0, 0, 0.5)',
        smoothing=1,
      ),
    ),
    dict(
      type='scatter',
      name='Surface<br>pressure',
      mode='lines',
      legendgroup='g1',
      x=sanitize1d(np.real(surfacepressurefill)),
      y=sanitize1d(np.imag(surfacepressurefill)),
      hoverinfo='skip',
      line=dict(
        shape='spline',
        smoothing=1,
        width=1,
        color='rgba(255, 0, 0, 0.5)'
      ),
      fill='toself',
      fillcolor='rgba(255, 0, 0, 0.2)'
    ),
    dict(
      type='scatter',
      mode='lines',
      legendgroup='g1',
      showlegend=False,
      x=sanitize1d(np.real(pressurelines)),
      y=sanitize1d(np.imag(pressurelines)),
      hoverinfo='skip',
      line=dict(
        width=1,
        color='rgba(255, 0, 0, 0.3)'
      ),
    ),
    dict(
      type='scatter',
      name='cp',
      mode='lines',
      text=map(lambda x: "c<sub>p</sub> = %.2g" % x, cp[:, 0].tolist()),
      legendgroup='g1',
      showlegend=False,
      hoverinfo='text',
      x=sanitize1d(np.real(xy + cpoffset)),
      y=sanitize1d(np.imag(xy + cpoffset)),
      line=dict(
        width=0,
        color='rgba(255, 0, 0, 0.2)'
      ),
    ),
  ]

f = open('assets/airfoil.json', 'w')
json.dump(dict(
  data=makedata(alpha0),
  layout=dict(
    title=u"Flow over a Karman-Trefftz airfoil",
    width=900,
    height=700,
    margin=dict(t=80, r=60, b=40, l=40),
    hovermode='closest',
    xaxis=dict(
      showgrid=False,
      zeroline=False,
      range=[-3.8, 3.8],
      scaleanchor='y',
      scaleratio=1
    ),
    yaxis=dict(
      showgrid=False,
      zeroline=False,
      range=[-1.8, 1.8]
    ),
    dragmode='pan',
    updatemenus=[dict(
      type='buttons',
      direction='right',
      xanchor='left',
      yanchor='top',
      pad=dict(t=50),
      showactive=False,
      y=0,
      x=0,
      buttons=[dict(
        label='Play',
        method='animate',
        args=[None, dict(
          transition=dict(duration=0),
          frame=dict(duration=800),
          mode='immediate',
        )]
      ), dict(
        label='Pause',
        method='animate',
        args=[[None], dict(
          mode='immediate',
        )]
      )]
    )],
    sliders=[dict(
      transition=dict(
        duration=0
      ),
      active=alpharange.index(alpha0),
      currentvalue=dict(
        prefix=u'Angle of attack, α = ',
        xanchor='right',
      ),
      pad=dict(l=130),
      steps=map(lambda alpha: dict(
        label='%g°' % alpha,
        method='animate',
        args=[
          ['alpha%g' % alpha],
          dict(
            frame=dict(duration=1000),
            transition=dict(duration=0),
            mode='immediate',
          )
        ]
      ), alpharange)

    )]
  ),
  frames=map(lambda alpha: dict(
    name='alpha%g' % alpha,
    data=makedata(alpha),
  ), alpharange),
  config=dict(
    scrollZoom=True
  )
), f)
f.close();
