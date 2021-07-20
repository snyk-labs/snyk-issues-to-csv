APP_NAME=repo-issues-csv
TAG:=$(shell git rev-parse --short HEAD)

build:
	docker build -f Dockerfile -t $(APP_NAME):$(TAG) .

build-nc:
	docker build --no-cache -f Dockerfile -t $(APP_NAME):$(TAG) .

# make int: interactive container time
# builds a container image and runs it interactively
# it will destroy the image once you exit
int: build
	docker run --rm -it -e SNYK_TOKEN -e SNYK_GROUP -e SNYK_OUTPUT_DIR="/project/output" --volume $(CURDIR):/project --entrypoint "/bin/bash" $(APP_NAME):$(TAG)
	docker rmi $(APP_NAME):$(TAG)

run_issues: build
	docker run --rm -it -e SNYK_TOKEN -e SNYK_GROUP -e SNYK_OUTPUT_DIR="/project/output" --volume $(CURDIR):/project $(APP_NAME):$(TAG) /app/make_issues_csvs.py
	docker rmi $(APP_NAME):$(TAG)

run_join: build
	docker run --rm -it -e SNYK_TOKEN -e SNYK_GROUP -e SNYK_OUTPUT_DIR="/project/output" --volume $(CURDIR):/project $(APP_NAME):$(TAG) /app/auto_join_csv.py
	docker rmi $(APP_NAME):$(TAG)

stop:
	docker stop $(APP_NAME); docker rm $(APP_NAME)
