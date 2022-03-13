# Based on that awesome makefile https://github.com/dunglas/symfony-docker/blob/main/docs/makefile.md#the-template

# Let user override python binary, collection's namespace/name/version if needed
PYTHON?=python

COLLECTION_NAMESPACE?=$(shell $(PYTHON) -c 'import yaml;print(yaml.load(open("galaxy.yml"), yaml.SafeLoader)["namespace"])')
COLLECTION_NAME?=$(shell $(PYTHON) -c 'import yaml;print(yaml.load(open("galaxy.yml"), yaml.SafeLoader)["name"])')
COLLECTION_VERSION?=$(shell $(PYTHON) -c 'import yaml;print(yaml.load(open("galaxy.yml"), yaml.SafeLoader)["version"])')

ANSIBLE_VERSION=$(shell $(PYTHON) -c 'from ansible import __version__ ;print("%s" % ".".join( __version__.split(".")[:2]));')
# ansible-core below v2.11 doesn't support installing fom current directory if it is not under C_NAMESPACE/C_NAME directories
# Install from tar.gz instead
ifeq ($(ANSIBLE_VERSION), 2.9)
ANSIBLE_INSTALL_OLD_FASHION=1
else ifeq ($(ANSIBLE_VERSION), 2.10)
ANSIBLE_INSTALL_OLD_FASHION=1
else
ANSIBLE_INSTALL_OLD_FASHION=0
endif

BUILD_DIR?=build
ANSIBLE_COLLECTIONS_BUILD_DIR=${BUILD_DIR}/ansible_collections
COLLECTION_BUILD_DIR=${ANSIBLE_COLLECTIONS_BUILD_DIR}/${COLLECTION_NAMESPACE}/${COLLECTION_NAME}

.DEFAULT_GOAL = default

default: clean configure-dev-env

##—— 📚 Help ——————————————————————————————————————————————————————————————
.PHONY: help
help: ## ❓ Dislay this help
	@grep -E '(^[a-zA-Z0-9_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}{printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' \
		| sed -e 's/\[32m##——————————/[33m           /'  \
		| sed -e 's/\[32m##——/[33m ——/' \
		| sed -e 's/\[32m####/[34m                                 /' \
		| sed -e 's/\[32m###/[36m                                 /' \
		| sed -e 's/\[32m##/[33m/'

