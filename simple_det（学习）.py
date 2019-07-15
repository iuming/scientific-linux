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
    �������еķ���������ʱ�䣬�ӿ�ʼʱ�䣬ÿ����������һ��ʱ��������
	û�г�����������ÿһ���µ�.i�ļ���Ҳ���������ļ���˭д�ģ�
	������������һ��ִ�г���Ӧ�ò��������ļ��ı仯������Ҳû�������ļ��Ĳ�����
	�е���������ݵĿ��ƹ��̣������������ʣ��������������Լ��Ŀ��ơ�Ȼ�������֧�����ҿ�ʼ���㡣
	����������code������Ҫ���ݳ�ʼ�Ķ�ȡ�ļ��������µ��ļ����������µ��ļ�Ϊ������չ���㡣���Ҽ������ݶ�ȡ
	�ļ����ܻ���Ҫ��ע�ظ����ֵ����ݡ������Ҫ�˽⣬����det�������Ǹ������Ǹ��������ļ��������µ������ļ��ĺ�����
	�Ѿ�ȷ�ϣ�DETͨ���µ������ļ���Ϊ���롣��֧�����¼����ڵ�����µķ�֧����������֧��������Ϸ�֧������
	��DET�и��ʵĹ��ʹ�ϵ��ʲô�أ�
	������ļ���������ɷ�ʽ��Ҳ������˽��˸��ʵļ��㣬���ڶ���֧�Ļ�����������֮Ŀǰ�����˽���ʲôԭ��
	��֧������ÿ�μ����ʱ��Ϳ�ʼ����ġ���һ�����ǲ�����ġ�


