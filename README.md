# Healthbird

A scalable streaming pipeline for processing twitter streams and analyzing results. As the name implies, the focus of this project is around keywords related to public health.

## Getting started

Try it out with minikube! For step by step instructions on installing minikube, follow [Install Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/). You'll also need `kubectl` and `helm` installed. If you're feeling adventerous, the general steps are:

* Make sure you have either KVM or VirtualBox
* Install minikube: `brew install minikube`
* Install kubectl: `brew install kubectl`
* Install helm: `brew install helm`

Normally, you can start minikube with `minikube start`, but for this we are going to run: 

```sh
minikube start --cpus 4 --memory 8192
``` 

This gives us the resources we need to run elasticsearch. Next, install helm on your minikube cluster by running:

```sh
helm init

# check if tiller started
kubectl get pods -n kube-system | grep tiller

# tiller can take a few mins, but eventually you should see something like
tiller-deploy-77b79fcbfc-hmqj8 1/1 Running 0 50s
```

## Deploy with the helm chart

At this point, you should be able to run

```sh
helm install healthbird ./helm
```

This installs the chart on your minikube cluster with the release name `healthbird`. `./helm` refers to the location of the chart, so make sure you are in the root directory. It will take a few mins for everything to spin up, but you can check the status by running:

```sh
kubectl get all
```

Once everything says running, you can access kibana using port-forwarding:

```sh
kubectl port-forward service/healthbird-kibana 5601:5601
```

Open your browser to `localhost:5601`, set up the Kibana index, and watch the tweets stream in!

## Shutting down

You can run:

```sh
minikube stop # saves the state of the VM
minikube delete # the nuclear option, you will need to re-install the chart after starting minikube again
```




