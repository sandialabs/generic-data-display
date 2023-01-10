import _ from 'lodash';
const openmct = require("openmct/dist/openmct.js");

require("openmct/dist/espressoTheme.css");

import {GenericDataPlugin} from './generic-data-plugin/';
import {ImageStreamPlugin} from './image-stream-plugin/';
import {HistoricalDataPlugin} from './historical-data-plugin/';

function configureOpenMCT() {
    openmct.setAssetPath("node_modules/openmct/dist");
    openmct.install(openmct.plugins.Espresso());
    openmct.install(openmct.plugins.LocalStorage());
    openmct.install(openmct.plugins.MyItems());

    openmct.install(openmct.plugins.UTCTimeSystem());
    openmct.time.clock('local', {start: -15 * 60 * 1000, end: 0});
    openmct.time.timeSystem('utc');

    openmct.install(GenericDataPlugin());
    openmct.install(ImageStreamPlugin());
    openmct.install(HistoricalDataPlugin());

    openmct.start();

    console.log("Welcome To Generic Data Display!")
}

configureOpenMCT();