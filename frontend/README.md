# 📈 Generic Data Display UI

This is the frontend web application to connect to the generic data display server. 
It built on top of [OpenMCT](https://github.com/nasa/openmct), Typescript, and webpack. 
It uses npm to build, configure, and install the runtime environment.

## Install NPM
To install NPM, follow the instructions provided here: https://nodejs.org/en/download/

## Working in a Proxy Environment
To install npm packages in a proxy working environment, certain updates need to be made to allow connections/downloads to work correctly.
- Ensure that `http_proxy` and `https_proxy` are set to `[proxy_url]` in your development environment
- Ensure you have a path set locally to the repo's [pem_file](docker/placeholder_certificate.pem) file
- Set the npm config cafile to work with certificates to allow intallations with npm:
  - npm config set cafile /path/to/certificate.pem
  - /etc/ssl/certs/ca-certificates.cr
  - certificates.pem

## 🛠️ Building 
- `npm install`
- `npm run build`

## ▶️ Running
To run the development server, we use webpack's [DevServer](https://webpack.js.org/configuration/dev-server/).
By default the dev server proxy connects to `http://localhost:8844` at `/api` for http server info and `ws://localhost:8844/live` for websocket connection info.
If using different ports/host endpoints make sure that the backend aoi http server setup matches what is expected via the webpack server deployment.
- `npm run start` Server will be running on http://localhost:8080 and will connect to the backend at http://localhost:8844

## Auditing NPM/JavaScript Dependencies
To audit the NPM dependencies, run the following command from the `ui/` directory:
- `npm audit report`

This will display a listing of vulnerable NPM packages. There are two ways to fix these vulnerabilities:
1. Run the `npm audit fix` command to resolve vulnerabilities that do not involve breaking changes.
2. Run the `npm audit fix --force` command to resolve all vulnerabilities including those that produce breaking changes.

These commands will update the `package.json` and `package-lock.json` files, as well as the contents of the `ui/node_modules/` directory.

