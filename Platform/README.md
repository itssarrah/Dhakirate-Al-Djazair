# Installation :

Note : The front end and backend have to run together to work properly.

To use this front end for Dhakirate-Al-Djazair, you need to install the latest NodeJs and npm. to ensure that nodejs is on the latest version, you should uninstall the current version and install the latest one. To do so, you can use the following commands:

## On Windows: using Choco 
this is the official documentation from nodejs.org

```bash
# Download and install Chocolatey:
powershell -c "irm https://community.chocolatey.org/install.ps1|iex"

# Download and install Node.js:
choco install nodejs-lts --version="23"

# Verify the Node.js version:
node -v # Should print "v23.6.0".

# Verify npm version:
npm -v # Should print "10.9.2".
```

## On Linux: using NVM
this is the official documentation from nodejs.org

```bash
# Download and install nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

```
**Then you should close the terminal and open a new one to use nvm**

```bash
# Download and install Node.js:
nvm install 23

# Verify the Node.js version:
node -v # Should print "v23.6.0".
nvm current # Should print "v23.6.0".

# Verify npm version:
npm -v # Should print "10.9.2".
```

## Next steps after installing NodeJs or upgrading the version to latest :


### in the front end directory, you run:

```bash
npm install
```

**this generally yields errors depending on the version of nodejs and npm you have, if it does not succeed you should try : 

```bash
npm install --legacy-peer-deps
```

***And*** 

```bash
npm install --force
```

**until the front end runs successfully with :**

```bash
npm start
```

**which will start the front end on localhost:3000**