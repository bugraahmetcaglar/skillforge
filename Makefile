.PHONY: setup-hooks
setup-hooks:
	chmod +x scripts/git-hooks/pre-commit
	ln -sf ../../scripts/git-hooks/pre-commit .git/hooks/pre-commit
	echo "Git hooks installed successfully!"

.PHONY: setup
setup: setup-hooks
	pip install -r requirements/local.txt
	python manage.py migrate
