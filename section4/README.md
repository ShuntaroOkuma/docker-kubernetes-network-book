# 第４章 Kubernetes ネットワークのしくみ

## ソースコードについて

本ソースコードは、第４章 Kubernetes ネットワークのしくみ で使用するものです。詳細は本書該当部分をご確認ください。

## 実行するコマンド一覧

### 4-2 Kubernetes の環境構築

```sh
minikube start --nodes=3
minikube node list
alias kubectl="minikube kubectl --"
kubectl get pods -A
kubectl get nodes

kubectl create sa admin
kubectl apply -f admin-clusterrolebinding.yaml

```

- Ubuntu の場合

```sh
minikube ip
export DOCKER_TLS_VERIFY="1"
export DOCKER_HOST="tcp://192.168.49.2:2376"
export DOCKER_CERT_PATH="$HOME/.minikube/certs"
export MINIKUBE_ACTIVE_DOCKERD="minikube"
docker build -t kube-sample-app:1.0 ./

export DOCKER_TLS_VERIFY="1"
export DOCKER_HOST="tcp://$(minikube -n minikube-m02 ip):2376"
export DOCKER_CERT_PATH="$HOME/.minikube/certs"
export MINIKUBE_ACTIVE_DOCKERD="minikube"
docker build -t kube-sample-app:1.0 ./

export DOCKER_TLS_VERIFY="1"
export DOCKER_HOST="tcp://$(minikube -n minikube-m03 ip):2376"
export DOCKER_CERT_PATH="$HOME/.minikube/certs"
export MINIKUBE_ACTIVE_DOCKERD="minikube"
docker build -t kube-sample-app:1.0 ./

eval $(minikube docker-env -u)
```

- macOS の場合

```sh
export DOCKER_TLS_VERIFY="1"
export DOCKER_HOST="tcp://127.0.0.1:$(docker inspect --format '{{ json .NetworkSettings.Ports }}' minikube | jq -r '."2376/tcp"[0].HostPort')"
export DOCKER_CERT_PATH="$HOME/.minikube/certs"
export MINIKUBE_ACTIVE_DOCKERD="minikube"
docker build -t kube-sample-app:1.0 ./
eval $(minikube docker-env -u)

export DOCKER_TLS_VERIFY="1"
export DOCKER_HOST="tcp://127.0.0.1:$(docker inspect --format '{{ json .NetworkSettings.Ports }}' minikube-m02 | jq -r '."2376/tcp"[0].HostPort')"
export DOCKER_CERT_PATH="$HOME/.minikube/certs"
export MINIKUBE_ACTIVE_DOCKERD="minikube"
docker build -t kube-sample-app:1.0 ./
eval $(minikube docker-env -u)

export DOCKER_TLS_VERIFY="1"
export DOCKER_HOST="tcp://127.0.0.1:$(docker inspect --format '{{ json .NetworkSettings.Ports }}' minikube-m03 | jq -r '."2376/tcp"[0].HostPort')"
export DOCKER_CERT_PATH="$HOME/.minikube/certs"
export MINIKUBE_ACTIVE_DOCKERD="minikube"
docker build -t kube-sample-app:1.0 ./
eval $(minikube docker-env -u)
```

### 4-3 Pod の通信のしくみ

```sh
kubectl apply -f pod.yaml
kubectl exec -ti sample-pod -c curl-container -- curl localhost:5000
kubectl exec -ti sample-pod -c curl-container -- ip address
docker inspect <k8s_api-container_sample-pod_default_で始まるコンテナ名> --format '{{.State.Pid}}'
docker inspect <k8s_curl-container_sample-pod_default_xxxではいまるコンテナ名> --format '{{.State.Pid}}'
sudo ls -la /proc/<出力されたプロセスID>/ns/net
sudo lsns <netnsのID> --output-all
kubectl delete -f pod.yaml

kubectl apply -f daemonset.yaml
kubectl get pod -o wide
kubectl exec -ti <Pod名> -- curl <PodのIPアドレス>:5000
kubectl delete -f daemonset.yaml
```

### 4-4 Service のしくみ