##—— ️⚙️  Environments ——————————————————————————————————————————————————————
.PHONY: clean
clean: ## 🧹 Clean generated contents
clean:
	rm -rf build/* tests/output .mypy_cache ${COLLECTION_NAMESPACE}-${COLLECTION_NAME}-*.tar.gz

.PHONY: configure-dev-env
configure-dev-env: ## 🤖 Install required libraries for dev environment (python libs used on codebase)
configure-dev-env:
	$(PYTHON) -m pip install --upgrade --upgrade-strategy eager -r meta/ee-requirements.txt # Install internal requirements

.PHONY: configure-test-env
configure-test-env: ## 🤖 Install required libraries for test environment (libs used on codebase, MyPy, etc)
#### Use target="..." to restrict extra galaxy requirements installation to specific target (units, integration, sanity)
configure-test-env: target ?=
configure-test-env: configure-dev-env
	$(PYTHON) -m pip install --upgrade --upgrade-strategy eager -r tests/requirements.txt # Install tests requirements
ifeq ($(shell if ([ "$(target)" = "units" ] || [ "$(target)" = "" ]) && [ -f tests/unit/requirements.yml ]; then echo 1; else echo 0; fi),1)
	$(MAKE) install install_o="-p ${ANSIBLE_COLLECTIONS_BUILD_DIR} -r tests/unit/requirements.yml" upgrade=1 source="--"
endif
ifeq ($(shell if ([ "$(target)" = "sanity" ] || [ "$(target)" = "" ]) && [ -f tests/sanity/requirements.yml ]; then echo 1; else echo 0; fi),1)
	$(MAKE) install install_o="-p ${ANSIBLE_COLLECTIONS_BUILD_DIR} -r tests/sanity/requirements.yml" upgrade=1 source="--"
endif
ifeq ($(shell if ([ "$(target)" = "integration" ] || [ "$(target)" = "" ]) && [ -f tests/integration/requirements.yml ]; then echo 1; else echo 0; fi),1)
	$(MAKE) install install_o="-p ${ANSIBLE_COLLECTIONS_BUILD_DIR} -r tests/integration/requirements.yml" upgrade=1 source="--"
endif

##—— 🇦 Ansible collection —————————————————————————————————————————————————
##—————————— \_ 🛰️  Galaxy —————————————————————————————————————————————————
.PHONY: build
build: ## 🗜️  Build for galaxy deployment (creates a tar.gz file)
#### Use build_o="..." to specify build options (--force, --output-path PATH, --token TOKEN, etc)
build: clean
	@$(eval build_o ?=)
	ansible-galaxy collection build $(build_o) .

.PHONY: install
install: ## ✍️  Install to a directory (to use the collection inside a playbook for instance)
#### Use install_o="..." to specify install options (--force, -p PATH, --no-deps, etc)
#### Use upgrade=1 instead of install_o="--upgrade" to keep compatibility with ansible below 2.10
#### Use source="..." to specify the source
install: upgrade ?= 0
install: install_o ?=
install: source ?= .
ifeq ($(ANSIBLE_INSTALL_OLD_FASHION),1)
# Disable upgrade on runtime
install: upgrade = 0
ifeq ($(shell if [ "$(source)" = "" ] || [ "$(source)" = "." ]; then echo 1; else echo 0; fi),1)
# Clean project in case goal is to install current project
install: clean
endif
endif
install:
ifeq ($(shell if [ "$(ANSIBLE_INSTALL_OLD_FASHION)" = "1" ] && [ "$(upgrade)" = "1" ]; then echo 1; else echo 0; fi),1)
	@echo "###################################################################################################"
	@echo "# Found --upgrade, not compatible with old fashion install. Existing content will be kept as is ! #"
	@echo "###################################################################################################"
endif
ifeq ($(shell if [ "$(ANSIBLE_INSTALL_OLD_FASHION)" = "1" ] && ([ "$(source)" = "" ] || [ "$(source)" = "." ]); then echo 1; else echo 0; fi),1)
	@echo "#########################################"
	@echo "# Old fashion installation using tar.gz #"
	@echo "#########################################"
	$(MAKE) build build_o="--output-path ${BUILD_DIR} --force"
	ansible-galaxy collection install $(install_o) ${BUILD_DIR}/${COLLECTION_NAMESPACE}-${COLLECTION_NAME}-${COLLECTION_VERSION}.tar.gz
else
	ansible-galaxy collection install $(install_o)$(if ($(upgrade),1), --upgrade,) $(source)
endif

.PHONY: deploy
deploy: ## 🚀 Deploy to ansible galaxy
	@echo "TODO"
##—————————— \_ 🧪️ Tests ——————————————————————————————————————————————————
.PHONY: build-for-test
build-for-test: ## 🧪️ Build to the temporary build directory for test usage
#### Use install_o="..." to specify install options (--force, -p PATH, --no-deps, etc)
build-for-test: install_o ?=
build-for-test:
	rm -rf ${COLLECTION_BUILD_DIR} # Remove only the collection directory (dependencies will be kept there if previously installed)
	$(MAKE) install install_o="$(install_o) --force -p ${ANSIBLE_COLLECTIONS_BUILD_DIR}" upgrade=1 # Use upgrade=1 to always run on latest versions
	cd ${COLLECTION_BUILD_DIR} && git init -q . # Workaround when test folder is under a gitignored folder (else ansible-test does nothing)

##—————————— \_ 🐍 Python —————————————————————————————————————————————————
.PHONY: install-as-python-pkg
install-as-python-pkg: ## 🔗 Build the collection and mount content as python package to current python environment
install-as-python-pkg: build_dir=${BUILD_DIR}/python-pkg
install-as-python-pkg: pkg_name=local-${COLLECTION_NAMESPACE}-${COLLECTION_NAME}-ansible-collections
install-as-python-pkg: clean
	rm -rf $(build_dir)/*
	$(MAKE) install install_o="--no-deps --force -p $(build_dir)/$(pkg_name)"
	cd $(build_dir) && $(PYTHON) -c 'from setuptools import setup;setup(name="$(pkg_name)", version="${COLLECTION_VERSION}", package_dir={"": "$(pkg_name)"}, packages=["ansible_collections"])' develop

.PHONY: uninstall-python-pkg
uninstall-python-pkg: ## 🗑️  Uninstall python package mirroring the project
uninstall-python-pkg:
	$(PYTHON)  -m pip uninstall local-${COLLECTION_NAMESPACE}-${COLLECTION_NAME}-ansible-collections
	$(MAKE) clean


##—— 🧪️ Tests —————————————————————————————————————————————————————————————
.PHONY: test
test: ## 🏃 Launch all tests
test: test-python test-ansible

##—————————— \_ 🐍 Python —————————————————————————————————————————————————
.PHONY: test-python
test-python: ## 🏃 Launch python-related tests (typehint, lint, etc)
test-python: test-mypy

.PHONY: test-mypy
test-mypy: ## 🏃 Launch MyPy checks
test-mypy:
	$(PYTHON) -m mypy --config-file mypy.ini .
	$(PYTHON) -m mypy --config-file tests/mypy.ini tests

##—————————— \_ 🇦 Ansible tests ———————————————————————————————————————————
### Trigger ansible-related tests upon built collection
.PHONY: test-ansible
test-ansible: ## 🏃 Launch ansible-related tests (unit, integration and sanity tests)
test-ansible: build-for-test test-ansible-units test-ansible-sanity test-ansible-integration

.PHONY: test-ansible-units
test-ansible-units: ## 🏃 Launch ansible unit tests
### Deactivated if "tests/unit" directory doesn't exist!
#### Use units_o="..." to specify options (--color, --docker, --coverage, etc)
ifneq ($(wildcard ${COLLECTION_BUILD_DIR}/tests/unit/.*),) # Execute tests only if there is the required directory !
test-ansible-units: units_o ?= -v --color --requirements
test-ansible-units:
	cd ${COLLECTION_BUILD_DIR} && ansible-test units $(units_o)
else
test-ansible-units:
	@echo "DEBUG ${COLLECTION_BUILD_DIR}/tests/unit => $(wildcard ${COLLECTION_BUILD_DIR}/tests/unit/.*)"
	@echo "###########################################################################"
	@echo "# Unit test directory is missing, create \"tests/unit\" directory first ! #"
	@echo "###########################################################################"
endif

.PHONY: test-ansible-integration
test-ansible-integration: ## 🏃 Launch ansible integration tests
### Deactivated if "tests/integration/targets" directory doesn't exist!
#### Use integration_o="..." to specify options (--retry-on-error, --python VERSION, --docker, --coverage, etc)
ifneq ($(wildcard ${COLLECTION_BUILD_DIR}/tests/integration/targets/),) # Execute tests only if there is the required directory !
test-ansible-integration: integration_o ?= -v --color --requirements
test-ansible-integration:
	cd ${COLLECTION_BUILD_DIR} && ansible-test integration $(integration_o)
else
test-ansible-integration:
	@echo "##################################################################################################"
	@echo "# Integration tests directory is missing, create \"tests/integration/targets\" directory first ! #"
	@echo "##################################################################################################"
endif

.PHONY: test-ansible-sanity
test-ansible-sanity: ## 🏃 Launch ansible sanity checks.
#### Use sanity_o="..." to specify options (--test TEST_NAME, --docker, --coverage, etc)
test-ansible-sanity: sanity_o ?= -v --color --requirements
test-ansible-sanity:
	cd ${COLLECTION_BUILD_DIR} && ansible-test sanity $(sanity_o)

.PHONY: test-ansible-coverage
test-ansible-coverage: ## 🏃 Launch ansible coverage generation (xml by default)
#### Use coverage_o="..." to specify options (--requirements, --group-by GROUP, etc)
#### Use coverage_c="..." to specify coverage command (report, html, combine, etc)
test-ansible-coverage: coverage_c ?= xml
test-ansible-coverage: coverage_o ?= -v --color --requirements
test-ansible-coverage:
	cd ${COLLECTION_BUILD_DIR} && ansible-test coverage $(coverage_c) $(coverage_o); \
