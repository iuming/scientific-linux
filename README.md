 wirless-divers-scientific-linux-
====
The record of installing wirless divers of scientific linux!   
    
一、安装scientific linux
---
先从装双系统scientific linux解释起吧！  
1、下载镜像文件：先从scientific linux官网上（也可以从不同的镜像站）下载[ios镜像文件](http://ftp.scientificlinux.org/linux/scientific/7x/x86_64/iso/)   
2、下载IMG写入U盘工具：这里推荐两个，1）[UltraIOS](https://cn.ultraiso.net/xiazai.html)这个软件收费但是可以下载试用版，比较好用的人也比较多，有一个缺点就是不能制作超过4G的镜像文件。2）[win32image](https://win32-image-writer.updatestar.com/)这个和UltraIOS制作启动盘大同小异，其他功能相对UltraIOS相对较少，但是可以制作超过4G的镜像文件。    因为everthing的scientific linux的镜像文件超过4G，所以这里推荐直接安装win32image。    
3、系统分区：这一步对于我就没有必要，因为我的电脑本来硬盘不是很大，快被我的文件占满了。所以直接买了一个移动硬盘来装linux系统，可以省去这个步骤。我也推荐用移动硬盘装系统，虽然没有装在本机硬盘上方便，但是比较便携，如果要出差或者去远处办事，拿着移动硬盘去到任何一个电脑都能运行这个系统，不用随时带着自己的电脑。废话不多说，开始正题！这里介绍windows系统的分区，macbook方法不同，这里不介绍。第一步，win+X快捷键，然后选择磁盘管理，进入之后选择一个比较空的盘，右键选择'压缩卷',然后输入需要分给linux的大小，至少15G，推荐分出30G。然后能够看见有30G硬盘显示的是黑色就可以了。    
4、制作启动盘：这时镜像文件和win32image应该下载完成，将win32image安装好，然后打开win32image，将U盘插入电脑，选择下载的镜像文件以及U盘的位置，先格式化一遍U盘，然后点击'写入'，等待一会儿，就制作好启动盘了。     
5、开始装系统：关机！将U盘插入电脑上，开机时进入bios，这里不同品牌的电脑进入的方式不同，华硕是开机时一直按住F2，然后选择开机启动项，第一行该成‘UEFI USB    ‘那一栏，点击F10，保存和确认，然后等待系统进入安装界面。选择语言等等之后会出现选择安装硬盘位置的图标，点进去选择在系统分区时分给它的硬盘，然后选择自动分配（正常情况下不用选），点击‘完成’，再选择软件安装，选择自己需要的软件进行安装（建议全选），最后点击‘安装’就开始安装了，一般需要安装半小时，这个与硬盘读存数据速度有关。安装的时候可以设置用户信息。    
6、安装完之后就完成了，重启！如果进入的不是linux系统的话，开机进入bios系统选择开机启动项，第一栏设置成linux系统再按F10启动就能进入linux系统了。    

二、安装无线驱动
---
正常开机之后发现设置里面wifi是缺少驱动的，如果安装好有wifi驱动请忽略这一步骤！     
1、查看网卡型号：进入终端，输入**lsb_release -a**查看版本号，然后输入**lspci | grep -i network**查看网卡型号。      
2、**yum group install 'Development Tools'   
     yum install redhat-lsb kernel-abi-whitelists    
     yum install kernel-devel-$(uname -r)**   
     在终端里面输入以上几行代码，来安装需要安装的组建和包。
     再输入以下几行代码，来创建一些目录和编译时需要的和版本有关的文件
   **mkdir -p ~/rpmbuild/{BUILD,RPMS,SPECS,SOURCES,SRPMS}    
     echo -e "%_topdir $(echo $HOME)/rpmbuild\n%dist .el$(lsb_release -s -r|cut -d"." -f1).local" >> ~/.rpmmacros**    
3、下载驱动[RPM 文件](http://elrepo.org/linux/elrepo/el7/SRPMS/wl-kmod-6_30_223_271-5.el7.elrepo.nosrc.rpm)、[网卡驱动](www.broadcom.com/support/802.11) 在打开上述网址之后，点击 Drivers 选项卡之后，根据 CPU 的位数以及网卡的版本选择下载。将下载完成后的文件放至 /root/rpmbuild/SOURCES 文件夹下（上一步创建的文件夹）。       
4、构建kmod-wl:     
     rpmbuild --rebuild --define 'packager <your-name>' /<path-to-nosrc.rpm>/wl-kmod*nosrc.rpm                
     将 <your-name> 替换为用户名，将 <path-to-nosrc.rpm> 替换成刚刚下载的 RPM 文件的路径。      
5、删除多余的包： yum remove \*ndiswrapper\*    也可能没有多余的包，无所谓！      
6、安装kmod-wl:    
     rpm -Uvh /<path-to-rpm>/kmod-wl*rpm     
     把 <path-to-rpm> 替换成刚刚生成的 RPM 的路径，即 `/root/rpmbuild/RPMS/x86_64/``。这一步操作也需要在这个路径下执行。      
 7、重启！到这一步已经安装好wifi驱动了，开机就能在状态栏看到wifi选项了。如果没有，在终端输入**modprobe wl**就能出现wifi图标！
