

for v in 0.7 0.8 0.9 0.9.1 0.9.2 1.0 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 1.10 1.11 1.12 2.0 2.1 2.2 2.2.1 2.3 2.4 2.5 2.6 2.7 2.8 2.9 2.10 2.11 2.12 2.13 2.14 2.14.1
do
   echo "Downloading and unzipping gradle $v"
   wget https://services.gradle.org/distributions/gradle-$v-bin.zip
   unzip gradle-$v-bin.zip
   mv gradle-$v $GRADLE_FARM_HOME/.
   rm gradle-$v-bin.zip
done