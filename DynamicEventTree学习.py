# Copyright 2017 Battelle Energy Alliance, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0 看不懂动态事件树的逻辑，还得看这个程序。
方法是一方面，程序实现是另外一方面。
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
  This module contains the Dynamic Event Tree and
  the Hybrid Dynamic Event Tree sampling strategies
  这个程序包括两个部分，一个是动态事件树，一个是混合动态事件树。可以作为攻关的基础。尽管

  架构是不一样的。可以看raven是如何实现调用的过程的。是一个学习的重点。
  看懂了DET的简单的例子，但是看不懂概率是如何生成的，因为没有relap7，所以无法尝试其他带有relap7的测试程序。还是蛮复杂的。
  还是应该看懂这个程序，应该是有一定的帮助。
  2019年5月30日，又看了一遍。有了一定的新的收获。但是还是没有完全的弄懂。到底是如何运行的呢？

  Created on May 21, 2016
  @author: alfoa
  supercedes Samplers.py from alfoa
  超级代码，抽样器，也是alfoa开发的？
"""
#for future compatibility with Python 3--------------------------------------------------------------
from __future__ import division, print_function, unicode_literals, absolute_import
import warnings
warnings.simplefilter('default',DeprecationWarning)
#End compatibility block for Python 3----------------------------------------------------------------

#External Modules------------------------------------------------------------------------------------
import sys
import os
import copy 这个适用于深拷贝和浅拷贝的
from operator import mul #mul模块是乘法的方法。operator是一个运算的模块。
#python标准库之operator（运算符模块） operator模块提供了一系列与Python自带操作一样有效的函数。
#例如：operator.add(x, y)和表达式x+y是等效的。那些特殊类的方法都有自己的函数名；
#为了方便起见，一些函数名是没有前导和后置（_）。 operator模块是用c实现的，所以执行速度比python代码快。
from functools import reduce
#reduce() 函数会对参数序列中元素进行累积。
#函数将一个数据集合（链表，元组等）中的所有数据进行下列操作：用传给 reduce 中的函数 function（有两个参数）
#先对集合中的第 1、2 个元素进行操作，得到的结果再与第三个数据用 function 函数运算，最后得到一个结果。
import xml.etree.ElementTree as ET#这是一个用于解析XML文件的语句。可以读取XML的节点，属性，并进行编辑修改等内容。
import itertools #这是一个迭代器。
from collections import Counter #其中Counter中文意思是计数器，也就是我们常用于统计的一种数据类型
#External Modules End--------------------------------------------------------------------------------
外部模块都都应该是可以理解的。当引用上述功能时，我们应该查找相关的模块，去看一下他的功能。


#Internal Modules------------------------------------------------------------------------------------
from .Grid import Grid  内部模块。在framework 中的sample文件夹里面有。
from .MonteCarlo import MonteCarlo  蒙卡在framework 中的sample文件夹里面有。
from .Stratified import Stratified  策略在framework 中的sample文件夹里面有。
from .Sampler import Sampler   抽样在framework 中的sample文件夹里面有。
from utils import utils   公共模块，在framework 中的utils文件夹中
from utils import InputData  公共模块，在framework 中的utils文件夹中
import utils.TreeStructure as ETS  公共模块，在framework 中的utils文件夹中
#Internal Modules End-------------------------------------------------------------------------------

class DynamicEventTree(Grid):  这是一个类的定义。可以把这个动态事件树的类进行实例化。以及操作一些方法。传递的参数是grid。
                            因为这里有一个Grid，这个本身就是一个类。所以，需要了解grid的类的情况。
#   grid不知道有什么属性。也是一个函数。
  """
  DYNAMIC EVENT TREE Sampler (DET)  这是一个类。一个动态事件树的类。
  """

  @classmethod  这个是装饰器，表明是一个类的方法。这是一个标识类属性的。
  def getInputSpecification(cls):定义了一个利用类的输入来获取特定信息的函数。说明这是类属性。
    """
      Method to get a reference to a class that specifies the input data for
      class cls.
      @ In, cls, the class for which we are retrieving the specification  输入从cls的类里面获得特殊的信息。
      @ Out, inputSpecification, InputData.ParameterInput, class to use for
        specifying input of cls.   输出是输入的说明，输入的数据，以及输入的类型。
		猜测是类似于relap仿真，这里是把输入历史存放于一个结构中，然后再根据需要去变换。
    """
    inputSpecification = super(DynamicEventTree, cls).getInputSpecification()  

    inputSpecification.addParam("printEndXmlSummary", InputData.StringType) 这个是传递设置的参数。通过DET的XML文件及属性。
    inputSpecification.addParam("maxSimulationType", InputData.FloatType)
    inputSpecification.addParam("removeXmlBranchInfo", InputData.StringType)

    oldSub = inputSpecification.popSub("Distribution")
    newDistributionInput = InputData.parameterInputFactory("Distribution", baseNode=oldSub) 这个参数是传递的XML文件中的分布的信息。
    gridInput = InputData.parameterInputFactory("grid", contentType=InputData.StringType) 

    gridInput.addParam("type", InputData.StringType)  这个是给DET的函数赋值。这里是CDF还是value不同。
    gridInput.addParam("construction", InputData.StringType) 这个是等步长还是自定义。
    gridInput.addParam("steps", InputData.IntegerType)  这个是步长信息。

    newDistributionInput.addSub(gridInput) 
    inputSpecification.addSub(newDistributionInput)

    #Strict mode off because basically this allows things to be passed to
    # sub Samplers, which will be checked later.
    hybridSamplerInput = InputData.parameterInputFactory("HybridSampler", strictMode=False)  这里是混合抽样输入
    hybridSamplerInput.addParam("type", InputData.StringType)

    for nodeName in ['variable','Distribution']:#这种函数如何循环，这个是在XML树形结构的子节点中循环。
      nodeInput = InputData.parameterInputFactory(nodeName, strictMode=False)
      nodeInput.addParam("name", InputData.StringType)
      hybridSamplerInput.addSub(nodeInput)
    inputSpecification.addSub(hybridSamplerInput)

    return inputSpecification

  def __init__(self):初始化部分？
    """
    Default Constructor that will initialize member variables with reasonable
    defaults or empty lists/dictionaries where applicable.

    @ In, None
    @ Out, None
    """
    Grid.__init__(self)  这是一个DET类传递的网格的参数的属性初始化。grid本身就是一个类。需要初始化。
	这里还要看一下Grid的初始化的内容。
    # Working directory (Path of the directory in which all the outputs,etc. are stored) 
    self.workingDir                        = "" 这个是输出的地址
    # (optional) if not present, the sampler will not change the relative keyword in the input file
    self.maxSimulTime                      = None 选择性的属性。
    # print the xml tree representation of the dynamic event tree calculation
    # see variable 'self.TreeInfo'
    self.printEndXmlSummary                = False 这是初始值。
    # flag to control if the branch info xml file needs to be removed after reading   设置XML文件是否删除。没有成功。
     通过尝试，这个部分不能修改。也就是分支的XML文件一定会被删除的。
    self.removeXmlBranchInfo               = True 
    # Dictionary of the probability bins for each distribution that have been 每一个使用的分布的以概率片存储的字典。
    #  inputted by the user ('distName':[Pb_Threshold_1, Pb_Threshold_2, ..., Pb_Threshold_n])
    self.branchProbabilities               = {}  这个函数代表分支概率。分支的概率。是通过数值或者函数反差的概率。
	#分支概率是一个字典。是1：分支概率 1：分支概率这种形式。
    # Dictionary of the Values' bins for each distribution that have been
    #  inputted by the user ('distName':[Pb_Threshold_1, Pb_Threshold_2, ..., Pb_Threshold_n])
	#这个是分布的概率阈值，distName这个的类型是什么？是分布名称吗？还是分布参数的名字？

    # these are the invCDFs of the PBs inputted in branchProbabilities (if ProbabilityThresholds have been inputted)

    self.branchValues                      = {}这个是分支的值。
    # List of Dictionaries of the last probability bin level (position in the array) reached for each distribution ('distName':IntegerValue)
	#分支数值。形式分布名称+一个整数。这里的含义是达到每一个分布最后一个概率离散区域的值。是每一个分支区域中最后边界上的值。
    # This container is a working dictionary. The branchedLevels are stored in the xml tree "self.TreeInfo" since they must track
    # the evolution of the dynamic event tree
	#这个函数是指工作的文件间。dictionary这里的level信息在self.treeinfo中。
    self.branchedLevel                     = []
    # Counter for the branch needs to be run after a calculation branched (it is a working variable) 计算分支计算以后的分支数目。
	#这个变量是分支水平？记录计算以后需要分支的层级。问题是这个是如何判断的？实际上是一个分布变量参数。
    self.branchCountOnLevel                = 0
    # Dictionary tha contains the actual branching info
    # (i.e. distribution that triggered, values of the variables that need to be changed, etc)
	#实际分支信息，包括触发的分布、需要变化的变量的值等。
    self.actualBranchInfo                  = {} 包含分支信息的字典。
    # Parent Branch end time (It's a working variable used to set up the new branches need to be run.
	#通过这个描述，RAVEN是通过时间来对DET的分支进行控制。
    #   The new branches' start time will be the end time of the parent branch )
	#父节点结束时间，新节点的开始时间就是父节点结束的时间。
    self.actualEndTime                     = 0.0
    # Parent Branch end time step (It's a working variable used to set up the new branches need to be run.
    #  The end time step is used to construct the filename of the restart files needed for restart the new branch calculations)
	#结束时间“步长”，用于构建文件名，这个文件用于重新启动新的分支计算？
    self.actualEndTs                       = 0
    # Xml tree object. It stored all the info regarding the DET. It is in continue evolution during a DET calculation
	#TreeInfo是一个XML的数据对象。存储了所有DET相关的信息，每一次DET的计算都会继续演化。

    self.TreeInfo                          = None
    # List of Dictionaries. It is a working variable used to store the information needed to create branches from a Parent Branch
	#一个列表，记录父节点信息，并用于子节点的分支？

    self.endInfo                           = []
    # Queue system. The inputs are waiting to be run are stored in this queue dictionary
	#是一个字典，存储序列系统，从下一个命令可以看出来，这个字典的键中包含了识别符类似于DET1-1等
    self.RunQueue                          = {}
    # identifiers of the inputs in queue (name of the history... for example DET_1,1,1)
	#这事一个标识符，是一个列表。这种范式表示的是一个字典的键。
    self.RunQueue['identifiers']           = []
    # Corresponding inputs
    self.RunQueue['queue']                 = []
    # mapping from jobID to rootname in TreeInfo {jobID:rootName}
	#映射，从工作ID，如DET_test_1-1-2-3-3，到TreeInfo中根的名称。
    self.rootToJob                         = {}
    # dictionary of Hybrid Samplers available
    self.hybridSamplersAvail               = {'MonteCarlo':MonteCarlo,'Stratified':Stratified,'Grid':Grid}
	#这种字典的赋值，包括键和值。确定了只有三种方法。这是一个现有的类别，就是只有浙西。
    # dictionary of inputted hybridsamplers need to be applied
	#需要应用的混合抽样的字典。这个是实际上应用的混合抽样方法。
    self.hybridStrategyToApply             = {}
    # total number of hybridsampler samples (combination of all different hybridsampler strategy)
	#抽样总的次数。
    self.hybridNumberSamplers              = 0
    # List of variables that represent the aleatory space
	#一个列表。列出所有DET中处理的参数。也就是标准的DET的此参数，是名称吗？通过下面的推测，应该是变量的名字。
    self.standardDETvariables              = []
    # Dictionary of variables that represent the epistemic space (hybrid det). Format => {'epistemicVarName':{'HybridTree name':value}}
	#按照字典的形式，给出认知不确定性参数，以及混合抽样的名称及数值。这里的数值是什么？这个是任务不确定性参数。
    self.epistemicVariables                = {}

  def _localWhatDoINeed(self): 这是一个在sample中定义的方法。
    """
      This method is a local mirror of the general whatDoINeed method.
	  def是函数，也是一种方法。一种我需要什么的方法？
      It is implmented here because this Sampler requests special objects
      @ In, None
      @ Out, needDict, dict, dictionary of objects needed
    """
    needDict = Sampler._localWhatDoINeed(self) 
	#这里应用了抽样器里的一个方法。将他复制给needDict。代表了一个选择的分布方法，Dict是分布类别。
	#猜测needDict是需要抽样的分布。
    for hybridsampler in self.hybridStrategyToApply.values():
	#这里是将混合抽样方法中的值得循环，赋给抽样器？
      preNeedDict = hybridsampler.whatDoINeed()
      for key,value in preNeedDict.items():这是一个关于字典的循环。
        if key not in needDict.keys():
          needDict[key] = []
        needDict[key] = needDict[key] + value
		#这句话不是很明白，或者猜测value就是分布类型。
    return needDict

  def localStillReady(self, ready):
    """
      first perform some check to understand what it needs to be done possibly perform an early return
	  第一次检查。明白了这个函数。这个函数就是为什么在工作目录中仅有的一个总结性的XML文件。就是一个尝试。
	  但是调试以后，不知道为什么都修改了。
	  感觉是在写一个总结的XML文件的过程。
      ready is returned
      @ In,  ready, bool, a boolean representing whether the caller is prepared for another input.
	  输入是一个布尔逻辑。代表调用是否准备好了。
      @ Out, ready, bool, a boolean representing whether the caller is prepared for another input.
    """
    self._endJobRunnable = max((len(self.RunQueue['queue']),1))
	#猜测是当前计算序列中是否还有计算序列。
    if(len(self.RunQueue['queue']) != 0 or self.counter == 0):
	#
      ready = True
    else:
      if self.printEndXmlSummary: 这是一个逻辑判断。因为printEndXmlSummary是一个逻辑变量。并且可以写文件。
        myFile = open(os.path.join(self.workingDir,self.name + "11_outputSummary.xml"),'w') 
		成功试验。就是这个地方。通过一个参数来控制这个变量的输出。具体格式就需要看树结构的知识了。
		这是建立一个文件，通过打开的方式，是一个xml文件。通过路径的方式，在制定的路径和名称建立一个文件。 
        for treeNode in self.TreeInfo.values():
		     #treeNode是一个在treeinfo.value中的一个方法，里面有一些属性？
          treeNode.writeNodeTree(myFile)
        myFile.close()
      ready = False
    return ready

  def _retrieveParentNode(self,idj):
    """
      Grants access to the parent node of a particular job
      @ In, idj, string, the identifier of a job object
	  输入是一个job的字符串。
      @ Out, parentNode, TreeStructure.Node, the parent node of the job linked to idj
	  每一个job都有一个ID，而对应每一个ID都有一个树形结构。保存了一些信息。
	  输出是父节点，一个树形结构。
    """
    if(idj == self.TreeInfo[self.rootToJob[idj]].getrootnode().name):
	#可以看到这么多的方法。最上层的是树的信息，然后是获得ID。如果传递的参数相等，就把属性结构的信息
	#传递给父节点。
      parentNode = self.TreeInfo[self.rootToJob[idj]].getrootnode()

    else:
      parentNode = list(self.TreeInfo[self.rootToJob[idj]].getrootnode().iter(idj))[0]
	  #如果不能匹配，则还是会赋值，这个是什么含义呢？
    return parentNode

  def localFinalizeActualSampling(self,jobObject,model,myInput,genRunQueue=True):
    """
      General function (available to all samplers) that finalize the sampling
      calculation just ended.这是一个通用的方法或者方程，每一个抽样器都可以用。去
	  finalize是什么意思？
	  In this case (DET), The function reads the
      information from the ended calculation, updates the working variables, and
      creates the new inputs for the next branches
	  非常重要的1个环节。主要是完成新的分支信息的生产。
	  从结束的计算中读取信息，更新工作变量，然后为新的分支产生一个新的变量。
      @ In, jobObject, instance, an instance of a JobHandler 一个调度器的实例化
      @ In, model, model instance, it is the instance of a RAVEN model
      @ In, myInput, list, the generating input  # myinput是一个列表，代表了一个输入
      @ In, genRunQueue, bool, optional, True if the RunQueue needs to be updated
      @ Out, None
    """
    self.workingDir = model.workingDir  
	#这是获得模型的工作目录。也就是可执行程序的目录。
    # returnBranchInfo = self.__readBranchInfo(jobObject.output)
    # Get the parent element tree (xml object) to retrieve the information needed to create the new inputs
	#获得父节点的信息。
    parentNode = self._retrieveParentNode(jobObject.identifier)
	#jobObject是一个调度器的实例，其中的标识符。job调度器传递的识别符。
    # set runEnded and running to true and false respectively
	#设置结束条件。但是没有判断，没有逻辑值，直接判断？
    parentNode.add('runEnded',True)
    parentNode.add('running',False)
    parentNode.add('endTime',self.actualEndTime)
	#这些都是树形节点的属性。都是字典。用add去增加。或则是更新。add应该是进行设置的意思。
    # Read the branch info from the parent calculation (just ended calculation)
    # This function stores the information in the dictionary 'self.actualBranchInfo'，说明当前的分支信息是一个字典性数据结构？
    # If no branch info, this history is concluded => return

    ## There are two ways to get at the working directory from the job instance
    ## and both feel a bit hacky and fragile to changes in the Runner classes.
    ## They are both listed below and the second inevitably stems from the first.
    ## I am wondering if there is a reason we cannot use the model.workingDir
    ## from above here? Granted the job instance should have a snapshot of
    ## whatever the model's current working directory was for that evaluation,
    ## and it could have changed in the meantime, so I will keep this as is for
    ## now, but note this should be re-evaluated in the future. -- DPM 4/12/17
    # codeModel = jobObject.args[0] 对于调度器这个属性，就是code的类型。
    # jobWorkingDir = codeModel.workingDir
    kwargs = jobObject.args[3]
	#从下面猜测，上面这个应该是一个列表。
    stepWorkingDir = kwargs['WORKING_DIR']
    jobWorkingDir = os.path.join(stepWorkingDir,kwargs['prefix'] if 'prefix' in kwargs.keys() else '1')

    ## This appears to be the same, so I am switching to the model's workingDir
    ## since it is more directly available and less change to how data is stored
    ## in the args of a job instance. -- DPM 4/12/17
    # jobWorkingDir = self.workingDir

    if not self.__readBranchInfo(jobObject.getMetadata()['outfile'], jobWorkingDir):
      parentNode.add('completedHistory', True)
      return False
    # Collect the branch info in a multi-level dictionary 将分支信息存储与一个多维字典？？
    endInfo = {'endTime':self.actualEndTime,'endTimeStep':self.actualEndTs,'branchDist':list(self.actualBranchInfo.keys())[0]}
    endInfo['branchChangedParams'] = self.actualBranchInfo[endInfo['branchDist']]
	# self.actualEndTs这是一个结束时间的步长？
    # check if RELAP7 mode is activated, in case prepend the "<distribution>" string
    if any("<distribution>" in s for s in self.branchProbabilities.keys()):
      endInfo['branchDist'] = list(self.toBeSampled.keys())[list(self.toBeSampled.values()).index(endInfo['branchDist'])]
	  #toBeSampled 是一个字典，包含了抽样参数和参数服从的分布。
      #endInfo['branchDist'] = "<distribution>"+endInfo['branchDist']
	  #确实是这种格式。
    parentNode.add('actualEndTimeStep',self.actualEndTs)
    # # Get the parent element tree (xml object) to retrieve the information needed to create the new inputs
	#获得父节点信息后，生成新的子节点。
    # if(jobObject.identifier == self.TreeInfo[self.rootToJob[jobObject.identifier]].getrootnode().name):
	#
	#endInfo['parentNode'] = self.TreeInfo[self.rootToJob[jobObject.identifier]].getrootnode()
    # else: endInfo['parentNode'] = list(self.TreeInfo[self.rootToJob[jobObject.identifier]].getrootnode().iter(jobObject.identifier))[0]
    endInfo['parentNode'] = parentNode
    # get the branchedLevel dictionary
    branchedLevel = {}  这种是字典，[]是列表，（）是元组，{}是字典，存在key和数值两种一对一的关系。
	#这里给出的是父节点中抽样参数名和数值。
    for distk, distpb in zip(endInfo['parentNode'].get('SampledVarsPb').keys(),endInfo['parentNode'].get('SampledVarsPb').values()):
	#zip的作用是把两个参数打包成一个元祖。然后循环。也就是循环抽样参数的键和数值进行循环？
      if distk not in self.epistemicVariables.keys():#这里是说是否有混合抽样的关键字。
	  #如果输入的不确定性参数的键与需要抽样的键不一致，或者没有。
	  #这里是字典的key
        branchedLevel[distk] = utils.index(self.branchProbabilities[distk],distpb)
		#分支水平是分支概率
    if not branchedLevel:
      self.raiseAnError(RuntimeError,'branchedLevel of node '+jobObject.identifier+'not found!')
    # Loop of the parameters that have been changed after a trigger gets activated
	#当触发器激活以后，循环改变的参数。
    for key in endInfo['branchChangedParams']: #这个就是分支的参数。是一个字典，应该是有很多的参数和数值吧。
	#计算程序中，为什么有的时候是X有的时候是泵的流量呢？通过一个属性结构变量，通过triggerNode这个里面的类来定义？
	#上面的问题已经看懂了。问题是方法是否通用。
	#  var = ET.SubElement(triggerNode,'Variable')这里是我增加的程序。
     #var.text=triggerVariable
      endInfo['n_branches'] = 1 + int(len(endInfo['branchChangedParams'][key]['actualValue']))
	  #哈哈哈，有看懂了一个地方。判断有几个分支的地方是在这里。这个数值对后面的实际分支是有影响的。上限是3。不知道为什么
	  #与实际的分支参数的数组的长度是有关的。
	  #我是不是缺少了计算机思维。刚才产生一个问题，就是说如果有两个参数要分支，那么分支程序是否能够适应。
	  #而这个对于计算机来说方法是不变的，而仅仅变得是分支的条件而已。因此，这个方法是通用的，具体是需要在自己的程序中进行控制。也就是
	  #利用不同的判断条件，传递需要分支的参数，并保存信息即可。至于其他数据还是处于保持的状态？
	  #外部程序可以自己产生判断条件，但是概率分支如何产生判断条件？
      if(len(endInfo['branchChangedParams'][key]['actualValue']) > 1):
        #  Multi-Branch mode => the resulting branches from this parent calculation (just ended)
        # will be more then 2
		#这里的含义是说，如果变化的参数值得类别大于1，也就是至少等于2，那么分支就是至少3个。
		#这里的逻辑是否是，其中一个状态是保持不变？
        # unchangedPb = probability (not conditional probability yet) that the event does not occur
		#不变化的概率=事件不发生的概率。但不是条件概率。？
        unchangedPb = 0.0
        try:
          # changed_pb = probability (not conditional probability yet) that the event A occurs and the final state is 'alpha' """
		  #变化的概率=就是分支概率？
          for pb in range(len(endInfo['branchChangedParams'][key]['associatedProbability'])):
		  #非常重点的部分。有一个循环。变化参数状态的相关概率。这个循环是一个循环次数。取决于上面相关概率中的多少。
            unchangedPb = unchangedPb + endInfo['branchChangedParams'][key]['associatedProbability'][pb]
			#不变的概率=一个累加过程。是变化参数的相关概率的列表的所有加和。
			#这是一个循环累加，不变化的概率=associatedProbability*一个倍数？不是倍数，是一个累加的循环。
        except KeyError:
          self.raiseAWarning("KeyError:"+str(key))
        if(unchangedPb <= 1):
          endInfo['branchChangedParams'][key]['unchangedPb'] = 1.0-unchangedPb
		  #赋值语句，如果求得的不变化的概率小于1.那么将这个值赋给数据结构。
		  #问题：这里是否存在逻辑错误。为什么要用1减一下呢？
        else:
          self.raiseAWarning("unchangedPb > 1:"+str(unchangedPb))
      else:
        # Two-Way mode => the resulting branches from this parent calculation (just ended) = 2
		#这里是二分支条件。也就是父节点数据不变以及变化的过程。
        if branchedLevel[endInfo['branchDist']] > len(self.branchProbabilities[endInfo['branchDist']])-1:
		#如果这样比较，那么分支水平这个是一个整数？不知道什么含义。
          pb = 1.0
        else:
          pb = self.branchProbabilities[endInfo['branchDist']][branchedLevel[endInfo['branchDist']]]
		  #从下面的描述判断，这个应该是一个概率值。但这是一个什么数据结构呢？
        endInfo['branchChangedParams'][key]['unchangedPb'] = 1.0 - pb
        endInfo['branchChangedParams'][key]['associatedProbability'] = [pb]
		#不变的概率和相关或叫协助概率的和是1.实际运行结果不是？回答，实际结果是这样的。关键是怎么取分支中的概率。
		#也就是是elf.branchProbabilities的具体结构。
    self.branchCountOnLevel = 0
    # # set runEnded and running to true and false respectively
    # endInfo['parentNode'].add('runEnded',True)
    # endInfo['parentNode'].add('running',False)
    # endInfo['parentNode'].add('endTime',self.actualEndTime)
    # The branchedLevel counter is updated 设置初始值
    if branchedLevel[endInfo['branchDist']] < len(self.branchProbabilities[endInfo['branchDist']]):
      branchedLevel[endInfo['branchDist']] += 1
	  #从这个表达式推断，branchedLevel[endInfo['branchDist']]是一个列表的值？
    # Append the parent branchedLevel (updated for the new branch/es) in the list tha contains them
    # (it is needed in order to avoid overlapping among info coming from different parent calculations)
    # When this info is used, they are popped out
    self.branchedLevel.append(branchedLevel)
    # Append the parent end info in the list tha contains them
    # (it is needed in order to avoid overlapping among info coming from different parent calculations)
    # When this info is used, they are popped out
    self.endInfo.append(endInfo)
    # Compute conditional probability
    self.computeConditionalProbability()  后面有专门的计算条件概率的函数。
    # Create the inputs and put them in the runQueue dictionary (if genRunQueue is true)
    if genRunQueue:
      self._createRunningQueue(model,myInput)
    return True

  def computeConditionalProbability(self,index=None):
    """
      Function to compute Conditional probability of the branches that are going to be run.
      The conditional probabilities are stored in the self.endInfo object
	  非常重点的一段代码，计算分支发生是的条件概率。这个概率存储在结束信息的对象里面。endinfo对象里面。
      @ In, index, int, optional, position in the self.endInfo list (optional). Default = 0
      @ Out, None
    """
    if not index:
      index = len(self.endInfo)-1
	  #len(self.endInfo)代表的是一个什么长度呢？是有多少实例？对的，这个含义就是一个方法中有多少个实例对象。可能方法
	  #都是endInfo，但是里面的标识符可能是不同的吧。
    try:一个异常的处理。
      parentCondPb = self.endInfo[index]['parentNode'].get('conditionalPbr')
	  #通过endInfo的一个方法中的子类，获得父节点的条件概率。
      if not parentCondPb:
        parentCondPb = 1.0
    except KeyError:
      parentCondPb = 1.0
    # for all the branches the conditional pb is computed
    # unchangedConditionalPb = Conditional Probability of the branches in which the event has not occurred
    # changedConditionalPb   = Conditional Probability of the branches in which the event has occurred
    for key in self.endInfo[index]['branchChangedParams']:
      self.endInfo[index]['branchChangedParams'][key]['changedConditionalPb'] = []
      self.endInfo[index]['branchChangedParams'][key]['unchangedConditionalPb'] 
	                      = parentCondPb*float(self.endInfo[index]['branchChangedParams'][key]['unchangedPb'])
						  #分支变化参数的不变概率是父节点的条件概率与当前节点的不变概率的乘积。
      for pb in range(len(self.endInfo[index]['branchChangedParams'][key]['associatedProbability'])):
	  #pb是一个整数。
        self.endInfo[index]['branchChangedParams'][key]['changedConditionalPb']
		      .append(parentCondPb*float(self.endInfo[index]['branchChangedParams'][key]['associatedProbability'][pb]))

  def __readBranchInfo(self,outBase=None,currentWorkingDir=None):
    """
      Function to read the Branching info that comes from a Model
	  在上面有一个调用。这个方法是读取从模型来的分支信息？可能是一个重点。
      The branching info (for example, distribution that triggered, parameters must be changed, etc)
      are supposed to be in a xml format
	  功能是读取来自于模型的分支信息，比如触发的分布，变更的参数等，这些是基于XML格式的文件。
      @ In, outBase, string, optional, it is the output root that, if present, 
	  is used to construct the file name the function is going to try reading.

      @ In, currentWorkingDir, string, optional, it is the current working directory.
	   If not present, the branch info are going to be looked in the self.workingDir
      @ Out, branchPresent, bool, true if the info are present (a set of new branches need to be run),
	        false if the actual parent calculation reached an end point
	  输出是布尔逻辑。如果是真，就是信息是有的。如果是假，则分支已经到达了终点。
    """
    # Remove all the elements from the info container
    del self.actualBranchInfo
    branchPresent = False
    self.actualBranchInfo = {}#给这个当前节点信息进行初始化。
    # Construct the file name adding the outBase root if present
    filename   = outBase + "_actual_branch_info.xml" if outBase else "actual_branch_info.xml"
	#outBase是一个选择项，如果选择，就用他构建读取的XML文件名，如果没有就利用默认的文件名。
    workingDir = currentWorkingDir if currentWorkingDir is not None else self.workingDir

    if not os.path.isabs(filename):
	#是一个判断语句，如果文件名是绝对路径，返回true
      filename = os.path.join(workingDir,filename)

    if not os.path.exists(filename):
	#判断文件名是否存在。如果存在则为true。
      self.raiseADebug('branch info file ' + os.path.basename(filename) +' has not been found. => No Branching.')
      return branchPresent
    # Parse the file and create the xml element tree object#如果存在一个分支信息，则产生新的分支XML文件。
    #try:
    branchInfoTree = ET.parse(filename)
	#猜测这个是xml解析的一个功能。把输入文件信息的句柄传递给分支信息树上。
    self.raiseADebug('Done parsing '+filename)
    root = branchInfoTree.getroot()
	#把XMl的树形结构的根元素赋给root。
    # Check if endTime and endTimeStep (time step)  are present... In case store them in the relative working vars
    #try: #Branch info written out by program, so should always exist.
	#判断是否分支文件中给了结束时间或结束步长。是否体现的是时间控制还是不长控制？
	#猜测，是否如果将分支条件改为等步长，则会由这个信息。而自定义变量则为运行时间？一个物理过程上的时间。
    self.actualEndTime = float(root.attrib['end_time'])
	#通过读取属性XML文件，把结束时间赋给函数。
    self.actualEndTs   = int(root.attrib['end_ts']) if  'end_ts' in root.attrib.keys() else -1
    #except? pass
    # Store the information in a dictionary that has as keywords the distributions that triggered
    for node in root: 
	#这个应该是一个ET库中的函数。就是循环树形结构中的元素或子节点。
      if node.tag == "Distribution_trigger":
        distName = node.attrib['name'].strip()
		#获取分布名称。
        self.actualBranchInfo[distName] = {}
        for child in node:
          self.actualBranchInfo[distName][child.text.strip()] =
		  {'varType':child.attrib['type'].strip(),'actualValue':child.attrib['actual_value'].strip().split(),
		  'oldValue':child.attrib['old_value'].strip()}
          if 'probability' in child.attrib:
            asPb = child.attrib['probability'].strip().split()
			#赋值辅助概率。
            self.actualBranchInfo[distName][child.text.strip()]['associatedProbability'] = []
            #self.actualBranchInfo[distName][child.text.strip()]['associatedProbability'].append(float(asPb))
            for index in range(len(asPb)):
              self.actualBranchInfo[distName][child.text.strip()]['associatedProbability'].append(float(asPb[index]))
			  #这个很关键的语句，没读懂。
      # we exit the loop here, because only one trigger at the time can be handled  right now
	  #非常重点的是，循环要出来，因为当前只有一个触发器可以激活。
	  #问题，如果有两个参数结果，将如何修改？
      break
    # remove the file
    if self.removeXmlBranchInfo:
      os.remove(filename) 为什么要把这个文件删除？
    branchPresent = True
    return branchPresent

  def _createRunningQueueBeginOne(self,rootTree,branchedLevel, model,myInput):
  #从含义说，这里是第一个节点？
    """
      Method to generate the running internal queue for one point in the epistemic
      space. It generates the initial information to instantiate the root of a
      Deterministic Dynamic Event Tree.
	  这是一个建立认知不确定性的方法。
      @ In, rootTree, Node object, the rootTree of the single coordinate in the epistemic space.

      @ In, branchedLevel, dict, dictionary of the levels reached by the rootTree mapped in the internal grid dictionary 
	  (self.branchProbabilities)
      @ In, model, Models object, the model that is used to explore the input space (e.g. a code, like RELAP-7)
	  这里写了一个可以动态事件树的模型
      @ In, myInput, list, list of inputs for the Models object (passed through the Steps XML block)
	  这里标注输入信息。通过step的XML模块解析的code需要的所有输入文件。
      @ Out, None
    """
    # add additional edits if needed
    model.getAdditionalInputEdits(self.inputInfo)

    precSampled = rootTree.getrootnode().get('hybridsamplerCoordinate')
	#这里应该是一个逻辑变量。
    rootnode    =  rootTree.getrootnode()
    rname       = rootnode.name
    rootnode.add('completedHistory', False)
	#通过分析知道add是设置的的意思，就是将一个树形结构的属性设置为一个值。
    # Fill th values dictionary in
    if precSampled:
      self.inputInfo['hybridsamplerCoordinate'  ] = copy.deepcopy(precSampled)
	  #将precSampled的值深度拷贝给这个值。从而两个是非常独立的变量，一个改变另一个不变。
    self.inputInfo['prefix'                    ] = rname
    self.inputInfo['initiatorDistribution'     ] = []
    self.inputInfo['PbThreshold'               ] = []
    self.inputInfo['ValueThreshold'            ] = []
    self.inputInfo['branchChangedParam'        ] = [b'None']
    self.inputInfo['branchChangedParamValue'   ] = [b'None']
    self.inputInfo['startTime'                 ] = -sys.float_info.max
	#这个第一步是初始化一个最大的系统时间，也就是第一步的时间。
    self.inputInfo['endTimeStep'               ] = 0
    self.inputInfo['RAVEN_parentID'            ] = "None"
    self.inputInfo['RAVEN_isEnding'            ] = True
    self.inputInfo['conditionalPb'             ] = [1.0]
    self.inputInfo['conditionalPbr'            ] = 1.0
    self.inputInfo['happenedEvent'             ] = False
    for key in self.branchProbabilities.keys():
      self.inputInfo['initiatorDistribution'].append(self.toBeSampled[key])
    #for key in self.branchProbabilities.keys():self.inputInfo['initiatorDistribution'].append(key.encode())
    for key in self.branchProbabilities.keys():
      self.inputInfo['PbThreshold'].append(self.branchProbabilities[key][branchedLevel[key]])
    #for key in self.branchProbabilities.keys():self.inputInfo['PbThreshold'].append(self.branchProbabilities[key][branchedLevel[key]])
    for key in self.branchProbabilities.keys():
      self.inputInfo['ValueThreshold'].append(self.branchValues[key][branchedLevel[key]])
    #for key in self.branchProbabilities.keys():self.inputInfo['ValueThreshold'].append(self.branchValues[key][branchedLevel[key]])
    for varname in self.standardDETvariables:
	#这个是一个列表，是一个随机不确定性，也就是DET分支的参数变量，这里是名称。目前，因该只有一个值。
      self.inputInfo['SampledVars'  ][varname] = self.branchValues[varname][branchedLevel[varname]]
	  #就是这个变量名第几个离散分支的数值。
      #self.inputInfo['SampledVars'  ][varname] = self.branchValues[self.toBeSampled[varname]][branchedLevel[self.toBeSampled[varname]]]
      self.inputInfo['SampledVarsPb'][varname] = self.branchProbabilities[varname][branchedLevel[varname] ]
	  #随机不确定性参数，第一个分区对应的概率值。
      #self.inputInfo['SampledVarsPb'][varname] = self.branchProbabilities[self.toBeSampled[varname]][branchedLevel[self.toBeSampled[varname]]]
    # constant variables
    self._constantVariables()
	#如果没有设置混合抽样，参数就是固定值。

    if precSampled:
      for precSample in precSampled:
        self.inputInfo['SampledVars'  ].update(precSample['SampledVars'])
        self.inputInfo['SampledVarsPb'].update(precSample['SampledVarsPb'])
    self.inputInfo['PointProbability' ] = reduce(mul, self.inputInfo['SampledVarsPb'].values())
	#reduce函数是把后面的迭代参数中的第一个参数和第二个参数，进行mul操作。也就是相乘，然后在于第三个数相乘。
	#一直到最后。
    self.inputInfo['ProbabilityWeight'] = self.inputInfo['PointProbability' ]
    self.inputInfo.update({'ProbabilityWeight-'+key.strip():value for key,value in self.inputInfo['SampledVarsPb'].items()})

    if(self.maxSimulTime):
	#Raven用于控制仿真时间的变量。
      self.inputInfo['endTime'] = self.maxSimulTime
	  #也就是如果到了指定的最大仿真时间，则输入信息中的结束时间就是最大时间。
    # Add the new input path into the RunQueue system
	#处理完以后，增加新的输入路径到计算队列系统中。
    newInputs = {'args':[str(self.type)], 'kwargs':dict(self.inputInfo)}
    for key,value in self.inputInfo.items():
      rootnode.add(key,copy.copy(value))
    self.RunQueue['queue'].append(newInputs)
	#根据前后文的含义，RunQueue是一个运行队列的字典，其中queue是一个键，值是整型。代表有几个队列。
	#append是在这个队列中增加元素？
    print(self.inputInfo['prefix'])#这应该是一个DET的标识符。
    self.RunQueue['identifiers'].append(self.inputInfo['prefix'])
    self.rootToJob[self.inputInfo['prefix']] = rname
    del newInputs
    self.counter += 1#计算器累加，作用是什么？

  def _createRunningQueueBegin(self,model,myInput):
    """
      Method to generate the running internal queue for all the points in
      the epistemic space. 
	  为在认知不确定性空间中的所有点，产生运行的内部队列。
	  It generates the initial information to
      instantiate the roots of all the N-D coordinates to construct multiple
      Deterministic Dynamic Event Trees.
      @ In, model, Models object, the model that is used to explore the input space (e.g. a code, like RELAP-7)
	  #需要了解，我们要分析一下有R7程序的测试，看看是什么样子。
      @ In, myInput, list, list of inputs for the Models object (passed through the Steps XML block)
      @ Out, None
    """
    # We construct the input for the first DET branch calculation'
    # Increase the counter
	#为第一个DET计算构建一个输入，累加计数器。
    # The root name of the xml element tree is the starting name for all the branches
    # (this root name = the user defined sampler name)
    # Get the initial branchedLevel dictionary (=> the list gets empty)
    branchedLevel = self.branchedLevel.pop(0)
    for rootTree in self.TreeInfo.values():
      self._createRunningQueueBeginOne(rootTree,branchedLevel, model,myInput)
	  #这就是一个调用的过程。

  def _createRunningQueueBranch(self,model,myInput,forceEvent=False):
    """
      建立一个运行的队列分支。非常重要的一个函数。
	  Method to generate the running internal queue right after a branch occurred
      It generates the the information to insatiate the branches' continuation of the Deterministic Dynamic Event Tree
	  产生一个辅助确定的DET计算的条件。混合DET就是说，每一次的DET是确定的DET，而不确定参数则在外面循环。
      @ In, model, Models object, the model that is used to explore the input space (e.g. a code, like RELAP-7)
	  输入一个模型，离散输入空降
      @ In, myInput, list, list of inputs for the Models object (passed through the Steps XML block)
	  通过stepXML文件，通过我的输入，列出需要输入模型的参数。比如抽样参数。
      @ In, forceEvent, bool, if True the events are forced to happen (basically, the "unchanged event" is not created at all)
	  这只一个布尔逻辑，如果为真，则时间强制发生。
      @ Out, None
    """
    # The first DET calculation branch has already been run'
	为什么说第一个DET计算分支已经运行了？因为有一个one的计算队列。
    # Start the manipulation:

    #  Pop out the last endInfo information and the branchedLevel
    branchedLevelParent     = self.branchedLevel.pop(0)
    endInfo                 = self.endInfo.pop(0)
    self.branchCountOnLevel = 0 #这是一个整型变量，可能值为0-2设置当前分支水平为0
    # n_branches = number of branches need to be run  有点像XML总结里面写的下面有多少个分支的部分。的内容
    nBranches = endInfo['n_branches']
    # Check if the distribution that just triggered hitted the last probability threshold .
	#检查是否触发的分布找到最后的概率阈值。
    # In case we create a number of branches = endInfo['n_branches'] - 1 => the branch in
    # which the event did not occur is not going to be tracked
    if branchedLevelParent[endInfo['branchDist']] >= len(self.branchProbabilities[endInfo['branchDist']]):
	#如果父节点中分支分布数量，大于实例化的分支分布。猜测说明已经达到了分布的最后一个阈值。
      self.raiseADebug('Branch ' + endInfo['parentNode'].get('name') + ' hit last Threshold for distribution ' + endInfo['branchDist'])

      self.raiseADebug('Branch ' + endInfo['parentNode'].get('name') + ' is dead end.')
      self.branchCountOnLevel = 1
      nBranches -= 1
    else:
      if forceEvent == True:
	  #后面有一个强制性的标识符，是强制分支。
        self.branchCountOnLevel = 1
        nBranches -= 1
    # Loop over the branches for which the inputs must be created
	在分支中循环？
    for _ in range(nBranches):#这是一个循环，nBranches是一个整型变量。从整体鲜花看，这个参数为3或2.
	      del self.inputInfo #先删除输入信息
      self.counter += 1 #计数器累加
      self.branchCountOnLevel += 1 #分支水平累加。
      branchedLevel = copy.deepcopy(branchedLevelParent)
	  #深度复制，将父节点的分支水平赋值给当前的节点。
      # Get Parent node name => the branch name is creating appending to this name  a comma and self.branchCountOnLevel counter
	  #非常重要，这个再设置演化的节点的文件名称。原理是通过获取父节点的标识符，然后加“_”再加上当前的分支水平的计数器。
	  #所以branchCountOnLevel是一个整数型变量，代表当前子节点分支的水平，一般就是1-3之间。
      rname = endInfo['parentNode'].get('name') + '-' + str(self.branchCountOnLevel)
	  #经过测试，已经理解了这个语句。rname是当前子节点的名称。
	  #这里可能是分层表示的一个函数。名字都是父节点的名字+“_”+分支的数量。但是分支的数量是如何确定的呢？
	  #分支数量是依靠nBranches来确定的。按照这个证书进行循环。
      # create a subgroup that will be appended to the parent element in the xml tree structure
	  #创建一个父节点元素XML文件中的子节点。
      subGroup = ETS.HierarchicalNode(self.messageHandler,rname)
	  #问题：这个函数不知道是什么意思。self.messageHandler也不知道什么意思。
      subGroup.add('parent', endInfo['parentNode'].get('name'))
	  #设置子节点中父节点的名
      subGroup.add('name', rname)
	  #设置子节点的名，已经有了分支了
      subGroup.add('completedHistory', False)
	  #既然已经有了子节点，那么完成的历史就是假。
      # condPbUn = conditional probability event not occur
      # condPbC  = conditional probability event/s occur/s
      condPbUn = 0.0
      condPbC  = 0.0
      # Loop over  branchChangedParams (events) and start storing information,
      # such as conditional pb, variable values, into the xml tree object
	  #循环分支参数，并存储概率。包括参数值，参数概率，以及参数名。
      branchChangedParamValue = []
      branchChangedParamPb    = []
      branchParams            = []
	  #这里是初始化子节点变化概率的列表，包括参数值，参数概率以及参数名称。是当前方法中的变量。先赋值在操作。
      #subGroup.add('branchChangedParam',endInfo['branchChangedParams'].keys())

      for key in endInfo['branchChangedParams'].keys():
        #subGroup.add('branchChangedParam',key)
        branchParams.append(key)
        if self.branchCountOnLevel != 1:#如果当前的分支水平不是1。1代表不变。那么等于2或者3.
          branchChangedParamValue.append(endInfo['branchChangedParams'][key]['actualValue'][self.branchCountOnLevel-2])
		  #branchChangedParamValue.append(endInfo['branchChangedParams'][key]['actualValue'][0或者1]？
		  #问题：不明白这个语法。可以猜测分支变化的数值按照分支水平赋值。
		  #这个语句是增加一个属性或实例，而这个信息是一个列表。元素的排列与当前分支计数水平相关。
          branchChangedParamPb.append(endInfo['branchChangedParams'][key]['associatedProbability'][self.branchCountOnLevel-2])

          #subGroup.add('branchChangedParamValue',endInfo['branchChangedParams'][key]['actualValue'][self.branchCountOnLevel-2])
          #subGroup.add('branchChangedParamPb',endInfo['branchChangedParams'][key]['associatedProbability'][self.branchCountOnLevel-2])
          #condPbC.append(endInfo['branchChangedParams'][key]['changedConditionalPb'][self.branchCountOnLevel-2])
          condPbC = condPbC + endInfo['branchChangedParams'][key]['changedConditionalPb'][self.branchCountOnLevel-2]
		  #事件发生的条件概率=这个是一个列表，
          subGroup.add('happenedEvent',True)
		  #有分支，则事件发生为真
        else:#这里是当前分支计数为1
          subGroup.add('happenedEvent',endInfo['parentNode'].get('happenedEvent'))
		  #子节点中增加一个发生的事件的逻辑值。
          branchChangedParamValue.append(endInfo['branchChangedParams'][key]['oldValue'])
		  #等于1的分支的数值是父节点的旧值。
          branchChangedParamPb.append(endInfo['branchChangedParams'][key]['unchangedPb'])
		  #子节点的概率是父节点的不变的概率
          #subGroup.add('branchChangedParamValue',endInfo['branchChangedParams'][key]['oldValue'])
          #subGroup.add('branchChangedParamPb',endInfo['branchChangedParams'][key]['unchangedPb'])
          #condPbUn.append(endInfo['branchChangedParams'][key]['unchangedConditionalPb'])
          condPbUn =  condPbUn + endInfo['branchChangedParams'][key]['unchangedConditionalPb']
		  #不变的概率就是父节点中不变的概率。
      subGroup.add('branchChangedParam',branchParams)
	  #增加一个变化参数名称的信息。
      # add conditional probability
	  #增加条件概率
      if self.branchCountOnLevel != 1:#不等于1就是变化的分支。其变化的数值、概率以及名称进行赋值。
        subGroup.add('conditionalPbr',condPbC)
        subGroup.add('branchChangedParamValue',branchChangedParamValue)
        subGroup.add('branchChangedParamPb',branchChangedParamPb)
      else:#这就是当前分支计数等于1.也就是不变的。
        subGroup.add('conditionalPbr',condPbUn)
        subGroup.add('branchChangedParamValue',branchChangedParamValue)
        subGroup.add('branchChangedParamPb',branchChangedParamPb)
      # add initiator distribution info, start time, etc.

      subGroup.add('initiatorDistribution',self.toBeSampled[endInfo['branchDist']])
	  #赋值子节点的分布信息，值就是需要抽样的分布类型。
      subGroup.add('startTime', endInfo['parentNode'].get('endTime'))
	  #子节点的开始时间就是父节点的结束时间，为什么要有一个时间变量呢？是用于同步问题的吗？
      # initialize the endTime to be equal to the start one... It will modified at the end of this branch
	  #先初始化结束时间为开始时间，然后在分支结束后，在进行变更。
      subGroup.add('endTime', endInfo['parentNode'].get('endTime'))
      # add the branchedLevel dictionary to the subgroup
      if self.branchCountOnLevel != 1:
        branchedLevel[endInfo['branchDist']] = branchedLevel[endInfo['branchDist']] - 1
      # branch calculation info... running, queue, etc are set here
      subGroup.add('runEnded',False)
      subGroup.add('running',False)
      subGroup.add('queue',True)
      #  subGroup.set('restartFileRoot',endInfo['restartRoot'])
      # Append the new branch (subgroup) info to the parentNode in the tree object
      endInfo['parentNode'].appendBranch(subGroup)
	  #在结束父节点信息中增加这个子节点信息。
      # Fill the values dictionary that will be passed into the model in order to create an input
      # In this dictionary the info for changing the original input is stored
	  #生成一个将要传递给模型的字典，作为模型的输入。
      self.inputInfo = {'prefix':rname,'endTimeStep':endInfo['endTimeStep'],
                'branchChangedParam':subGroup.get('branchChangedParam'),
                'branchChangedParamValue':subGroup.get('branchChangedParamValue'),
                'conditionalPb':subGroup.get('conditionalPbr'),
                'startTime':endInfo['parentNode'].get('endTime'),
				#当新的节点开始后，什么时间结束？当分支条件达到以后结束？这个例子中看不出来参数是如何传递的。不明显。
				#但猜测，如果达到了分支条件，则需要记录分支条件的一些属性，比如分支概率，时间，等内容。但是与code是什么关系，在哪里调用呢？
                'RAVEN_parentID':subGroup.get('parent'),
                'RAVEN_isEnding':True}这个符号是什么，没有具体含义。都是真
			#inputInfo是一个输入信息字典，包括的关键字信息如需行，数值需要利用函数获得。

      #'RAVEN_parentID','RAVEN_isEnding'
      self.inputInfo['happenedEvent'] = subGroup.get('happenedEvent')
      # add additional edits if needed
	  #这里是一个模型中的方法？
      model.getAdditionalInputEdits(self.inputInfo)
      # add the newer branch name to the map
      self.rootToJob[rname] = self.rootToJob[subGroup.get('parent')]
	  #这里的get，add，都是面向对象语言中对对象属性的操作。get就是取值，add就是赋值？至少猜测是这样。
      # check if it is a preconditioned DET sampling, if so add the relative information
      precSampled = endInfo['parentNode'].get('hybridsamplerCoordinate')
      if precSampled:
	  #猜测代表混合抽样器，如果没有，为none，则不执行。如果不为空，则执行。
        self.inputInfo['hybridsamplerCoordinate'] = copy.deepcopy(precSampled)
        subGroup.add('hybridsamplerCoordinate', precSampled)
      # Check if the distribution that just triggered hitted the last probability threshold .
	  #检查是否分布正好激活了最后的一个概率阈值？
      #  In this case there is not a probability threshold that needs to be added in the input
      #  for this particular distribution
      if not (branchedLevel[endInfo['branchDist']] >= len(self.branchProbabilities[endInfo['branchDist']])):
	  #猜测是已经分支的内容是否大于分支概率中实例的数量，分支概率实例的数量代表了概率区间的离散数量。如果大于等于了。则为真，就结束？
        self.inputInfo['initiatorDistribution'] = [self.toBeSampled[endInfo['branchDist']]]
        self.inputInfo['PbThreshold'           ] = [self.branchProbabilities[endInfo['branchDist']][branchedLevel[endInfo['branchDist']]]]
        self.inputInfo['ValueThreshold'        ] = [self.branchValues[endInfo['branchDist']][branchedLevel[endInfo['branchDist']]]]
      #  For the other distributions, we put the unbranched thresholds
      #  Before adding these thresholds, check if the keyword 'initiatorDistribution' is present...
      #  (In the case the previous if statement is true, this keyword is not present yet
      #  Add it otherwise
      if not ('initiatorDistribution' in self.inputInfo.keys()):
	  #判断在输入信息的键中是否有分布的设置？
        self.inputInfo['initiatorDistribution' ] = []
        self.inputInfo['PbThreshold'           ] = []
        self.inputInfo['ValueThreshold'        ] = []
      # Add the unbranched thresholds  这个是不是属于截断的部分？就是如果小于一定的数值就不分枝了？
      for key in self.branchProbabilities.keys():
        if not (key in self.toBeSampled[endInfo['branchDist']]) and (branchedLevel[key] < len(self.branchProbabilities[key])):
          self.inputInfo['initiatorDistribution'].append(self.toBeSampled[key])
      for key in self.branchProbabilities.keys():
        if not (key in self.toBeSampled[endInfo['branchDist']]) and (branchedLevel[key] < len(self.branchProbabilities[key])):
          self.inputInfo['PbThreshold'   ].append(self.branchProbabilities[key][branchedLevel[key]])
          self.inputInfo['ValueThreshold'].append(self.branchValues[key][branchedLevel[key]])
      self.inputInfo['SampledVars']   = {}
      self.inputInfo['SampledVarsPb'] = {}
      for varname in self.standardDETvariables:
        self.inputInfo['SampledVars'][varname]   = self.branchValues[varname][branchedLevel[varname]]
        self.inputInfo['SampledVarsPb'][varname] = self.branchProbabilities[varname][branchedLevel[varname]]
        #self.inputInfo['SampledVars'][varname]   = self.branchValues[self.toBeSampled[varname]][branchedLevel[self.toBeSampled[varname]]]
        #self.inputInfo['SampledVarsPb'][varname] = self.branchProbabilities[self.toBeSampled[varname]][branchedLevel[self.toBeSampled[varname]]]
      self._constantVariables()
      if precSampled:
        for precSample in precSampled:
          self.inputInfo['SampledVars'  ].update(precSample['SampledVars'])
          self.inputInfo['SampledVarsPb'].update(precSample['SampledVarsPb'])
      self.inputInfo['PointProbability' ] = reduce(mul, self.inputInfo['SampledVarsPb'].values())*subGroup.get('conditionalPbr')
	  #输入的点估计概率=抽样参数概率的累乘积，然后在乘以子节点的条件概率。
      self.inputInfo['ProbabilityWeight'] = self.inputInfo['PointProbability' ]
	  #概率权重就是分支点的概率。
      self.inputInfo.update({'ProbabilityWeight-'+key.strip():value for key,value in self.inputInfo['SampledVarsPb'].items()})
      # Add the new input path into the RunQueue system
      newInputs = {'args': [str(self.type)], 'kwargs':dict(self.inputInfo)}
	  #根据这个表达式newInputs是一个字典型变量。
      self.RunQueue['queue'].append(newInputs)
	  #运行队列中队列是一个列表，但列表的元素是一个字典。从上下文分析。
      self.RunQueue['identifiers'].append(self.inputInfo['prefix'])
      for key,value in self.inputInfo.items():#习惯了就好了。这是在遍历一个字典。也就是输入信息的元素都是字典。
        subGroup.add(key,copy.copy(value))
      popped = endInfo.pop('parentNode')
      subGroup.add('endInfo',copy.deepcopy(endInfo))
      endInfo['parentNode'] = popped
      del branchedLevel

  def _createRunningQueue(self, model, myInput, forceEvent=False):#上面是创建一个运行的队列分支，现在是创建一个运行队列。用于混合抽样？
    """
      Function to create and append new inputs to the queue. It uses all the containers have been updated by the previous functions
      @ In, model, Model instance, model instance that can be a Code type, ROM, etc.
      @ In, myInput, list, List of the original inputs
      @ In, forceEvent, bool, True if a branching needs to be forced
	  #forceEvent是一个逻辑变量，可以用于控制强制分支。
      @ Out, None
    """
    if self.counter >= 1:#计数器大于1.问题是这个计数器的作用是什么呢？
      # The first DET calculation branch has already been run，也许第一个分支就是一个启动的分支。
      # Start the manipulation:
      #  Pop out the last endInfo information and the branchedLevel
      self._createRunningQueueBranch(model, myInput, forceEvent)
    else:#如果计数器等于1.则说明是第一个DET。我们运行第一次的测试。
      # We construct the input for the first DET branch calculation'
      self._createRunningQueueBegin(model, myInput)
    return

  def __getQueueElement(self):#猜测的逻辑是先根据分值产生计算队列，然后再通过这个方法去调用code计算？
    """
      Function to get an input from the internal queue system
	  如果这里是一个队列系统，那么队列系统运行的逻辑是什么？也就是说从一次生成所有的事件节点，还是按层进行分？
	  从运行结果看，感觉是按照层来分，每一层计算完然后在往后。
	  在队列系统中，得到一个输入。
      @ In, None
      @ Out, jobInput, list, the list of inout (First input in the queue)
	  输出是一个job输入。一个列表。
    """
    # Pop out the first input in queue
	#pop的方法是不是取出的意思？这个语句的意思理解了。pop的含义是删除列表中的元素，并讲这个元素的值返回。
	#特别适合进行队列的操作。简单说就是取出一个删除一个。
    jobInput  = self.RunQueue['queue'      ].pop(0)
	#含义就是从运行队列中取出一个的计算信息，并删除原队列中的元素。
    jobId     = self.RunQueue['identifiers'].pop(0)
	#取出队列中第一个标识符，赋值后删除队列中的信息。
    #set running flags in self.TreeInfo
    root = self.TreeInfo[self.rootToJob[jobId]].getrootnode()
	#通过标识符，获得节点信息。
    # Update the run information flags
    if (root.name == jobId):#在节点信息中，节点的名字和队列中的ID应该是一致的。
      root.add('runEnded',False)
	  #add是给集合增加元素。
      root.add('running',True)
      root.add('queue',False)
    else:
      subElm = list(root.iter(jobId))[0]
      if(subElm):
        subElm.add('runEnded',False)
        subElm.add('running',True)
        subElm.add('queue',False)
		#两个赋值都是一样的？是赋值的位置不对？

    return jobInput

  def generateInput(self,model,oldInput):
    """
      This method has to be overwritten to provide the specialization for the specific sampler
      The model instance in might be needed since, especially for external codes,
      only the code interface possesses 拥有支配的意思 the dictionary for reading the variable definition syntax
	  这个方法是重新写已经确定的特定抽样器。这个过程中可能需要模型的实例，特别对于外部code
	  因为code接口拥有读取变量定义语法的文件夹？或字典？
      @ In, model, model instance, it is the instance of a RAVEN model
      @ In, oldInput, list, a list of the original needed inputs for the model (e.g. list of files, etc. etc)


      @ Out, generateInput, (0,list), list containing the new inputs -in reality it is the model that returns this; 
	  the Sampler generates the value to be placed in the input of the model.
    """
    #NB:（提示注意的意思） if someday the DET handles restarts as other samplers do in generateInput, the return code 1 indicates the result
    #  is stored in a restart data object, while 0 indicates a new run has been found.
	#猜测的是，未来DET可以用于与程序进行交互，也就是DET的一些参数可能会根据code的物理过程变化而变化，那么DET执行过程中则需要产生一个
	#中间用于重新启动的数据结构。这个函数就是用于标识。如果是1，则是重新生成的，如果是0，就是一个全新的计算问题。
    #model.getAdditionalInputEdits(self.inputInfo)
    return 0, self.localGenerateInput(model, oldInput)

  def localGenerateInput(self,model,myInput):
    """
      Function to select the next most informative point for refining the limit
      surface search.
	  选择最有效的下一个计算点的方法，从而可以优化极限曲面的搜索。
      After this method is called, the self.inputInfo should be ready to be sent
      to the model
	  调用这个方法后，输入信息就要准备传递给模型。
      @ In, model, model instance, an instance of a model
      @ In, myInput, list, a list of the original needed inputs for the model (e.g. list of files, etc.)
      @ Out, newerInput, list, list of new inputs
    """
    #self._endJobRunnable = max([len(self.RunQueue['queue']),1])
    if self.counter <= 1:
      # If first branch input, create the queue
      self._createRunningQueue(model, myInput)
    # retrieve the input from the queue
    newerInput = self.__getQueueElement()
    # If no inputs are present in the queue => a branch is finished
    if not newerInput:
      self.raiseADebug('A Branch ended!')
	  #推理这个逻辑是如果计数器小于等于1，则要产生一个新的队列。然后获取队列元素，如果队列元素为空。则说明已经结束。

    ## It turns out the "newerInput" contains all of the information that should
    ## be in inputInfo (which should actually be returned and not stored in the
	#队列中的元素是所有的信息。这个信息要给inputInfo进行赋值。从而进行计算。
    ## sampler object, but all samplers do this for now) -- DPM 4/26/17
    self.inputInfo = newerInput['kwargs']
	#['kwargs']这种赋值方式是什么含义？
    return myInput

  def _generateDistributions(self,availableDist,availableFunc):#没有用户调用这个函数，经过简单DET测试，注释后没有影响
    """
      Generates the distrbutions and functions. 
      It is overloaded here because we need to manage the sub-sampling
      strategies for the Hybrid DET approach
	  重复的部分，因为要产生混合抽样的方法。
	 
      @ In, availDist, dict, dict of distributions
      @ In, availableFunc, dict, dict of functions
      @ Out, None
    """
    Grid._generateDistributions(self,availableDist,availableFunc)
    for hybridsampler in self.hybridStrategyToApply.values():
      hybridsampler._generateDistributions(availableDist,availableFunc)

  def localInputAndChecks(self,xmlNode, paramInput):#问题是，这个函数没有被调用。
    """
      Class specific xml inputs will be read here and checked for validity.
	  读取XML文件并检查有效性。
      @ In, xmlNode, xml.etree.ElementTree.Element, The xml element node that will be checked against 
	  the available options specific to this Sampler.
      @ In, paramInput, InputData.ParameterInput, the parsed parameters
      @ Out, None
    """
    #TODO remove using xmlNode，这两个函数在后面都有。一个用于简单DET的检查，一个用于混合DET的检查。
    self._localInputAndChecksDET(xmlNode, paramInput)
    self._localInputAndChecksHybrid(xmlNode, paramInput)

  def _localInputAndChecksDET(self,xmlNode, paramInput):
    """
      Class specific inputs will be read here and checked for validity.
	  读取类的特殊输入，并且检查有效性。
      This method reads the standard DET portion only (no hybrid)
	  这个仅仅适用DET
      @ In, xmlNode, xml.etree.ElementTree.Element, The xml element node that will be
	  checked against the available options specific to this Sampler.
	  输入为XML的节点，以及XML的节点信息。
      @ In, paramInput, InputData.ParameterInput, the parsed parameters
	  输入为参数输入、输入参数，以及。。。
      @ Out, None
    """
    Grid.localInputAndChecks(self,xmlNode, paramInput)
	#调用了一个网格抽样的检查方法。因为DET本质上是一个网格抽样。但有什么不同呢？
    if 'printEndXmlSummary'  in xmlNode.attrib.keys():
      self.printEndXmlSummary  = xmlNode.attrib['printEndXmlSummary'].lower()  in utils.stringsThatMeanTrue()
	  #utils.stringsThatMeanTrue是utils模块中的一个方法，不知道什么含义。

    if 'removeXmlBranchInfo' in xmlNode.attrib.keys():
      self.removeXmlBranchInfo = xmlNode.attrib['removeXmlBranchInfo'].lower() in utils.stringsThatMeanTrue()
    if 'maxSimulationTime'   in xmlNode.attrib.keys():
      try:
        self.maxSimulTime = float(xmlNode.attrib['maxSimulationTime'])
      except (KeyError,NameError):
        self.raiseAnError(IOError,'Can not convert maxSimulationTime in float number!!!')
    branchedLevel, error_found = {}, False
    gridInfo   = self.gridEntity.returnParameter("gridInfo")
    errorFound = False
    errorMsgs  = ''

    for keyk in self.axisName:
	#self.axisName在程序中没有调用。从哪里来的？
	#回答：这个参数是grid程序中定义的一个列表的变量。描述如下。含义是每一个轴的名称，也就是抽样参数名称？
	#self.axisName             = []           # the name of each axis (variable) X轴的参数名。
      branchedLevel[keyk] = 0 
	  #分支水平是一个整数，是在当前节点下具体的一个子节点的排序？
	  #？
      #branchedLevel[self.toBeSampled[keyk]] = 0
      self.standardDETvariables.append(keyk)
	  #append是在列表后增加一个元素。在标准的DET变量中增加一个keyk。一个键的值。也就是增加了一个抽样参数。
	  #这个间的值是在axisName中的。
      if self.gridInfo[keyk] == 'CDF':
	  #这是一个分层抽样的列表的属性选择。一共就有两种，CDF和value
        self.branchProbabilities[keyk] = gridInfo[keyk][2]
		#gridInfo是一个字典。{'name of the variable':Type}
		#从学习上来说，一个字典，可以用[]代表键的元素。所以，这个含义就是分支概率是一个字典。
		#而分支概率字典的键是抽样参数，值是类别？
		#gridInfo[keyk][2]这个是DET中用户输入的离散的具体数值，以一种列表的方式出现。
		#
        self.branchProbabilities[keyk].sort(key=float)
		#sort这是一个排序函数。有可能用户在输入的时候，并不是按照顺序的离散进行输入。程序中考虑了这种不足。
        if max(self.branchProbabilities[keyk]) > 1:
		#branchProbabilities[keyk]是一个列表，代表了DET离散的数值。无论是概率还是参数值。
          errorMsgs += "One of the Thresholds for distribution " + str(gridInfo[keyk][2]) + " is > 1 \n"
		  #已经确认了这部分的输出功能。
          errorFound = True
        probMultiplicities = Counter(self.branchProbabilities[keyk])
		#重复性检查。检查列表中重复的元素。这个重复元素还是一个列表的形式。
        multiples = [prob for prob,mult in probMultiplicities.items() if mult > 1]
        ## Only the multiple variables remain
        for prob in multiples:
          errorMsgs += "In variable " + str(keyk) + " the Threshold " + str(prob)+" appears multiple times!!\n"
		  #通过调试指导，keyk是一个分布+分布名称。In variable <distribution>zeroToOne the Threshold 0.2 appears multiple times!!
		  #主要的作用是检查在输入是，是否有重复的部分。
          errorFound = True
