
clean:
	@echo "cleaning build artifacts..."
	@rm -rf dist
	@rm -rf build
	@rm -rf rpm-build
	@rm -rf install
	@rm -f MANIFEST AUTHORS README
	@echo "cleaning python bytecode..."
	@rm -f zenossctl/*.pyc

readme:
	@echo "creating: README"
	@cat README.md | sed -e 's/^\[!.*//g' | tail -n "+3" > README


sdist: readme authors
	@python setup.py sdist

build:
	@python setup.py build

install:
	@python setup.py install --root ${DESTDIR} install

qa:
	@echo "running pyflakes..."
	@pyflakes zenossctl/api.py zenossctl/cli.py zenossctl/utils.py zenossctl/server.py scripts/*
	@echo "running pep8..."
	@pep8 --ignore E303,E501 --exclude=arg_parse.py zenossctl/ scripts/

authors:
	@echo "creating: AUTHORS"
	@cp AUTHORS.in AUTHORS
	@git log --format='%aN <%aE>' | grep -v 'root' | sort -u >> AUTHORS


doc:
	@echo "creating: documentation"
	@cd docs; make html > /dev/null 2>&1

rpm: clean sdist
	@mkdir -p rpm-build
	@cp dist/*.gz rpm-build/
	@rpmbuild --define "_topdir %(pwd)/rpm-build" \
		--define "_builddir %{_topdir}" \
		--define "_rpmdir %{_topdir}" \
		--define "_srcrpmdir %{_topdir}" \
		--define "_specdir %{_topdir}" \
		--define '_rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm' \
		--define "_sourcedir  %{_topdir}" \
    		-ba zenossctl.spec


# EOF
