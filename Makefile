# Based on that awesome makefile https://github.com/dunglas/symfony-docker/blob/main/docs/makefile.md#the-template

# Let user override python binary, collection's namespace/name/version if needed
PYTHON?=python

COLLECTION_NAMESPACE?=$(shell $(PYTHON) -c 'import yaml;print(yaml.load(open("galaxy.yml"), yaml.SafeLoader)["namespace"])')
COLLECTION_NAME?=$(shell $(PYTHON) -c 'import yaml;print(yaml.load(open("galaxy.yml"), yaml.SafeLoader)["name"])')
COLLECTION_VERSION?=$(shell $(PYTHON) -c 'import yaml;print(yaml.load(open("galaxy.yml"), yaml.SafeLoader)["version"])')

BUILD_DIR=build
ANSIBLE_COLLECTIONS_BUILD_DIR=${BUILD_DIR}/ansible_collections
COLLECTION_BUILD_DIR=${ANSIBLE_COLLECTIONS_BUILD_DIR}/${COLLECTION_NAMESPACE}/${COLLECTION_NAME}

.DEFAULT_GOAL = default

default: clean configure-dev

## —— 📚 Help ——————————————————————————————————————————————————————————————
.PHONY: help
help: ## ❓ Dislay this help
	@grep -E '(^[a-zA-Z0-9_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}{printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'

## —— ️⚙️  Environments ——————————————————————————————————————————————————————
.PHONY: clean
clean: ## 🧹 Clean generated contents
clean:
	rm -rf ${BUILD_DIR}/* tests/output .mypy_cache ${COLLECTION_NAMESPACE}-${COLLECTION_NAME}-*.tar.gz

.PHONY: configure-dev
configure-dev: ## 🤖 Install collection's required libraries to current python environment
configure-dev:
	$(PYTHON) -m pip install -r tests/requirements.txt # Install tests requirements
	$(PYTHON) -m pip install -r meta/ee-requirements.txt # Install internal requirements

.PHONY: configure-test-ansible
configure-test-ansible: ## 🧪️ Deploy to the temporary build directory for test usage
configure-test-ansible:
	rm -rf ${COLLECTION_BUILD_DIR} # Remove only this collection directory (dependencies will be kept there if previously installed)
	$(MAKE) install-local path="${ANSIBLE_COLLECTIONS_BUILD_DIR}"
	cd ${COLLECTION_BUILD_DIR} && git init . # Workaround, ansible-test doesn't launch any test if current directory is not a git repo :/

## —— 🇦 Ansible collection —————————————————————————————————————————————————
##               \_ 🛰️  Galaxy ——————————————————————————————————————————————
.PHONY: build
build: ## 🗜️  Build for galaxy deployment (creates a tar.gz file)
build: clean
	@$(eval o ?=)
	ansible-galaxy collection build $(o) .

.PHONY: install
install: ## ✍️  Install to default ansible collections directory (to use the collection inside a playbook for instance)
install: clean
	@$(eval o ?=)
	ansible-galaxy collection install --force $(o) .

.PHONY: deploy
deploy: ## 🚀 Deploy to ansible galaxy
	@echo "TODO"
##               \_ 📁 Local ———————————————————————————————————————————————
.PHONY: install-local
install-local: ## ✍️  Install for dev or tests usage. Example `make install-local path="path/to/somewhere" o="--no-deps --force"`
install-local:
	@$(eval o ?=)
	ansible-galaxy collection install -p $(path) $(o) --force .
##               \_ 🐍 Python ——————————————————————————————————————————————
.PHONY: install-as-python-pkg
install-as-python-pkg: ## 🔗 Build the collection and mount content as python package to current python environment
install-as-python-pkg: build_dir=${BUILD_DIR}/python-pkg
install-as-python-pkg: pkg_name=local-${COLLECTION_NAMESPACE}-${COLLECTION_NAME}-ansible-collections
install-as-python-pkg: clean
	rm -rf $(build_dir)/*
	$(MAKE) install-local path="$(build_dir)/$(pkg_name)" o="--no-deps"
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
.PHONY: test-ansible
test-ansible: ## 🏃 Launch ansible-related tests (unit, integration and sanity tests)
test-ansible: configure-test-ansible test-ansible-sanity

.PHONY: test-ansible-unit
test-ansible-unit: ## 🏃 Launch ansible unit tests
	@echo "TODO"

.PHONY: test-ansible-integration
test-ansible-integration: ## 🏃 Launch ansible integration tests
	@echo "TODO"

.PHONY: test-ansible-sanity
test-ansible-sanity: ## 🏃 Launch ansible sanity checks. To target a specific test, execute `make test-ansible-sanity c="--test TEST_NAME"`
test-ansible-sanity:
	@$(eval c ?=)
	cd ${COLLECTION_BUILD_DIR} && ansible-test sanity $(c)
