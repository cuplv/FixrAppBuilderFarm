
sudo apt-get update

sudo apt-get -y install software-properties-common python-software-properties bzip2 unzip openssh-client git lib32stdc++6 lib32z1

# sudo add-apt-repository ppa:openjdk-r/ppa
# sudo apt-get update
# sudo apt-get install openjdk-8-jdk

wget http://dl.google.com/android/android-sdk_r24.4-linux.tgz
tar -xvzf android-sdk_r24.4-linux.tgz
sudo ln -s android-sdk-linux /usr/local/android-sdk
rm android-sdk_r24.4-linux.tgz

/usr/local/android-sdk/tools/android update sdk -u -a -t 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52

/usr/local/android-sdk/tools/android update sdk -u -a -t 119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141

/usr/local/android-sdk/tools/android update sdk -u -a -t 153,154,155,156,157,158,159,160,161,162,163,164,165,166

wget https://dl.google.com/android/ndk/android-ndk-r9d-linux-x86_64.tar.bz2
tar -xvjf android-ndk-r9d-linux-x86_64.tar.bz2
sudo ln -s android-ndk-r9d /usr/local/android-ndk
rm android-ndk-r9d-linux-x86_64.tar.bz2


wget https://downloads.gradle.org/distributions/gradle-2.14-bin.zip
unzip gradle-2.14-bin.zip
sudo ln -s gradle-2.14 /usr/local/gradle
rm gradle-2.14-bin.zip

sudo apt-get -y install python-pip python-dev build-essential 
sudo apt-get -y install build-essential libssl-dev libffi-dev

wget https://github.com/libgit2/libgit2/archive/v0.24.0.tar.gz
tar xzf v0.24.0.tar.gz 
cd libgit2-0.24.0
cmake .
make
sudo make install
cd ..
rm v0.24.0.tar.gz

sudo pip install pygit2


# MongoDB
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927
echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list

sudo apt-get update
sudo apt-get install -y mongodb-org
sudo pip install pymongo

# Redis
wget http://download.redis.io/releases/redis-3.2.3.tar.gz
tar xzf redis-3.2.3.tar.gz
cd redis-3.2.3
make
sudo make install
cd ..

sudo pip install redis

# Flask
sudo pip install Flask

# Graylog
sudo easy_install graypy[amqp]


