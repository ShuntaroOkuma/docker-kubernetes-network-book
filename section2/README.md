# 第 2 章 Docker ネットワークの要素技術

## ソースコードについて

本ソースコードは、第 2 章 Docker ネットワークの要素技術 で使用するものです。詳細は本書該当部分をご確認ください。

## 実行するコマンド一覧

### 2-1 Docker ネットワークの全体像と技術

```sh
docker build -t test-image ./
docker run -ti -d --name="curl-container" test-image
docker run -ti -d --name="api-container" test-image
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' api-container
docker exec -ti curl-container sh
```

### 2-2 インターネットの通信の全体像

```sh
docker restart curl-container
docker restart api-container
brctl show docker0
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' curl-container
docker inspect --format='{{range .NetworkSettings.Networks}}{{.MacAddress}}{{end}}' curl-container
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' api-container
docker inspect --format='{{range .NetworkSettings.Networks}}{{.MacAddress}}{{end}}' api-container
docker exec -ti api-container sh
docker exec -ti curl-container sh
brctl showmacs docker0
docker stop curl-container api-container
docker rm curl-container api-container
```

### 2-3 VXLAN

```sh
sudo ip link add vxlan0 type vxlan id 10 dstport 4789 dev enX0
sudo ip addr add 192.168.1.1/24 broadcast 192.168.1.255 dev vxlan0
sudo ip link set vxlan0 up
sudo ip link add vxlan0 type vxlan id 10 dstport 4789 dev enX0
sudo ip addr add 192.168.1.2/24 broadcast 192.168.1.255 dev vxlan0
sudo ip link set vxlan0 up
ping -c 1 192.168.1.2
sudo bridge fdb append 00:00:00:00:00:00 dev vxlan0 dst <パブリックIPアドレス>
bridge fdb show |grep vxlan0
sudo tcpdump -n host <パブリックIPアドレス>
sudo ip link delete vxlan0
```

### 2-4 Network Namespace

```sh
sudo ip netns add netns0
ip netns show
sudo ip netns exec netns0 ip link show
sudo ip netns exec netns0 ping <ホストのIPアドレス>
sudo ip netns exec netns0 ping www.google.com
sudo ip link add name veth0_container type veth peer name veth0_br
sudo ip link add name veth1_host type veth peer name veth1_br
sudo ip link set dev veth0_container netns netns0
sudo ip netns exec netns0 ip link show
sudo ip link add name bridge0 type bridge
ip link show bridge0
sudo ip link set dev veth0_br master bridge0
sudo ip link set dev veth1_br master bridge0
sudo ip netns exec netns0 ip addr add 192.168.0.1/24 dev veth0_container
sudo ip netns exec netns0 ip addr show veth0_container
sudo ip addr add 192.168.0.2/24 dev veth1_host
ip addr show veth1_host
sudo ip addr add 192.168.0.254/24 broadcast 192.168.0.255 label bridge0 dev bridge0
ip addr show bridge0
sudo ip link set bridge0 up
sudo ip link set veth0_br up
sudo ip link set veth1_host up
sudo ip link set veth1_br up
sudo ip netns exec netns0 ip link set veth0_container up
sudo ip netns exec netns0 ping -c1 192.168.0.2
sudo ip netns exec netns0 ping -c1 192.168.0.254
ping -c1 192.168.0.1
sudo ip netns del netns0
sudo ip link del dev bridge0
sudo ip link del dev veth1_br
```

### 2-5 iptables

```sh
sudo iptables -L -nv
sudo iptables -L -nv -t nat
docker network create --opt "com.docker.network.bridge.name"=br0 test-nw
docker network rm test-nw
docker run -dti -p 8888:80 alpine /bin/sh
```
