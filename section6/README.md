# 第 ６ 章 サービスメッシュを支える技術

## ソースコードについて

本ソースコードは、第 ６ 章 サービスメッシュを支える技術 で使用するものです。詳細は本書該当部分をご確認ください。

## 実行するコマンド一覧

### 6-2 Istio の使い方としくみ

```sh
minikube delete
minikube start --memory=16384 --cpus=4
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.24.3 sh -
cd istio-1.24.3
export PATH=$PWD/bin:$PATH
istioctl install --set profile=demo -y
kubectl get pod -n istio-system
kubectl label namespace default istio-injection=enabled

kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml
kubectl get pods
kubectl get services
kubectl get pods $(kubectl get pod -l app=productpage -o jsonpath={.items..metadata.name}) -o jsonpath="{.spec.containers[*].name}"
kubectl logs $(kubectl get pod -l app=productpage -o jsonpath={.items..metadata.name}) -c istio-proxy | grep "Envoy proxy"
kubectl exec $(kubectl get pod -l app=ratings -o jsonpath={.items..metadata.name}) -c ratings -- curl -s productpage:9080/productpage | grep "<title>"

kubectl apply -f samples/bookinfo/networking/bookinfo-gateway.yaml
kubectl get gateway bookinfo-gateway -o yaml
kubectl get virtualservice bookinfo -o yaml
sudo minikube tunnel --cleanup
kubectl get svc -n istio-system istio-ingressgateway
ps -ef | grep docker@127.0.0.1
kubectl get svc -n istio-system istio-ingressgateway -o jsonpath="{.spec.ports}" |jq .
kubectl get pods $(kubectl get pod -n istio-system -l app=istio-ingressgateway -o jsonpath={.items..metadata.name}) -n istio-system -o jsonpath="{.status.podIP}"

kubectl apply -f samples/bookinfo/networking/destination-rule-reviews.yaml
kubectl apply -f reviews.yaml
kubectl apply -f ratings-delay.yaml
kubectl apply -f reviews-timeout.yaml
kubectl delete -f ratings-delay.yaml
kubectl delete -f reviews-timeout.yaml
kubectl delete -f samples/bookinfo/networking/destination-rule-reviews.yaml

kubectl exec $(kubectl get pod -l app=productpage -o jsonpath={.items..metadata.name}) -c istio-proxy -- curl http://reviews:9080/health -o /dev/null -s -w '%{http_code}¥n'
istioctl x describe pod $(kubectl get pod -l app=productpage -o jsonpath={.items..metadata.name})
kubectl apply -f bookinfo-pa.yaml
kubectl get pa
kubectl exec $(kubectl get pod -l app=productpage -o jsonpath={.items..metadata.name}) -c istio-proxy -- curl https://reviews:9080/health -o /dev/null -s -w '%{http_code}¥n'
cp samples/bookinfo/networking/destination-rule-all-mtls.yaml ./destination-rule-all-mtls-disabled.yaml
sed -i '' 's/ISTIO_MUTUAL/DISABLE/g' destination-rule-all-mtls-disabled.yaml
kubectl apply -f destination-rule-all-mtls-disabled.yaml
kubectl delete -f destination-rule-all-mtls-disabled.yaml
kubectl delete -f bookinfo-pa.yaml
kubectl exec $(kubectl get pod -l app=productpage -o jsonpath={.items..metadata.name}) -c istio-proxy -- curl http://reviews:9080/health -o /dev/null -s -w '%{http_code}¥n'

kubectl apply -f samples/addons/kiali.yaml
kubectl apply -f samples/addons/prometheus.yaml
kubectl rollout status deployment/kiali -n istio-system
istioctl dashboard kiali
kubectl apply -f samples/bookinfo/networking/virtual-service-reviews-90-10.yaml
kubectl apply -f samples/bookinfo/networking/destination-rule-all.yaml
for i in $(seq 1 100); do curl -s -o /dev/null "http://localhost/productpage"; done
kubectl delete -f samples/bookinfo/networking/virtual-service-reviews-90-10.yaml
kubectl delete -f samples/bookinfo/networking/destination-rule-all.yaml
kubectl delete -f samples/bookinfo/networking/bookinfo-gateway.yaml
kubectl delete -f samples/bookinfo/platform/kube/bookinfo.yaml
minikube delete
```
