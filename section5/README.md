# 第 5 章 CNI（Container Network Interface）

## ソースコードについて

本ソースコードは、第 5 章 CNI（Container Network Interface） で使用するものです。詳細は本書該当部分をご確認ください。

## 実行するコマンド一覧

### 5-1 CNS のしくみ

```sh
minikube ssh -- cat /etc/cni/net.d/10-kindnet.conflist
minikube ssh -- ls /opt/cni/bin/
kubectl describe node minikube | grep PodCIDRs
kubectl describe node minikube-m02 | grep PodCIDRs
kubectl describe node minikube-m03 | grep PodCIDRs
kubectl apply -f deployment.yaml
kubectl get pod -o wide
minikube ssh -n minikube-m02
cd /run/cni-ipam-state/kindnet/
kubectl delete -f deployment.yaml

minikube delete
minikube start --nodes 3 --cni=flannel
minikube ssh -- cat /etc/cni/net.d/10-flannel.conflist
minikube ssh
sudo apt update && sudo apt install jq
sudo cat /var/lib/cni/flannel/<設定ファイル名> | jq

minikube ssh -- /opt/cni/bin/ptp
```

### 5-2 CNI プラグインの裏側のしくみ

```sh
minikube delete
minikube start --nodes 3 --cni=calico
kubectl get pods -n kube-system
kubectl create deployment sample --image=nginx
kubectl scale deployment sample --replicas=3
kubectl get pods -o wide
minikube ssh
sudo apt update
sudo apt install -y net-tools tcpdump
minikube ssh -- route -n
kubectl exec -ti <sampleのPod名> -- curl <minikube-m02ノードのIPアドレス>
minikube ssh
sudo tcpdump -i eth0 -n -q |grep <minikube-m02ノードのIPアドレス>
kubectl exec -ti <sampleのPod名> -- curl <minikube-m02ノードのIPアドレス>
kubectl delete deployment sample
```

### 5-3 Network Policy

```sh
kubectl apply -f pod.yaml
kubectl get pod -o wide
kubectl exec -ti web -- curl <db PodのIPアドレス>
kubectl apply -f deny-all.yaml
kubectl get networkpolicies
kubectl exec -ti web -- curl -m 3 <db PodのIPアドレス>
kubectl describe networkpolicies deny-all
kubectl apply -f pod-selector.yaml
kubectl get networkpolicies
kubectl describe networkpolicies pod-selector-api2db-egress
kubectl exec -ti web -- curl -m 3 <db PodのIPアドレス>
kubectl delete -f pod-selector.yaml
kubectl delete -f deny-all.yaml
kubectl delete -f pod.yaml

kubectl apply -f ns.yaml
kubectl apply -f pod.yaml -n app
kubectl get pod -o wide -n app
kubectl apply -f pod-analysis.yaml -n analysis
kubectl get pod -o wide -n analysis
kubectl exec -n app -ti db -- curl -m 3 <analysis PodのIPアドレス>
kubectl apply -f deny-all.yaml -n app
kubectl apply -f deny-all.yaml -n analysis
kubectl apply -f ns-selector.yaml
kubectl exec -n app -ti db -- curl -m 3 <analysis PodのIPアドレス>
kubectl exec -n analysis -ti analysis -- curl -m 3 <web PodのIPアドレス>
kubectl exec -n analysis -ti analysis -- curl -m 3 <api PodのIPアドレス>
kubectl apply -f ns-podSelector.yaml
kubectl exec -n analysis -ti analysis -- curl -m 3 <api PodのIPアドレス>
kubectl delete -f ns-podSelector.yaml
kubectl delete -f ns-selector.yaml
kubectl delete -f deny-all.yaml -n app
kubectl delete -f deny-all.yaml -n analysis
kubectl delete -f pod.yaml -n app
kubectl delete -f pod-analysis.yaml -n analysis
kubectl delete -f ns.yaml

minikube ssh
sudo apt update
sudo apt install iptables
sudo iptables -nvL
```
