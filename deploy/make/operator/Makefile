# Makefile to deploy KDP operator to a k8s cluster

.PHONY: deploy up down destroy uninstall

.DEFAULT_GOAL := deploy

# Deploy kdp-operator to the cluster
deploy:
	kubectl apply -f ../../yaml/namespace.yaml
	kubectl apply -f ../../yaml/crd.yaml
	kubectl apply -f ../../yaml/rbac.yaml
	kubectl apply -f ../../yaml/deployment.yaml

up: deploy # alias

# Remove kdp-operator from the cluster
destroy:
	kubectl delete -f ../../yaml/namespace.yaml
	kubectl delete -f ../../yaml/crd.yaml
	kubectl delete -f ../../yaml/rbac.yaml
	kubectl delete -f ../../yaml/deployment.yaml

down: destroy # alias
uninstall: destroy # alias