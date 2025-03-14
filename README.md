# docker-kubernetes-network-book

## docker のインストール方法

ここでは、docker のインストール方法を記載します。
バージョンは `27.5.1` です。

- リポジトリの追加

```sh
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

- インストール

```sh
VERSION_STRING=5:27.5.1-1~ubuntu.24.04~noble
sudo apt-get install docker-ce=$VERSION_STRING docker-ce-cli=$VERSION_STRING containerd.io docker-buildx-plugin docker-compose-plugin
```

- 確認

```sh
$ docker version
```

`Version: 27.5.1` という表示があればインストール成功です。

- docker のコマンドを sudo なしで実行できるようにする

```sh
sudo gpasswd -a $USER docker
sudo systemctl restart docker
```

上記コマンドを実行後、一度ログアウトして再度ログインすると、sudo なしで docker コマンドが実行できるようになります。
