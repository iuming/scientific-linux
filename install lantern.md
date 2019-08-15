# INSTALL LANTERN              
蓝灯官网开发的版本只有windows、android以及ubuntu等版本，没有基于REDHAT的版本。基于这种情况，scientific linux需要使用lantern就需要操作一些步骤才能使用，以下记录我操作的这些步骤！                   
## 安装alien       
alien是一个用于在各种不同的Linux包格式相互转换的工具，其最常见的用法是将.rpm转换成.deb，我们需要的是将.deb转换成.rpm。        
```
yum install alien
```
等待一小会儿，alien就安装好了！            
## 下载lantern安装包         
进入github，搜索lantern，或者[点击这里](https://github.com/getlantern/lantern/releases/tag/latest)下载Ubuntu版本的安装包！或者直接：
```
cd <目标目录>
wget https://raw.githubusercontent.com/getlantern/lantern-binaries/master/lantern-installer-64-bit.deb
```
## 转换成rpm包          
在<目标目录>的终端下，输入：
```
alien -r lantern-installer-64-bit.deb #64位系统包
alien -r lantern-installer-32-bit.deb #32位系统包
```
这时有可能出现错误`Get Error:“conflicts with file from package filesystem”`         
（如果没有出现此处错误，可以跳到下一步）       
安装rpmrebuild：
```
yum install rpmrebuild
rpmrebuild -pe lantern-5.5.1-2.x86_64.rpm
```
将文件最后的一部分替换成下面这一段：
```
(Converted from a deb package by alien version 8.95.)
%files
#%dir %attr(0755, root, root) "/"
#%dir %attr(0755, root, root) "/usr"
#%dir %attr(0755, root, root) "/usr/bin"
%attr(0777, root, root) "/usr/bin/lantern"
#%dir %attr(0755, root, root) "/usr/lib"
%dir %attr(0755, root, root) "/usr/lib/lantern"
%attr(0644, root, root) "/usr/lib/lantern/.packaged-lantern.yaml"
%attr(0644, root, root) "/usr/lib/lantern/lantern-binary"
%attr(0755, root, root) "/usr/lib/lantern/lantern.sh"
%attr(0644, root, root) "/usr/lib/lantern/lantern.yaml"
#%dir %attr(0755, root, root) "/usr/share"
#%dir %attr(0755, root, root) "/usr/share/applications"
%attr(0644, root, root) "/usr/share/applications/lantern.desktop"
#%dir %attr(0755, root, root) "/usr/share/doc"
%dir %attr(0755, root, root) "/usr/share/doc/lantern"
%doc %attr(0644, root, root) "/usr/share/doc/lantern/changelog.gz"
%doc %attr(0644, root, root) "/usr/share/doc/lantern/copyright"
#%dir %attr(0755, root, root) "/usr/share/icons"
#%dir %attr(0755, root, root) "/usr/share/icons/hicolor"
#%dir %attr(0755, root, root) "/usr/share/icons/hicolor/128x128"
#%dir %attr(0755, root, root) "/usr/share/icons/hicolor/128x128/apps"
%attr(0644, root, root) "/usr/share/icons/hicolor/128x128/apps/lantern.png"
%changelog
```
## 安装lantern         
输入：`rpm -i /root/rpmbuild/RPMS/x86_64/lantern-5.5.1-2.x86_64.rpm`        
有可能出现缺少某些包的错误，缺什么安什么！例如：`yum install libappindicator-gtk3`，安完之后再安装，直至安装成功！             
## 设置自启动     
到上一步完成后，就能在应用程序中找到lantern了，也就是可以使用了！      
为了更加方便的使用lantern，可以设置开机自启动：
```
vi /etc/rc.d/rc.local
```
在最后添加`su - user -c '/usr/lib/lantern/lantern.sh'`      

至此，lantern安装完毕了～
