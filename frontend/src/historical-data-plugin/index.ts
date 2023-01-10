/**
 * Basic historical data plugin modified from the OpenMCT historical telemetry plugin.
*/

import axios from "axios";

const openmct = require("openmct/dist/openmct.js");

function HistoricalDataPlugin() {
    return function install (openmct: any) {

        var provider = {
            supportsRequest: (domainObject : any) => {
                return domainObject.type === 'plot.data' || domainObject.type === "image.data";
            },
            request: (domainObject: any, options: any) => {
                return axios.get('sidecar/?'+ new URLSearchParams({field: domainObject.identifier.key}))
                .then((result) => {
                    // console.log(result.data)
                    return result.data;
                })
                .catch(console.error);
            }
        };
        openmct.telemetry.addProvider(provider);
    }
}

export {
    HistoricalDataPlugin
}