write out an xml file with branch info, otherwise it will stop.
���ջ���û�п�������ļ���

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
�����ǵ��Ե���Ϣ���ڵ���code��ʱ�򣬴��ݵ������о��������Ϣ��������·���������ļ����Լ��ļ�����
 'Arguments:����һ���б�
 [\'C:/msys64/home/wangh/projects/raven/tests/framework/Samplers/DynamicEventTrees/simple_det.py\', 
 \'-i\',�������1��Ԫ�ء�
 \'simple_det_test.i\',
 \'Outputs/file_base=out~simple_det_test\', 
 \'Outputs/csv=false\', 
 \'Outputs/checkpoint=true\', 
 \'Outputs/tail/type=ControlLogicBranchingInfo\', 
 \'Outputs/ravenCSV/type=CSVRaven\']
 #��Ϊ�����Ĵ�ӡ���Ǳ�׼��ӡ����������Ļ�ϴ�ӡ��


if len(sys.argv) < 3 or sys.argv[1] != "-i":
  print(sys.argv[0]," -i input")
  sys.exit(-1)


inputFilename = sys.argv[2] simple_det_test.i ���Ӧ�����ļ����� Ӧ����simple_det_test.i
������ǰ�һ���ļ����ݸ���input���������
inputFile = open(inputFilename,"r") ��һ���Ѿ����ڵ��ļ������ð���·����
����Ĭ��·����inputFile��������ļ��Ķ�ȡ��
���濪ʼ������
������������˼��ͨ���ļ����ݣ�����ļ���ַ�Լ��ļ��������ǰ������ļ��ĺ�׺ȥ�����γ��µ��ļ���׺��
root = os.path.splitext(inputFilename)[0] ���ļ��������ƺͺ�׺���롣
splitext()    ���ڷ����ļ�������չ��Ԫ�顣
head,tail = os.path.split(root)
ע�ͣ�split()  ���ڷ���Ŀ¼·�����ļ�����Ԫ�顣һ����ַ�ͺ�׺��Ԫ�档
prefix = "out~"
outFile = open(os.path.join(head,prefix+tail+".csv"),"w") 
������Ĳ������һ��·�������ԣ�headӦ����һ����ַ�����������һ���ļ�����
���������ļ���ͨ���򿪷�ʽ����һ������ļ���
����ļ���out~simple_det_test.csv

lines = inputFile.readlines()��ȡ�����ļ���ÿһ���С�

lastLine = lines.index("[]\n") ���һ�С�

def get_params(line):  ��һ���л�����ݡ� ����һ��Ԫ�档
  """
    Gets the parameters from a line. ��һ���ļ����л������
    @ In, line, string, The line to parse   ���������һ������ַ���
    @ Out, (name,params), (string,string or list), The name of the parameter
      and either a single parameter or a list of parameters.
	  ������������Ͳ������ַ�������롣��ò������������ߵ�һ��������һϵ�еĲ�����
	  �Ƿ��ǻ��һ���������Լ�������ͨ�����ļ��ķ�ʽ����ȡһ�������ļ���ÿһ�У�
	  �Ӷ����ÿһ���еĲ��������Լ�����ֵ������һ�������б�
  """
  start_match = re.search("\[\./([a-zA-Z_]+)\]",line)�ж�ĳһ���Ƿ����ַ���ͷ��
  #��\���ַ��ĺ�����ȥ������ַ�������ŵ����⺬�塣���ԣ�ƥ��ĺ������[./tring]
  �ж��Ƿ������Щ�ַ���
  if start_match is not None: �ж��Ƿ���
  ���û�У��򷵻�һ���س���
    return "[./]",start_match.group(1) #����ط��е㲻��������һ��./����ĵ�һ����ʲô��
  if " = " not in line:���û�С��Ⱥš�����д�����տ�
    return None, None
  equalsIndex = line.index("=") ����ÿһ�����Ƿ���һ�����Ⱥš�������з���һ����ʼֵ��
  ��õȺŵ�λ�ã�Ȼ��ѵȺ�ǰ�����е��ַ�����name����ɾ���ո�Ҳ���ǻ�ȡÿһ�б��������֡�
  name = line[:equalsIndex].strip() ���Ƶ��ڵȺź�����ַ�����ȥ���ո�����ǰѵȺ�
  if line.rstrip().endswith('"'):
    params = line[equalsIndex + 1:].strip().strip('"').split()����ȥ����β�ġ�����
	�������ڵȺź����ֵ��ȥ����β�ġ���
    return name,params
  else:
    return name,line[equalsIndex + 1:].strip()ȥ���ո񡣷��ص������ͺ�������֣�Ҳ���ǲ�����

triggerLow = [] ���Ƶ����ޡ���һ���б�
triggerHigh = []

�����Ƕ�ȡ�����ļ���Ȼ��������дһ�������ļ���Ŀ����ÿ�ζ�Ҫ��һ���µ��ļ���

for name, params in [get_params(l) for l in lines]: ���������涨��ĺ�����#forѭ����仹��Ҫ��ǿѧϰ��


  print(name,params)�������
  if name == "names":
    nameList = params ����������һ���Ǳ�����һ���Ƿ�֧��Ϣ
    names = ",".join(["time","x"]+params) 
	#����ǲ��������ļ��ĵ�һ�У�Ҳ��CSV�ļ��ı�ͷ������������֧����������ʱ���X����������
    nameIndexs = {}#����һ���ֵ�
    for i in range(len(params)):#paramsӦ����һ���б��Ԫ�飬len�������Ԫ����Ԫ�صĸ�����
      nameIndexs[params[i]] = i #����ֵ�Ĺؼ��������ֵĲ�����ֵ����š�
	  #����һ���ֵ䣬�ǲ������Ͳ�������Ӧ�ı�ŵ��ֵ䡣���������ֵ�ĸ�ֵ��䡣�Բ�����Ϊ���������Ͳ���Ϊ��ֵ��
  elif name == "start":
    start = list(map(float, params)) #��Ԫ��ת��Ϊ�б�map�����ú�������ÿһ����������ɸ��������ݡ�
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
  #��ȡ�ļ�������ôһ����ʶ������������ֵ��
  #���ǳ��������ļ��кܶ�����ֱ���������δ���
  #���ܰ����е����ֱ�ʶ�������ݶ�ȡ����ص��ļ��С�
    header = params
  elif name == "value":
    temp_value = float(params) ÿһ�ε�value�ǲ�ͬ�ģ����ԣ������ʱ�ı���Ҳ�ǲ�ͬ�ġ�
    if header == "x":����ط������˲����ı仯��������滹����Ҫ��һ�������ġ�
      xStart = temp_value - startTime * xDt
    elif header in nameIndexs:
      j = nameIndexs[header]
	  #����j��һ��������
      start[j] = temp_value - startTime * dt[j]��ÿ��ѭ�������仯���Ӷ�valueҲ��仯��Ҳ���Ƿ�֧���ͱ�������仯��
	  #��һ�εĺ����ǣ��жϷ�֧�������������֧��X����仯xStart����ֵ�������ֵ��x��ֵ��ء�������������ģ����֧���߱��������ͱ俪ʼʱ�䡣
	  #start��һ���б������֧���߱��������ˣ���������ʼֵ�仯��
	  ������ظ��ģ��ͻḲ�ǡ�

print(names,file=outFile)  
#�����п���������д�����ļ��������ļ���д��������Ҫ��һ��ѧϰ�������ǰѱ�ͷд��ȥ�ˡ�
#Ҳ����time��X����֧���Լ��õ�������

#timeDelta = (endTime - startTime)/timesteps

if len(triggerLow) > 0 and len(triggerHigh) > 0: �жϣ��ߡ��ʹ������Ƿ���ڡ�����ֵ���߼����Ʊ�����
  hasTrigger = True
else:
  hasTrigger = False

triggerVariable = ""
triggerValue = 0.0

for i in range(0,timesteps+1):  ���������дcsv�ļ�����0��ʼ��ѭ���������ļ�������д�ļ���ѭ��10����
#Ӣ���Ѿ��޸��ˣ��������ڵĿ����߼��ǣ����û�з�����ֹ��������ô������10�����������Ƿ�ﵽ�����еĽ���ʱ�䡣

  shouldBreak = False
  time = startTime + timeDelta * i   ʱ����ڿ�ʼʱ����ϲ������ۼ�ʱ�䣬���ﲽ����1.���ԣ��������ö�����û��Ӱ�졣
  x = xStart + xDt * time   x=��ʼ+ʱ����Ա仯����x=1.0+0.1*time
  print(time, end=",", file=outFile)  ͨ�����ԣ����������д�ļ���дÿ��det�ļ������csv�ļ������ҿ������ӡ�
  print(x, end="", file=outFile)
  for j in range(0,min(len(start),len(dx),len(dt))):
    print(end=",", file=outFile)
    value = start[j] + time*dt[j] + x*dx[j] һ���б���ۼӡ���ǰʱ����Ա仯��+��ǰ��ֵ*��ֵ�仯����

	��֧ʱ���������
    print(value, end="", file=outFile)
    if hasTrigger:
      if triggerLow[j] < value < triggerHigh[j]: ������жϷ�֧��������
	  trigger_low = "12.0 5.0"
      trigger_high = "12.1 5.1"
	  �������ֵ���������б�����ߺ����֮�䣬���֧��
        shouldBreak = True
        triggerVariable = nameList[j] 
		#���Ӧ����ָ��֧��Ϣ��������Ҳ���Ǵ�����֧�Ĳ�����������֮һ��
		#branchChangedParam������DET�еķ�֧����
		#triggerVariable���������еĴ�������������������һ�µġ���������δ��ݵĲ�����
        triggerValue = value
  print(file=outFile)
  if shouldBreak:
    break


#print([x + endDxi for endDxi in endDx],endProbability)

outFile.close()

if len(triggerVariable) == 0: �������ֵ�ڳ�������֮�䣬�򴥷���֧����x��
#����184�жϵ�������ֻ�з�֧�ˣ��ŶԴ������������и�ֵ��������ǿգ��������㡣

  triggerVariable = "x"
  triggerValue = x  ����֧���ݺͱõ����������������ǣ�����x��Ϊ��֧������
  ���������ÿһ�ε��õĵ�һ�ξ�ȷ���ġ���Ϊ��һ�ε���ʱ������x��x�仯�Ժ���Ϊ��������
  �Ѿ���ֵ���Ͳ����ٽ��и�ֵ�ˡ�Ҳ����ֻ��һ�η�֧������������ֻ���ڵ�һ����

if time < endTime: ����ʱ�䡣��һ����ʲô���أ�
#�о���������ڲ���DET��֧�ļ��Ĳ��֡��Ʋ�����������ʱ�䲻��������ʱ�䣬��ͼ�����֧���㡣��
#��һ�������ļ�Ϊ������
  root = ET.Element('Branch_info') ����һ��ET�е�һ������
  root.set("end_time", str(time)) 
  triggerNode=ET.SubElement(root,"Distribution_trigger")
  triggerNode.set("name", triggerName)#������õ��ǳ�����һ��������ơ�
  var = ET.SubElement(triggerNode,'Variable')#�����ָ�������ı�������
  var.text=triggerVariable
  ���Ӧ���Ƕ�DET���һ����ֵ���²��ǰѴ�������������������ֵ��������
  ���涼�����������ԡ�
  var.set('type', "auxiliary") ����һ��������ϣ�
  var.set('old_value', str(triggerValue))�����ܶ����ֵ䣬����ֵ��Ӧ�����ԣ�old_value���Ǵ�����ֵ��
  �������������ݿ�����������档
  var.set('actual_value', " ".join([str(v) for v in [triggerValue + endDxi for endDxi in endDx]]))
  ����Ƿ�֧��һ���ж��������о���ʵ�ʵ�ֵ�Ǵ���ֵ���ټ���������
  #���ڸ�����ˣ�����ʵ������ô���أ�������Ǹ��������ˣ�
  #v��p����һ��ָʾ�Եı���������ѭ���ı�����
  #��������һ���ֵ䣬ʵ��ֵ��һ������������ֵ��һ���ַ����͵����ݣ�
  var.set('probability', " ".join([str(p) for p in endProbability]))��仰������
  #��仰�ĺ����ǣ�����p�����ӽ��������е���ֵ�����Ĳ��ԡ�
  #����������ÿո� �ѽ������ʵ���ֵ���������������


  xmlFile = open(os.path.join(head,prefix+tail+"_actual_branch_info.xml"),"w")  дһ��XML�ļ����������ļ�����û�п�����

     #Done parsing C:\msys64\home\wangh\projects\raven\tests\framework\Samplers\DynamicEventTrees\DETshort\DETrunTest\DET_test_1\
	# out~simple_det_test_actual_branch_info.xml

    û�п�����ԭ������DETĬ�ϳ����п���ɾ���ˡ����Ե���һ�¡�
  ���Գ��������ᵽ�������actual���xml�ļ������֧�����򲻷�֧��
  xmlFile.write(minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent="\t"))
  xmlFile.close()
