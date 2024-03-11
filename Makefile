
SHELL := /bin/bash
PYTHON := python
CONAN := conan
CONAN_HOME := $(shell pwd)/.conan2
# execute all lines of a target in one shell
.ONESHELL:

.PHONY: all
all: build

.PHONY: build
build:
	@if [ "$$VIRTUAL_ENV" == "" ] ; then
	    echo "creating python virtual environment in ./venv"
	    ${PYTHON} -m venv venv
	    source venv/bin/activate
	    pip install -r requirements.txt
	fi
	export CONAN_HOME="${CONAN_HOME}"  # copy from make env to bash env
	${CONAN} config install conan-config
	${CONAN} remote enable conancenter
	[ ! -e ".conan2/profiles/default" ] && ${CONAN} profile detect
	(cd conan_lbstanza_generator && ${CONAN} create .)

	 # get the current project name from the slm.toml file
	SLMPROJNAME=$$(sed -n -e '/^ *name *= *"*\([^"]*\).*/{s//\1/;p;q}' slm.toml)
	SLMPROJVER=$$(sed -n -e '/^ *version *= *"*\([^"]*\).*/{s//\1/;p;q}' slm.toml)

	 # build slm and link to dependency libs using stanza.proj fragments
	 # build only the current project, not any dependencies
	echo "building \"$${SLMPROJNAME}/$${SLMPROJVER}\""
	${CONAN} create \
	    -vtrace \
	    --build "$${SLMPROJNAME}/$${SLMPROJVER}" .

.PHONY: upload
upload:
	@if [ "$$VIRTUAL_ENV" == "" ] ; then
	    echo "using python virtual environment in ./venv"
	    source venv/bin/activate
	fi
	export CONAN_HOME="${CONAN_HOME}"  # copy from make env to bash env
	${CONAN} remote enable artifactory
	 # expects user in CONAN_LOGIN_USERNAME_ARTIFACTORY and password in CONAN_PASSWORD_ARTIFACTORY
	${CONAN} remote login artifactory

	 # get the current project name from the slm.toml file
	SLMPROJNAME=$$(sed -n -e '/^ *name *= *"*\([^"]*\).*/{s//\1/;p;q}' slm.toml)
	SLMPROJVER=$$(sed -n -e '/^ *version *= *"*\([^"]*\).*/{s//\1/;p;q}' slm.toml)

	${CONAN} upload -r artifactory $${SLMPROJNAME}/$${SLMPROJVER}

.PHONY: clean
clean:
	rm -rf .conan2 .slm build build_slm venv
