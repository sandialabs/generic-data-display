const openmct = require("openmct/dist/openmct.js");

function hasImage(domainObject: any): boolean {
    const metadata = openmct.telemetry.getMetadata(domainObject);
    if (!metadata) return false;

    return metadata.valuesForHints(['image']).length > 0;
}

const ImageStreamPlugin = () => {
    return (openmct: any) => {
        openmct.objectViews.addProvider({
            name: "Image Stream",
            description: "A simple viewer for streaming images",
            key: "imagestream",

            canView: hasImage,

            view: (domainObject: any) => {
                const metadata = openmct.telemetry.getMetadata(domainObject);
                const imageHints = { ...metadata.valuesForHints(['image'])[0] };
                const formatter = openmct.telemetry.getValueFormatter(imageHints);

                let image = new Image(500, 500);

                let unsubscribe = openmct.telemetry.subscribe(domainObject, (datum: any) => {
                    image.src = formatter.format(datum);
                });

                return {
                    show: (element: Element) => {
                        element.appendChild(image);
                    },
                    destroy: () => {
                        image.parentElement.removeChild(image);
                        unsubscribe();
                    }
                }
            }
        });
    }
}

export {
    ImageStreamPlugin
}