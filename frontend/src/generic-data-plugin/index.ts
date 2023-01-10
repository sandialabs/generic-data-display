import axios from 'axios';

function getDictionary() {
    return axios.get('api/config')
        .then((result) => {
            return result.data;
        });
}

function getNamespaces() : any {
    const Http = new XMLHttpRequest();
    const url='sidecar/namespaces';
    Http.open("GET", url, false);
    Http.send(null);
    return JSON.parse(Http.responseText)
}

const objectProvider = {
    get: (identifier: any) => {
        return getDictionary().then((dictionary) => {
            var measurement = dictionary.measurements.find((m: any) => m.key === identifier.key)
            measurement.identifier = identifier;
            return measurement;
        });
    }
};

const compositionProvider = {
    appliesTo: (object: any) => {
        var namespaces = getNamespaces()
        return namespaces.includes(object.identifier.namespace) && object.composition !== undefined
    },
    load: (model: any) => {
        var id = model.identifier
        return getDictionary().then((dictionary) => {
            return dictionary.measurements.find((measurement: any) => {
                return measurement.key === id.key
            }).composition.map((identifier: any) => {
                return identifier
            });
        });
    }
};

const GenericDataPlugin = () => {
    return (openmct: any) => {

        var namespaces = getNamespaces()

        for(let i = 0; i < namespaces.length; i++){
            var namespace = namespaces[i]
            openmct.objects.addRoot({
                namespace: namespace,
                key: namespace
            });

            openmct.objects.addProvider(namespace, objectProvider);
        };

        openmct.composition.addProvider(compositionProvider);

        openmct.types.addType('plot.data', {
            name: 'Generic Telemetry Point',
            description: 'A generic telemetry point',
            cssClass: 'icon-telemetry'
        });
        openmct.types.addType('image.data', {
            key: 'image.data',
            name: 'Generic Image Display',
            description: 'A way to display image data',
            cssClass: 'icon-image',
            createable: true
        });

        // realtime provider
        var socket = new WebSocket(location.origin.replace(/^http/, 'ws') + '/live');
        var listener : any = {};

        socket.onmessage = (event) => {
            let point = JSON.parse(event.data);
            if (listener[point.topic]) {
                listener[point.topic](point);
            }
        };

        var generic_telemetry_provider = {
            supportsSubscribe: (domainObject : any) => {
                return domainObject.type === 'plot.data' || domainObject.type === 'image.data';
            },
            subscribe: (domainObject : any, callback : any) => {
                listener[domainObject.identifier.key] = callback;

                let msg = {cmd: 'subscribe', topic: domainObject.identifier.key};
                console.debug('subscribing to ' + domainObject.identifier.key);
                socket.send(JSON.stringify(msg));
                return function unsubscribe() {
                    delete listener[domainObject.identifier.key];
                    let umsg = {cmd: 'unsubscribe', topic: domainObject.identifier.key};

                    console.debug('unsubscribing from ' + domainObject.identifier.key);
                    socket.send(JSON.stringify(umsg));
                };
            }
        };
        openmct.telemetry.addProvider(generic_telemetry_provider);
    };
};

/**
 * Basic Realtime telemetry plugin using websockets.
 */
export {
    GenericDataPlugin
}