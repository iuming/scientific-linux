#!/usr/bin/env python
# Copyright 2017 Battelle Energy Alliance, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Program that reads in input file, and runs it for a bit.
If start_time + timesteps * time_delta < end_time, it will
    控制运行的方法是依靠时间，从开始时间，每个步长增加一个时间增量。
	没有抽样参数啊？每一次新的.i文件，也就是输入文件是谁写的？
	这个程序仅仅是一个执行程序，应该不管输入文件的变化？这里也没有输入文件的参数？
	有点理解了数据的控制过程，不是依靠概率，而是依靠程序自己的控制。然后产生分支，并且开始计算。
	从消化看，code还是需要根据初始的读取文件，生成新的文件，并且以新的文件为基础开展计算。并且计算数据读取
	文件可能还需要关注重复部分的内容。这个需要了解，具体det程序中那个部分是根据输入文件，生产新的输入文件的函数。
	已经确认，DET通过新的输入文件作为输入。分支依靠事件树节点产生新的分支，是三个分支。如果符合分支条件。
	与DET中概率的国际关系是什么呢？
	理解了文件编码的生成方式，也大概料了解了概率的计算，对于二分支的话，对于三分之目前还不了解是什么原理。
	分支概率是每次计算的时候就开始计算的。第一步长是不计算的。


write out an xml file with branch info, otherwise it will stop.
最终还是没有看懂这个文件。

