# Based on that awesome makefile https://github.com/dunglas/symfony-docker/blob/main/docs/makefile.md#the-template

# Let user override python binary, collection's namespace/name/version if needed
PYTHON?=python

COLLECTION_NAMESPACE?=$(shell $(PYTHON) -c 'import yaml;print(yaml.load(open("galaxy.yml"), yaml.SafeLoader)["namespace"])')
COLLECTION_NAME?=$(shell $(PYTHON) -c 'import yaml;print(yaml.load(open("galaxy.yml"), yaml.SafeLoader)["name"])')
COLLECTION_VERSION?=$(shell $(PYTHON) -c 'import yaml;print(yaml.load(open("galaxy.yml"), yaml.SafeLoader)["version"])')
ANSIBLE_VERSION=$(shell $(PYTHON) -c 'from ansible.release import __version__ ;print("%s" % ".".join( __version__.split(".")[:2]));')

BUILD_DIR=build
ANSIBLE_COLLECTIONS_BUILD_DIR=${BUILD_DIR}/ansible_collections
COLLECTION_BUILD_DIR=${ANSIBLE_COLLECTIONS_BUILD_DIR}/${COLLECTION_NAMESPACE}/${COLLECTION_NAME}

.DEFAULT_GOAL = default

default: clean configure-dev-env

## —— 📚 Help ——————————————————————————————————————————————————————————————
.PHONY: help
help: ## ❓ Dislay this help
	@grep -E '(^[a-zA-Z0-9_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}{printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'

## —— ️⚙️  Environments ——————————————————————————————————————————————————————
.PHONY: clean
clean: ## 🧹 Clean generated contents
clean:
	rm -rf ${BUILD_DIR}/* tests/output .mypy_cache ${COLLECTION_NAMESPACE}-${COLLECTION_NAME}-*.tar.gz

.PHONY: configure-dev-env
configure-dev-env: ## 🤖 Install required libraries for dev environment (python libs used on codebase)
configure-dev-env:
	$(PYTHON) -m pip install -r meta/ee-requirements.txt # Install internal requirements

.PHONY: configure-test-env
configure-test-env: ## 🤖 Install required libraries for test environment (libs used on codebase, MyPy, etc)
configure-test-env: configure-dev-env
	$(PYTHON) -m pip install -r tests/requirements.txt # Install tests requirements

## —— 🇦 Ansible collection —————————————————————————————————————————————————
##               \_ 🛰️  Galaxy ——————————————————————————————————————————————
.PHONY: build
build: ## 🗜️  Build for galaxy deployment (creates a tar.gz file)
##                                  Use build_o="..." to specify build options (--force, --output-path PATH, --token TOKEN, etc)
build: clean
	@$(eval build_o ?=)
	ansible-galaxy collection build $(build_o) .

.PHONY: install
install: ## ✍️  Install to a directory (to use the collection inside a playbook for instance)
##                                  Use install_o="..." to specify install options (--force, -p PATH, --no-deps, etc)
install: clean
ifeq ($(ANSIBLE_VERSION), 2.10)
# ansible-core v2.10 doesn't support installing fom current directory if it is not under C_NAMESPACE/C_NAME directories
# Install from tar.gz instead
install: build_o=--output-path ${BUILD_DIR} --force
install: build
install: source=${BUILD_DIR}/${COLLECTION_NAMESPACE}-${COLLECTION_NAME}-${COLLECTION_VERSION}.tar.gz
else
install: source=.
endif
install:
	@$(eval install_o ?=)
	ansible-galaxy collection install $(install_o) $(source)

.PHONY: deploy
deploy: ## 🚀 Deploy to ansible galaxy
	@echo "TODO"
##               \_ 🧪️ Tests ———————————————————————————————————————————————
.PHONY: build-for-test
build-for-test: ## 🧪️ Build to the temporary build directory for test usage
build-for-test:
	rm -rf ${COLLECTION_BUILD_DIR} # Remove only this collection directory (dependencies will be kept there if previously installed)
	$(MAKE) install install_o="--force -p ${ANSIBLE_COLLECTIONS_BUILD_DIR}"
	cd ${COLLECTION_BUILD_DIR} && git init -q . # Workaround when test folder is under a gitignored folder (else ansible-test does nothing)

##               \_ 🐍 Python ——————————————————————————————————————————————
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


## —— 🧪️ Tests —————————————————————————————————————————————————————————————
.PHONY: test
test: ## 🏃 Launch all tests
test: test-python test-ansible

##               \_ 🐍 Python ——————————————————————————————————————————————
.PHONY: test-python
test-python: ## 🏃 Launch python-related tests (typehint, lint, etc)
test-python: test-mypy

.PHONY: test-mypy
test-mypy: ## 🏃 Launch MyPy checks
test-mypy:
	$(PYTHON) -m mypy --config-file mypy.ini .

##               \_ 🇦 Ansible tests ————————————————————————————————————————
##                                  Trigger ansible-related tests upon built collection
.PHONY: test-ansible
test-ansible: ## 🏃 Launch ansible-related tests (unit, integration and sanity tests)
test-ansible: build-for-test test-ansible-sanity

.PHONY: test-ansible-units
test-ansible-units: ## 🏃 Launch ansible unit tests
##                                  Use unit_o="..." to specify options (--color, --docker, --coverage, etc)
test-ansible-units: unit_o?=--color
test-ansible-units:
	@$(eval unit_o ?=)
	@echo "TODO"

.PHONY: test-ansible-integration
test-ansible-integration: ## 🏃 Launch ansible integration tests
##                                  Use integration_o="..." to specify options (--retry-on-error, --python VERSION, --docker, --coverage, etc)
test-ansible-integration: integration_o?=--color
test-ansible-integration:
	@$(eval integration_o ?=)
	@echo "TODO"

.PHONY: test-ansible-sanity
test-ansible-sanity: ## 🏃 Launch ansible sanity checks.
##                                  Use sanity_o="..." to specify options (--test TEST_NAME, --docker, --coverage, etc)
test-ansible-sanity: sanity_o?=--color
test-ansible-sanity:
	@$(eval sanity_o ?=)
	cd ${COLLECTION_BUILD_DIR} && ansible-test sanity $(sanity_o)

.PHONY: test-ansible-coverage
test-ansible-coverage: ## 🏃 Launch ansible coverage generation (xml by default)
##                                  Use coverage_o="..." to specify options (--requirements, --group-by GROUP, etc)
##                                  Use coverage_c="..." to specify coverage command (report, html, combine, etc)
test-ansible-coverage: coverage_c?=xml
test-ansible-coverage: coverage_o?=--color
test-ansible-coverage:
	@$(eval coverage_o ?=)
	cd ${COLLECTION_BUILD_DIR} && ansible-test coverage $(coverage_c) $(coverage_o)