```sh
kubectl apply -f api-replicaset.yaml
kubectl apply -f curl-replicaset.yaml
kubectl get pod -o wide
kubectl apply -f clusterip.yaml

kubectl get svc clusterip-svc
kubectl describe svc clusterip-svc
kubectl get pod |grep curl
kubectl exec -ti <curl-containerが起動しているPod名> -- curl <clusterip-svcのIPアドレス>:5555
kubectl exec -ti <curl-containerが起動しているPod名> -- curlclusterip-svc.default.svc.cluster.local:5555
kubectl delete -f clusterip.yaml

kubectl apply -f nodeport.yaml
kubectl get svc nodeport-svc
curl 192.168.49.2:30000
docker exec -ti minikube-m02 sh

minikube start --ports=30000:30000
curl http://localhost:30000
kubectl delete -f nodeport.yaml

kubectl apply -f loadbalancer.yaml
kubectl get svc lb-svc
docker run -d --name haproxy --network=host -v $(pwd)/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro haproxy:2.9.7
curl localhost:8080

docker cp haproxy.cfg minikube:/home/docker/
docker exec -ti minikube bash
cd /home/docker/
docker run -d --name haproxy --network=host -v $(pwd)/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro haproxy
docker ps -f "name=haproxy"
exit
ssh docker@127.0.0.1 -N -p $(docker inspect --format='{{(index (index .NetworkSettings.Ports "22/tcp") 0).HostPort}}' minikube) -i $(minikube ssh-key) -L 8080:192.168.49.2:8080
curl localhost:8080
docker stop haproxy && docker rm haproxy
kubectl delete -f loadbalancer.yaml

kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.5/config/manifests/metallb-native.yaml
kubectl get pod -n metallb-system -o wide
kubectl apply -f metallb.yaml
kubectl get ipaddresspool -n metallb-system
kubectl apply -f loadbalancer.yaml
kubectl get svc
curl 192.168.49.100:5555
ssh docker@127.0.0.1 -N -p $(docker inspect --format='{{(index (index .NetworkSettings.Ports "22/tcp") 0).HostPort}}' minikube) -i $(minikube ssh-key) -L 5555:192.168.49.100:5555
curl localhost:5555
kubectl delete -f https://raw.githubusercontent.com/metallb/metallb/v0.14.5/config/manifests/metallb-native.yaml

minikube ssh
sudo iptables -L -nv -t nat | grep lb-svc | grep KUBE-SEP
kubectl delete -f loadbalancer.yaml

kubectl apply -f clusterip.yaml
kubectl get pod | grep curl
kubectl exec -ti <curl-containerが起動しているPod名> -- curl clusterip-svc.default.svc.cluster.local:5555
kubectl exec -ti <curl-containerが起動しているPod名> -- curl clusterip-svc:5555
kubectl exec -ti <curl-containerが起動しているPod名> -- cat /etc/resolv.conf
kubectl delete -f clusterip.yaml
kubectl delete -f api-replicaset.yaml
kubectl delete -f curl-replicaset.yaml
```

### 4-5 Ingress のしくみ

```sh
kubectl apply -f pod-for-ingress.yaml
kubectl exec -ti app1 -- curl app1:5000
kubectl exec -ti app2 -- curl app2:5000
minikube addons enable ingress
minikube addons list | grep ingress

kubectl apply -f ingress.yaml
kubectl get svc
kubectl get ingress

echo "192.168.49.2 app1.com" >> /etc/hosts
echo "192.168.49.2 app2.com" >> /etc/hosts
curl app1.com
curl app2.com
curl 192.168.49.2

kubectl get pods -n ingress-nginx | grep -v admission
kubectl get service -n ingress-nginx | grep -v admission
kubectl -n ingress-nginx exec -ti <ingress-nginx-controllerのPod名> -- cat nginx.conf |grep app1
kubectl delete -f ingress.yaml
kubectl delete -f pod-for-ingress.yaml
minikube addons disable ingress
```

### 4-6 リソースを適用するときの各コンポーネントの動き方

```sh
kubectl -n kube-system get pod
minikube ssh sudo service kubelet status

kubectl proxy --port=8001
curl http://127.0.0.1:8001/apis/apps/v1/watch/namespaces/default/deployments
kubectl apply -f deployment.yaml

kubectl apply -f service.yaml
kubectl get endpointslice
curl http://127.0.0.1:8001/api/v1/watch/namespaces/default/endpoints
curl http://127.0.0.1:8001/apis/discovery.k8s.io/v1/watch/namespaces/default/endpointslices

kubectl -n kube-system patch daemonsets.apps kube-proxy --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/command/-", "value": "--v=5" }]'
kubectl get pod -n kube-system |grep kube-proxy
kubectl logs -f -n kube-system <kube-proxyのPod名>
kubectl delete -f service.yaml
kubectl delete -f deployment.yaml
```
