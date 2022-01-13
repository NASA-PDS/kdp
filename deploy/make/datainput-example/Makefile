# Makefile to deploy a KDP datainput to a k8s cluster

.PHONY: deploy up down destroy uninstall

.DEFAULT_GOAL := deploy

# Deploy the datainput to the cluster
deploy:
	kubectl apply -f ../../yaml/datainput-example/datainput.yaml

up: deploy # alias

# Remove the datainput from the cluster
destroy:
	kubectl delete -f ../../yaml/datainput-example/datainput.yaml

down: destroy # alias
uninstall: destroy # alias