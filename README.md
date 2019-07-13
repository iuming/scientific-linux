 wirless-divers-scientific-linux-
====
The record of installing wirless divers of scientific linux!   
    
一、安装scientific linux
---
先从装双系统scientific linux解释起吧！  
1、下载镜像文件：先从scientific linux官网上（也可以从不同的镜像站）下载[ios镜像文件](http://ftp.scientificlinux.org/linux/scientific/7x/x86_64/iso/)   
2、下载IMG写入然后再下载一个制作启动盘的软件，这里推荐两个，1）[UltraIOS](https://cn.ultraiso.net/xiazai.html)这个软件收费但是可以下载试用版，比较好用的人也比较多，有一个缺点就是不能制作超过4G的镜像文件。2）[win32image](https://win32-image-writer.updatestar.com/)这个和UltraIOS制作启动盘大同小异，其他功能相对UltraIOS相对较少，但是可以制作超过4G的镜像文件。    因为everthing的scientific linux的镜像文件超过4G，所以这里推荐直接安装win32image。    
3、系统分区：这一步对于我就没有必要，因为我的电脑本来硬盘不是很大，快被我的文件占满了。所以直接买了一个移动硬盘来装linux系统，可以省去这个步骤。我也推荐用移动硬盘装系统，虽然没有装在本机硬盘上方便，但是比较便携，如果要出差或者去远处办事，拿着移动硬盘去到任何一个电脑都能运行这个系统，不用随时带着自己的电脑。废话不多说，开始正题！这里介绍windows系统的分区，macbook方法不同，这里不介绍。第一步，win+X快捷键，然后选择磁盘管理，进入之后选择一个比较空的盘，右键选择'压缩卷',然后输入需要分给linux的大小，至少15G，推荐分出30G。然后能够看见有30G硬盘显示的是黑色就可以了。
4、制作启动盘：这时镜像文件和win32image应该下载完成，将win32image安装好，然后打开win32image