#         self.branchProbabilities[self.toBeSampled[keyk]] = gridInfo[keyk][2]
#         self.branchProbabilities[self.toBeSampled[keyk]].sort(key=float)
#         if max(self.branchProbabilities[self.toBeSampled[keyk]]) > 1:
#           self.raiseAWarning("One of the Thresholds for distribution " + str(gridInfo[keyk][2]) + " is > 1")
#           errorFound = True
#           for index in range(len(sorted(self.branchProbabilities[self.toBeSampled[keyk]], key=float))):
#             if sorted(self.branchProbabilities[self.toBeSampled[keyk]], key=float).count(sorted(self.branchProbabilities[self.toBeSampled[keyk]], key=float)[index]) > 1:
#               self.raiseAWarning("In distribution " + str(self.toBeSampled[keyk]) + " the Threshold " + str(sorted(self.branchProbabilities[self.toBeSampled[keyk]], key=float)[index])+" appears multiple times!!")
#               errorFound = True
      else:
        self.branchValues[keyk] = gridInfo[keyk][2]  这个就是基于数值的分支方法。
        self.branchValues[keyk].sort(key=float)
        valueMultiplicities = Counter(self.branchValues[keyk])
		#Counter函数的含义是查找是否重复。
        multiples = [value for value,mult in valueMultiplicities.items() if mult > 1]
        ## Only the multiple variables remain
        for value in multiples:
          errorMsgs += "In variable " + str(keyk) + " the Threshold " + str(value)+" appears multiple times!!\n"
          errorFound = True