"""


#for future compatibility with Python 3--------------------------------------------------------------
from __future__ import division, print_function, unicode_literals, absolute_import
import warnings
warnings.simplefilter('default',DeprecationWarning)
#End compatibility block for Python 3----------------------------------------------------------------

import sys,os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re

print("Arguments:",sys.argv)
以下是调试的信息。在调用code的时候，传递的命令行就是这个信息。代表了路径，输入文件，以及文件名。
 'Arguments:这是一个列表。
 [\'C:/msys64/home/wangh/projects/raven/tests/framework/Samplers/DynamicEventTrees/simple_det.py\', 
 \'-i\',这个就是1号元素。
 \'simple_det_test.i\',
 \'Outputs/file_base=out~simple_det_test\', 
 \'Outputs/csv=false\', 
 \'Outputs/checkpoint=true\', 
 \'Outputs/tail/type=ControlLogicBranchingInfo\', 
 \'Outputs/ravenCSV/type=CSVRaven\']
 #因为这样的打印就是标准打印，就是在屏幕上打印。


if len(sys.argv) < 3 or sys.argv[1] != "-i":
  print(sys.argv[0]," -i input")
  sys.exit(-1)


inputFilename = sys.argv[2] simple_det_test.i 这个应该是文件名。 应该是simple_det_test.i
结果就是把一个文件传递给了input这个变量。
inputFile = open(inputFilename,"r") 打开一个已经存在的文件。不用包括路径吗？
属于默认路径。inputFile就是这个文件的读取。
下面开始解析。
理解了这里的意思：通过文件传递，获得文件地址以及文件名，但是把输入文件的后缀去掉，形成新的文件后缀。
root = os.path.splitext(inputFilename)[0] 把文件名的名称和后缀分离。
splitext()    用于返回文件名和扩展名元组。
head,tail = os.path.split(root)
注释：split()  用于返回目录路径和文件名的元组。一个地址和后缀的元祖。
prefix = "out~"
outFile = open(os.path.join(head,prefix+tail+".csv"),"w") 
将分离的部分组成一个路径。所以，head应该是一个地址，而后面的是一个文件名。
根据输入文件，通过打开方式建立一个输出文件。
输出文件是out~simple_det_test.csv

lines = inputFile.readlines()读取输入文件的每一个行。

lastLine = lines.index("[]\n") 最后一行。

def get_params(line):  从一个行获得数据。 返回一个元祖。
  """
    Gets the parameters from a line. 从一而文件的行获得数据
    @ In, line, string, The line to parse   输入包括在一行里的字符串
    @ Out, (name,params), (string,string or list), The name of the parameter
      and either a single parameter or a list of parameters.
	  输出包括名、和参数。字符串或李彪。获得参数的名，或者单一参数或者一系列的参数。
	  是否是获得一个参数名以及参数。通过读文件的方式，读取一个输入文件的每一行，
	  从而获得每一行中的参数名称以及参数值，或者一个参数列表。
  """
  start_match = re.search("\[\./([a-zA-Z_]+)\]",line)判断某一行是否是字符开头。
  #“\”字符的含义是去掉这个字符后面符号的特殊含义。所以，匹配的含义就是[./tring]
  判断是否包括这些字符。
  if start_match is not None: 判断是否有
  如果没有，则返回一个回车。
    return "[./]",start_match.group(1) #这个地方有点不懂。返回一个./后面的第一组是什么？
  if " = " not in line:如果没有“等号”，则写两个空空
    return None, None
  equalsIndex = line.index("=") 搜索每一行里是否有一个“等号”，如果有返回一个开始值。
  获得等号的位置，然后把等号前面所有的字符赋给name。并删除空格，也就是获取每一行变量的名字。
  name = line[:equalsIndex].strip() 名称等于等号后面的字符串并去掉空格。这个是把等号
  if line.rstrip().endswith('"'):
    params = line[equalsIndex + 1:].strip().strip('"').split()参数去除收尾的“”和
	参数等于等号后面的值，去掉首尾的“”
    return name,params
  else:
    return name,line[equalsIndex + 1:].strip()去除空格。返回的是名和后面的数字，也就是参数吗？

triggerLow = [] 控制的下限。是一个列表
triggerHigh = []

上面是读取输入文件，然后再重新写一个输入文件。目的是每次都要有一个新的文件吗？

for name, params in [get_params(l) for l in lines]: 调用了上面定义的函数。#for循环语句还需要加强学习。


  print(name,params)，这个是
  if name == "names":
    nameList = params 是两个参数一个是泵流量一个是分支信息
    names = ",".join(["time","x"]+params) 
	#这个是产生输入文件的第一行，也就CSV文件的表头。除了两个分支，还增加了时间和X两个变量。
    nameIndexs = {}#这是一个字典
    for i in range(len(params)):#params应该是一个列表或元组，len是求这个元组中元素的个数？
      nameIndexs[params[i]] = i #这个字典的关键字是名字的参数，值是序号。
	  #这是一个字典，是参数名和参数名对应的编号的字典。这个语句是字典的赋值语句。以参数名为键，以整型参数为数值。
  elif name == "start":
    start = list(map(float, params)) #将元组转换为列表。map是作用函数，将每一个变量都变成浮点型数据。
  elif name == "dt":
    dt = list(map(float, params))
  elif name == "dx":
    dx = list(map(float, params))
  elif name == "start_time":
    startTime = float(params)
  elif name == "end_time":
    endTime = float(params)
  elif name == "time_delta":
    timeDelta = float(params)
  elif name == "x_start":
    xStart = float(params)
  elif name == "timesteps":
    timesteps = int(params)
  elif name == "x_dt":
    xDt = float(params)
  elif name == "end_dx":
    endDx = list(map(float, params))
  elif name == "end_probability":
    endProbability = list(map(float, params))
  elif name == "trigger_name":
    triggerName = params.strip()
  elif name == "trigger_low":
    triggerLow = list(map(float, params))
  elif name == "trigger_high":
    triggerHigh = list(map(float, params))
  elif name == "[./]":
  #读取文件中有这么一个标识符，后面是数值。
  #但是程序输入文件有很多的这种表述符，如何处理？
  #可能把所有的这种标识符的内容都取到相关的文件中。
    header = params
  elif name == "value":
    temp_value = float(params) 每一次的value是不同的，所以，这个暂时的变量也是不同的。
    if header == "x":这个地方控制了参数的变化。这个里面还是需要进一步的理解的。
      xStart = temp_value - startTime * xDt
    elif header in nameIndexs:
      j = nameIndexs[header]
	  #这里j是一个整数？
      start[j] = temp_value - startTime * dt[j]，每次循环这个会变化，从而value也会变化，也就是分支量和泵流量会变化。
	  #这一段的含义是，判断分支的条件，如果分支是X，则变化xStart的数值，这个数值与x的值相关。。如果是其他的，如分支或者泵流量，就变开始时间。
	  #start是一个列表。如果分支或者泵流量变了，则把这个初始值变化。
	  如果有重复的，就会覆盖。

print(names,file=outFile)  
#这里有可能是重新写输入文件。关于文件的写操作还是要进一步学习。这里是把表头写上去了。
#也就是time，X，分支，以及泵的流量。

#timeDelta = (endTime - startTime)/timesteps

if len(triggerLow) > 0 and len(triggerHigh) > 0: 判断，高、低触发器是否存在。并赋值给逻辑控制变量。
  hasTrigger = True
else:
  hasTrigger = False

triggerVariable = ""
triggerValue = 0.0

for i in range(0,timesteps+1):  这个就是在写csv文件。从0开始，循环步长的文件。是在写文件。循环10步。
#英文已经修改了，所以现在的控制逻辑是，如果没有符合终止条件，那么就运行10步，而不管是否达到了运行的结束时间。

  shouldBreak = False
  time = startTime + timeDelta * i   时间等于开始时间加上步长的累计时间，这里步长是1.所以，步长设置对运行没有影响。
  x = xStart + xDt * time   x=开始+时间乘以变化量。x=1.0+0.1*time
  print(time, end=",", file=outFile)  通过尝试，这个就是在写文件。写每个det文件里面的csv文件。而且可以增加。
  print(x, end="", file=outFile)
  for j in range(0,min(len(start),len(dx),len(dt))):
    print(end=",", file=outFile)
    value = start[j] + time*dt[j] + x*dx[j] 一个列表的累加。当前时间乘以变化量+当前数值*数值变化量。

	分支时间和流量。
    print(value, end="", file=outFile)
    if hasTrigger:
      if triggerLow[j] < value < triggerHigh[j]: 这个是判断分支的条件，
	  trigger_low = "12.0 5.0"
      trigger_high = "12.1 5.1"
	  如果计算值，是两个列表。在最高和最低之间，则分支。
        shouldBreak = True
        triggerVariable = nameList[j] 
		#这个应该是指分支信息和流量。也就是触发分支的参数名是其中之一。
		#branchChangedParam变量是DET中的分支变量
		#triggerVariable是主程序中的触发变量。两个变量是一致的。问题是如何传递的参数？
        triggerValue = value
  print(file=outFile)
  if shouldBreak:
    break


#print([x + endDxi for endDxi in endDx],endProbability)

outFile.close()

if len(triggerVariable) == 0: 如果计算值在出发条件之间，则触发分支的是x？
#根据184判断的条件，只有分支了，才对触发变量名进行赋值，否则就是空，长度是零。

  triggerVariable = "x"
  triggerValue = x  当分支数据和泵的流量不符合条件是，就是x作为分支变量。
  而这个是在每一次调用的第一次就确定的。因为第一次调用时，就是x，x变化以后，因为触发变量
  已经赋值，就不会再进行赋值了。也就是只有一次分支的条件发生。只是在第一步吗？

if time < endTime: 结束时间。这一段有什么用呢？
#感觉这个是用于产生DET分支文件的部分。推测的是如果运行时间不许傲宇结束时间，则就继续分支计算。以
#上一个结束文件为基础。
  root = ET.Element('Branch_info') 这是一个ET中的一个类吗？
  root.set("end_time", str(time)) 
  triggerNode=ET.SubElement(root,"Distribution_trigger")
  triggerNode.set("name", triggerName)#这个调用的是出发的一个类的名称。
  var = ET.SubElement(triggerNode,'Variable')#这个是指明触发的变量名。
  var.text=triggerVariable
  这个应该是对DET类的一个赋值，猜测是把触发变量，触发变量的值赋给对象。
  下面都是在设置属性。
  var.set('type', "auxiliary") 这是一个参数结合？
  var.set('old_value', str(triggerValue))，可能都是字典，键和值对应。所以，old_value就是触发的值。
  真正触发的内容可能在这个里面。
  var.set('actual_value', " ".join([str(v) for v in [triggerValue + endDxi for endDxi in endDx]]))
  这个是分支的一个判断条件，感觉。实际的值是触发值，再加上两个。
  #终于搞清楚了，但是实际上怎么用呢？还差就是概率问题了？
  #v和p都是一个指示性的变量，可以循环的变量。
  #这个语句是一个字典，实际值是一个键，键的数值是一个字符串型的数据，
  var.set('probability', " ".join([str(p) for p in endProbability]))这句话有用吗？
  #这句话的含义是，利用p来连接结束概率中的数值？理解的不对。
  #这个含义是用空格 把结束概率的数值，覆盖这个参数。


  xmlFile = open(os.path.join(head,prefix+tail+"_actual_branch_info.xml"),"w")  写一个XML文件，但是在文件里面没有看到？

     #Done parsing C:\msys64\home\wangh\projects\raven\tests\framework\Samplers\DynamicEventTrees\DETshort\DETrunTest\DET_test_1\
	# out~simple_det_test_actual_branch_info.xml

    没有看到的原因是在DET默认程序中可能删除了。可以调试一下。
  调试程序里面提到，如果有actual这个xml文件，则分支，否则不分支？
  xmlFile.write(minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent="\t"))
  xmlFile.close()
