# Makefile to deploy a KDP pipeline to a k8s cluster

.PHONY: deploy up down destroy uninstall

.DEFAULT_GOAL := deploy

# Deploy the pipeline to the cluster
deploy:
	kubectl apply -f ../../yaml/pipeline-example/pipeline.yaml

up: deploy # alias

# Remove the pipeline from the cluster
destroy:
	kubectl delete -f ../../yaml/pipeline-example/pipeline.yaml

down: destroy # alias
uninstall: destroy # alias