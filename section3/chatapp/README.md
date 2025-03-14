# 第３章 Docker ネットワークのしくみ

## ソースコードについて

本ソースコードは、第３章 Docker ネットワークのしくみ の 3-6 チャットアプリ開発を通じた実践的なネットワーク構築　で使用するものです。詳細は本書該当部分をご確認ください。

## 実行するコマンド一覧

題３章に記載したコマンドは長いものが多いため、ここにまとめています（`docker ps -a`のような簡単なコマンドは除外しています）。

### 3-1 Docker のネットワーク構成

```sh
iptables -nv -L
iptables -nv -L -t nat
docker network ls
docker network inspect bridge

docker run -d --name=test-container alpine:latest tail -f /dev/null
docker inspect test-container --format '{{.State.Pid}}'
sudo ls -la /proc/<プロセスID>/ns/net
sudo mkdir /var/run/netns
sudo ln -s /proc/<プロセスID>/ns/net /var/run/netns/test-ns
sudo ip netns exec test-ns ip address
sudo ip netns exec test-ns ip route
cat /sys/class/net/<veth名>/iflink
sudo ip netns exec test-ns cat /sys/class/net/eth0/iflink
docker network inspect bridge
docker stop test-container
docker rm test-container
```

### 3-2 Docker ネットワークドライバ

```sh
docker run --rm -it --network=host alpine /bin/sh
docker run --rm -it --network=none alpine /bin/sh

```

### 3-3 ログからわかるコンテナ間の通信

```sh
docker run -ti -d --name="curl-container" test-image
docker run -ti -d --name="api-container" test-image
docker exec -ti curl-container hostname -i
docker exec -ti api-container hostname -i
docker exec -ti curl-container curl 172.17.0.3:5000
docker exec curl-container apk add tcpdump
docker exec api-container apk add tcpdump
docker exec curl-container tcpdump -h
docker exec api-container tcpdump -h

docker restart curl-container
docker exec curl-container arp -n
sudo tcpdump arp -i docker0 -n -e -q
docker exec curl-container curl 172.17.0.3:5000
docker exec -ti curl-container ip route
docker exec -ti curl-container cat /sys/class/net/eth0/iflink
brctl show docker0
bridge fdb show |grep <MACアドレス>
sudo tcpdump -i docker0 -n -A '(tcp[tcpflags] & tcp-syn)' == 0 and '(tcp[tcpflags] & tcp-push)' != 0
docker exec -ti curl-container curl 172.17.0.3:5000
sudo tcpdump -i <veth名> -n -A '(tcp[tcpflags] & tcp-syn)' == 0 and '(tcp[tcpflags] & tcp-push)' != 0
sudo docker exec -ti api-container tcpdump -i eth0 -n -A '(tcp[tcpflags] & tcp-syn)' == 0 and '(tcp[tcpflags] & tcp-push)' != 0
```

### 3-4 ログからわかるコンテナ外部との通信

```sh
TOKEN=`curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"` && curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4
ip address show dev enX0
docker stop api-container
docker rm api-container
docker run -ti -d --name="api-container" -p 5000:5000 test-image
sudo iptables -t nat -I PREROUTING 1 -j LOG --log-prefix "PREROUTING: "
sudo iptables -t nat -I DOCKER 1 -j LOG --log-prefix "NAT DOCKER: "
sudo iptables -t nat -I POSTROUTING 1 -j LOG --log-prefix "POSTROUTING: "
sudo iptables -I FORWARD 1 -j LOG --log-prefix "FORWARD: "
sudo iptables -I DOCKER 1 -j LOG --log-prefix "FILTER DOCKER: "
sudo iptables -L -t nat
sudo iptables -L -nv -t nat --line-numbers

sudo tcpdump -i enX0 port 5000 -n -q
tail -f /var/log/kern.log |grep -e "PREROUTING" -e "NAT DOCKER"
sudo iptables -L DOCKER -t nat
tail -f /var/log/kern.log |grep -e "FORWARD" -e "FILTER DOCKER"
sudo tcpdump -i docker0 port 5000 -n -q

docker stop curl-container api-container
docker rm curl-container api-container
```

### 3-5 マルチホストネットワークの構築

```sh
docker network create --subnet 172.18.0.0/16 \
--attachable=true \
-o "com.docker.network.bridge.name"="test-net" \
test-net
docker network ls
docker run -d --network test-net --ip 172.18.0.2 --name test-container test-image
docker network inspect test-net -f '{{json .Containers}}' | jq .
docker stop test-container
docker rm test-container
docker network rm test-net
```

- ホスト A

```sh
sudo ip link add vxlan0 type vxlan id 10 remote <ホストBのパブリックアドレス> dstport 4789 dev enX0
bridge fdb show |grep vxlan0
sudo ip address add 172.100.0.1/16 broadcast 172.100.255.255 dev vxlan0
ip -details address show vxlan0
sudo ip link set vxlan0 up
ip route |grep vxlan0

docker network create --attachable=true \
--subnet 172.18.0.0/16 \
-o "com.docker.network.bridge.name"="vxlan-net" \
vxlan-net
ip address show vxlan-net
brctl show vxlan-net
sudo brctl addif vxlan-net vxlan0
docker run -d --rm --name test-a --net vxlan-net --ip 172.18.0.11 alpine sleep 3600
docker exec -ti test-a hostname -i

docker exec -ti test-a ping -c 3 172.18.0.22

docker stop test-a
```

- ホスト B

```sh
sudo ip link add vxlan0 type vxlan id 10 remote <ホストAのパブリックアドレス> dstport 4789 dev enX0
bridge fdb show |grep vxlan0
sudo ip address add 172.100.0.1/16 broadcast 172.100.255.255 dev vxlan0
ip -details address show vxlan0
sudo ip link set vxlan0 up
ip route |grep vxlan0

docker network create --attachable=true \
--subnet 172.18.0.0/16 \
-o "com.docker.network.bridge.name"="vxlan-net" \
vxlan-net
ip address show vxlan-net
brctl show vxlan-net
sudo brctl addif vxlan-net vxlan0
docker run -d --rm --name test-b --net vxlan-net --ip 172.18.0.22 alpine sleep 3600
docker exec -ti test-b hostname -i

docker exec -ti test-b ping -c 3 172.18.0.11

docker stop test-b
```

### 3-6 チャットアプリ開発を通じた実践的なネットワーク構築

- ホスト A

```sh
docker build -t chat-app .
docker run -d --name redis --net vxlan-net --ip 172.18.0.100 redis
docker run -d --name chat-a --net vxlan-net --ip 172.18.0.11 -p 5000:5000 chat-app
```

- ホスト B

```sh
docker build -t chat-app .
docker run -d --name chat-b --net vxlan-net --ip 172.18.0.22 -p 5000:5000 chat-app
```
