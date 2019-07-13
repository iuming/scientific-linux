在Scientific Linux7.6环境下安装python3
===
Scientific Linux系统自带的是python2系统，所以，想用python3需要自己安装，这里记录我安装python3的流程！    

安装流程     
---
1）下载安装包：**wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz**     
2）解压安装包：**tar zxvf Python-3.7.4.tgz**    
3）转到该目录下：**cd Python-3.7.4**         
4）对安装进行配置，并指定安装路径：**．/configure --prefix=/usr/local/python3.7.4**      
5）编译：**make**         
6）安装：**make install**       

建立连接    
---
1）**mv /usr/bin/python /usr/bin/python.bak**    
2）**ln -s /usr/local/python3.7.4/bin/python3.7.4 /usr/bin/python**     

这样，就安装配置好python3环境了！
