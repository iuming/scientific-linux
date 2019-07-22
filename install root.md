INSTALL ROOT!       
====
欧洲核子研究中心CERN开发的基于C++，可与Fortran、Python等多种语言交互的数据处理软件。      
安装root可以大致分为三个步骤！第一步，将root的资源包以及需要的工具下载下来；第二步，解压、编译、安装；第三步，添加环境配置。         

一、下载root   
---------
root压缩包可以到[root官网](https://root.cern.ch/downloading-root)下载！       
正常情况下，下载Pro版本可以了，现在的最新版是[6.18.00](https://root.cern/download/root_v6.18.00.Linux-centos7-x86_64-gcc4.8.tar.gz)     
觉得这样不够酷，也可以直接在`/opt/root`终端输入`wget https://root.cern/download/root_v6.18.00.Linux-centos7-x86_64-gcc4.8.tar.gz`       
下载完root压缩文件后，需要查看电脑里有没有安装root需要的[其他工具软件](https://root.cern.ch/build-prerequisites#fedora),一般情况下会有`cmake`
、`libXpm-devel`、`libXext-devel`没有，检查的方式就是安一个，如果有的话终端会提示已经有了。例如：在终端输入`yum install libXpm-devel`.如果没有
`cmake`，可能不能这样安装，需要从官网下载安装包，然后解压、编译、安装。        

二、安装root       
------
安装root大致有5步：      
1、解压：`tar -zxvf root_v6.18.00.tar.gz`       
2、新建安装文件夹：`mkdir rootbld`           
3、进入文件夹目录：`cd rootbld`        
4、编译：`cmake /opt/root/root-6.18.00`       
5、安装：`cmake --build .`这一步的时间可能比较久!         

安装root有可能出现的问题：在编译步骤可能会出现错误，基本是缺少某些工具而导致的，查看提示的错误，重新安装一遍导致错误的工具就基本能解决这个问题了。      

三、添加root         
-------------
安装完成后，输入`source /opt/root/rootbld/bin/thisroot.sh`然后再输入`root`,就能运行root了！    
但是每次都要输入`source /opt/root/rootbld/bin/thisroot.sh`这么一大串比较繁琐，可以将它添加到.bashrc文件中：打开文件夹搜索`.bashrc`(在打开隐藏文
件情况下)，或者在根目录终端输入`ls`，再打开`gedit .bashrc`。再最下面添加`source /opt/root/rootbld/bin/thisroot.sh`     
这样，就可以直接在终端输入`root`就能运行root软件了！
