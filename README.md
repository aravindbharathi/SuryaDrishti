# SuryaDrishti

_SuryaDrishti_ is a standalone web-based application using _Python_ and _Angular_ to identify X-ray bursts and categorise them based on peak energy flux and temperature given long-duration X-ray light curve. Parameters like rise and decay time have also been derived and false positives have been kept to the minimum. It is primarily being developed to browse _XSM_ observations and visualise solar flares to facilitate research based on _XSM_ data but the target audience also includes the larger astronomy community.

_SuryaDrishti_ provides utilities to:

- Visualise and analyse light curve data in the X-ray regime
- Identify solar flares and fit them to a curve
- Summarise properties such as the duration of the burst, the peak photon count, etc.

Possible use-case scenarios:

- Study X-ray bursts from XSM data
- Aid in establishing a relationship (or the lack thereof) between solar flares and coronal mass ejections
- Combine with spectroscopy data to comprehensively analyse solar bursts
- Have fun finding patterns in the data using the visualisation tool (assumes no pre-requisites)

## Installation Procedure for SuryaDrishti

### Dependencies

SuryaDrishti depends on npm, node.js and Python3.8

npm and node.js can be installed with -

```
$ sudo apt -y install curl;
$ curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -;
$ sudo apt -y install nodejs;
```

### Run the backend

```
$ cd backend/;
$ pip install -r ../requirements.txt;
$ uvicorn server:app;
```

### Run the frontend

```
$ cd frontend/;
$ npm i;
$ npm start;
```

### Accessing the interface

You can simply go to either of the following addresses in your browser to access the interface -

```
localhost:4200
```

## Documentation

Documentation is present in the ```Docs/``` folder and the home page is ```Docs/Documentation.html```.