#         self.branchValues[self.toBeSampled[keyk]] = gridInfo[keyk][2]
#         self.branchValues[self.toBeSampled[keyk]].sort(key=float)
#         for index in range(len(sorted(self.branchValues[self.toBeSampled[keyk]], key=float))):
#           if sorted(self.branchValues[self.toBeSampled[keyk]], key=float).count(sorted(self.branchValues[self.toBeSampled[keyk]], key=float)[index]) > 1:
#             self.raiseAWarning("In distribution " + str(self.toBeSampled[keyk]) + " the Threshold " + str(sorted(self.branchValues[self.toBeSampled[keyk]], key=float)[index])+" appears multiple times!!")
#             errorFound = True

    # check if RELAP7 mode is activated, in case check that a <distribution> variable is unique in the input
    if any("<distribution>" in s for s in self.branchProbabilities.keys()):
	#用于检查模型中的分布是否与前面的程序一致。
      associatedDists = self.toBeSampled.values()
      if len(list(set(associatedDists))) != len(associatedDists):
        errorMsgs += "Distribution-mode sampling activated in " + self.name+". In this case every <distribution> needs to be assocaited
		with one single <Distribution> block!\n"
        errorFound = True
    if errorFound:
      self.raiseAnError(IOError,"In sampler named " + self.name+' the following errors have been found: \n'+errorMsgs )
	  #self.name这里是指抽样的名称。
    # Append the branchedLevel dictionary in the proper list
    self.branchedLevel.append(branchedLevel)

  def _localInputAndChecksHybrid(self,xmlNode, paramInput): 仅仅是针对混合DET的部分。
    """
      Class specific inputs will be read here and checked for validity.
      This method reads the hybrid det portion only
      @ In, xmlNode, xml.etree.ElementTree.Element, The xml element node that will be checked against the available options specific to this Sampler.
      @ In, paramInput, InputData.ParameterInput, the parsed parameters
      @ Out, None
    """
    for child in xmlNode:
	#这个判断xml文件中的子节点的。循环每一个xmlNode的子节点。
      if child.tag == 'HybridSampler':
	  #专门用于混合抽样监测。利用抽样标志位识别。
        if not 'type' in child.attrib.keys():
		#因为在输入文件中，如果使用混合抽样，那么type的属性是必须设置和选择的。否则报错。
          self.raiseAnError(IOError,'Not found attribute type in hybridsamplerSampler block!')
        if child.attrib['type'] in self.hybridStrategyToApply.keys():
          self.raiseAnError(IOError,'Hybrid Sampler type '+child.attrib['type'] + ' already inputted!')
        if child.attrib['type'] not in self.hybridSamplersAvail.keys():
          self.raiseAnError(IOError,'Hybrid Sampler type ' +child.attrib['type'] + ' unknown. Available are '+ ','.join(self.hybridSamplersAvail.keys()) + '!')
        self.hybridNumberSamplers = 1
        # the user can decided how to sample the epistemic
        self.hybridStrategyToApply[child.attrib['type']] = self.hybridSamplersAvail[child.attrib['type']]()
        # give the hybridsampler sampler the message handler
        self.hybridStrategyToApply[child.attrib['type']].setMessageHandler(self.messageHandler)
        # make the hybridsampler sampler read  its own xml block
        childCopy = copy.deepcopy(child)#这个是把xml文件的子节点都深度赋值给childCopy。
        childCopy.tag = child.attrib['type']
        childCopy.attrib.pop('type')#为什么要移除type。
		#pop是移除列表中的一个元祖。
        self.hybridStrategyToApply[child.attrib['type']]._readMoreXML(childCopy)
        # store the variables that represent the epistemic space
        self.epistemicVariables.update(dict.fromkeys(self.hybridStrategyToApply[child.attrib['type']].toBeSampled.keys(),{}))

  def localGetInitParams(self):
  #没有函数调用和使用。难道是其他函数使用？
    """
      Appends a given dictionary with class specific member variables and their
      associated initialized values.
      @ In, None
      @ Out, paramDict, dict, dictionary containing the parameter names as keys
        and each parameter's initial value as the dictionary values
		这是一个字典形式的数据，关键字是参数名称，再加上初始数值。
    """
    paramDict = {}  这里是参数字典。初始化一个空。
    for key in self.branchProbabilities.keys(): 这个是分支概率
      paramDict['Probability Thresholds for var ' + str(key) + ' are: '] = [str(x) for x in self.branchProbabilities[key]]
    for key in self.branchValues.keys()       :  这个是分支的值
      paramDict['Values Thresholds for var ' + str(key) + ' are: '] = [str(x) for x in self.branchValues[key]]
    return paramDict

  def localGetCurrentSetting(self):
    """
      Appends a given dictionary with class specific information regarding the
      current status of the object.
      @ In, None
      @ Out, paramDict, dict, dictionary containing the parameter names as keys
        and each parameter's initial value as the dictionary values
    """
    paramDict = {}
    paramDict['actual threshold levels are '] = self.branchedLevel[0]
    return paramDict

  def localInitialize(self):这是那个函数的局部初始化函数？
  #这个函数没有任何一个函数调用，如何运行？有什么含义？
    """
      Will perform all initialization specific to this Sampler. 执行这个抽样器的所有初始化过程。
	  For instance,
      creating an empty container to hold the identified surface points, error
      checking the optionally provided solution export and other preset values,
      and initializing the limit surface Post-Processor used by this sampler.
	  创建一个包含识别的极限曲面的计数结构，
	  用这个抽样器初始化一个极限面的后处理器？
      @ In, None
      @ Out, None
    """
    if len(self.hybridStrategyToApply.keys()) > 0:
	#判断是否有混合抽样的选项。
      hybridlistoflist = []  
    for cnt, preckey  in enumerate(self.hybridStrategyToApply.keys()):
	#这类数据对的循环，就是一起循环。也就是cnt是整数索引，preckey是抽样策略类型。
	#enumerate的含义是将混合抽样策略的类型生成一个数据对，并循环。（1 一种方法） （2 一种方法）
      hybridsampler =  self.hybridStrategyToApply[preckey]
	  #取出混合抽样名称
      hybridlistoflist.append([])
      hybridsampler.initialize()#混合抽样器初始化
      self.hybridNumberSamplers *= hybridsampler.limit
      while hybridsampler.amIreadyToProvideAnInput():
        hybridsampler.counter +=1
        hybridsampler.localGenerateInput(None,None)
        hybridsampler.inputInfo['prefix'] = hybridsampler.counter
        hybridlistoflist[cnt].append(copy.deepcopy(hybridsampler.inputInfo))
    if self.hybridNumberSamplers > 0:
      self.raiseAMessage('Number of Hybrid Samples are ' + str(self.hybridNumberSamplers) + '!')
      hybridNumber = self.hybridNumberSamplers
      combinations = list(itertools.product(*hybridlistoflist))
    else:
      hybridNumber = 1
    self.TreeInfo = {}
    for precSample in range(hybridNumber):
      elm = ETS.HierarchicalNode(self.messageHandler,self.name + '_' + str(precSample+1))
      elm.add('name', self.name + '_'+ str(precSample+1))
      elm.add('startTime', str(0.0))
      # Initialize the endTime to be equal to the start one...
      # It will modified at the end of each branch
	  #初始化结束时间为起始时间，在每次分支结束后变化。
      elm.add('endTime', str(0.0))
      elm.add('runEnded',False)
      elm.add('running',True)
      elm.add('queue',False)
	  #这个add的方法是增加属性，或者是设置属性的含义。
      # if preconditioned DET, add the sampled from hybridsampler samplers
      if self.hybridNumberSamplers > 0:
        elm.add('hybridsamplerCoordinate', combinations[precSample])
        for point in combinations[precSample]:
          for epistVar, val in point['SampledVars'].items():
            self.epistemicVariables[epistVar][elm.get('name')] = val
      # The dictionary branchedLevel is stored in the xml tree too. That's because
      # the advancement of the thresholds must follow the tree structure
      elm.add('branchedLevel', self.branchedLevel[0])
      # Here it is stored all the info regarding the DET => we create the info for all the
      # branchings and we store them
      self.TreeInfo[self.name + '_' + str(precSample+1)] = ETS.HierarchicalTree(self.messageHandler,elm)

    for key in self.branchProbabilities.keys():
      #kk = self.toBeSampled.values().index(key)
      #self.branchValues[key] = [self.distDict[self.toBeSampled.keys()[self.toBeSampled.values().index(key)]].ppf(float(self.branchProbabilities[key][index])) for index in range(len(self.branchProbabilities[key]))]
      self.branchValues[key] = [self.distDict[key].ppf(float(self.branchProbabilities[key][index])) for index in range(len(self.branchProbabilities[key]))]
    for key in self.branchValues.keys():
      #kk = self.toBeSampled.values().index(key)
      #self.branchProbabilities[key] = [self.distDict[self.toBeSampled.keys()[self.toBeSampled.values().index(key)]].cdf(float(self.branchValues[key][index])) for index in range(len(self.branchValues[key]))]
      self.branchProbabilities[key] = [self.distDict[key].cdf(float(self.branchValues[key][index])) for index in range(len(self.branchValues[key]))]
    self.limit = sys.maxsize
    # add expected metadata
    self.addMetaKeys(['RAVEN_parentID','RAVEN_isEnding'])
