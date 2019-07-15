# Copyright 2017 Battelle Energy Alliance, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0 ��������̬�¼������߼������ÿ��������
������һ���棬����ʵ��������һ���档
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
  This module contains the Dynamic Event Tree and
  the Hybrid Dynamic Event Tree sampling strategies
  �����������������֣�һ���Ƕ�̬�¼�����һ���ǻ�϶�̬�¼�����������Ϊ���صĻ���������

  �ܹ��ǲ�һ���ġ����Կ�raven�����ʵ�ֵ��õĹ��̵ġ���һ��ѧϰ���ص㡣
  ������DET�ļ򵥵����ӣ����ǿ�����������������ɵģ���Ϊû��relap7�������޷�������������relap7�Ĳ��Գ��򡣻��������ӵġ�
  ����Ӧ�ÿ����������Ӧ������һ���İ�����
  2019��5��30�գ��ֿ���һ�顣����һ�����µ��ջ񡣵��ǻ���û����ȫ��Ū����������������е��أ�

  Created on May 21, 2016
  @author: alfoa
  supercedes Samplers.py from alfoa
  �������룬��������Ҳ��alfoa�����ģ�
"""
#for future compatibility with Python 3--------------------------------------------------------------
from __future__ import division, print_function, unicode_literals, absolute_import
import warnings
warnings.simplefilter('default',DeprecationWarning)
#End compatibility block for Python 3----------------------------------------------------------------

#External Modules------------------------------------------------------------------------------------
import sys
import os
import copy ��������������ǳ������
from operator import mul #mulģ���ǳ˷��ķ�����operator��һ�������ģ�顣
#python��׼��֮operator�������ģ�飩 operatorģ���ṩ��һϵ����Python�Դ�����һ����Ч�ĺ�����
#���磺operator.add(x, y)�ͱ��ʽx+y�ǵ�Ч�ġ���Щ������ķ��������Լ��ĺ�������
#Ϊ�˷��������һЩ��������û��ǰ���ͺ��ã�_���� operatorģ������cʵ�ֵģ�����ִ���ٶȱ�python����졣
from functools import reduce
#reduce() ������Բ���������Ԫ�ؽ����ۻ���
#������һ�����ݼ��ϣ�����Ԫ��ȣ��е��������ݽ������в������ô��� reduce �еĺ��� function��������������
#�ȶԼ����еĵ� 1��2 ��Ԫ�ؽ��в������õ��Ľ����������������� function �������㣬���õ�һ�������
import xml.etree.ElementTree as ET#����һ�����ڽ���XML�ļ�����䡣���Զ�ȡXML�Ľڵ㣬���ԣ������б༭�޸ĵ����ݡ�
import itertools #����һ����������
from collections import Counter #����Counter������˼�Ǽ�������Ҳ�������ǳ�����ͳ�Ƶ�һ����������
#External Modules End--------------------------------------------------------------------------------
�ⲿģ�鶼��Ӧ���ǿ������ġ���������������ʱ������Ӧ�ò�����ص�ģ�飬ȥ��һ�����Ĺ��ܡ�


#Internal Modules------------------------------------------------------------------------------------
from .Grid import Grid  �ڲ�ģ�顣��framework �е�sample�ļ��������С�
from .MonteCarlo import MonteCarlo  �ɿ���framework �е�sample�ļ��������С�
from .Stratified import Stratified  ������framework �е�sample�ļ��������С�
from .Sampler import Sampler   ������framework �е�sample�ļ��������С�
from utils import utils   ����ģ�飬��framework �е�utils�ļ�����
from utils import InputData  ����ģ�飬��framework �е�utils�ļ�����
import utils.TreeStructure as ETS  ����ģ�飬��framework �е�utils�ļ�����
#Internal Modules End-------------------------------------------------------------------------------

class DynamicEventTree(Grid):  ����һ����Ķ��塣���԰������̬�¼����������ʵ�������Լ�����һЩ���������ݵĲ�����grid��
                            ��Ϊ������һ��Grid������������һ���ࡣ���ԣ���Ҫ�˽�grid����������
#   grid��֪����ʲô���ԡ�Ҳ��һ��������
  """
  DYNAMIC EVENT TREE Sampler (DET)  ����һ���ࡣһ����̬�¼������ࡣ
  """

  @classmethod  �����װ������������һ����ķ���������һ����ʶ�����Եġ�
  def getInputSpecification(cls):������һ�����������������ȡ�ض���Ϣ�ĺ�����˵�����������ԡ�
    """
      Method to get a reference to a class that specifies the input data for
      class cls.
      @ In, cls, the class for which we are retrieving the specification  �����cls�����������������Ϣ��
      @ Out, inputSpecification, InputData.ParameterInput, class to use for
        specifying input of cls.   ����������˵������������ݣ��Լ���������͡�
		�²���������relap���棬�����ǰ�������ʷ�����һ���ṹ�У�Ȼ���ٸ�����Ҫȥ�任��
    """
    inputSpecification = super(DynamicEventTree, cls).getInputSpecification()  

    inputSpecification.addParam("printEndXmlSummary", InputData.StringType) ����Ǵ������õĲ�����ͨ��DET��XML�ļ������ԡ�
    inputSpecification.addParam("maxSimulationType", InputData.FloatType)
    inputSpecification.addParam("removeXmlBranchInfo", InputData.StringType)

    oldSub = inputSpecification.popSub("Distribution")
    newDistributionInput = InputData.parameterInputFactory("Distribution", baseNode=oldSub) ��������Ǵ��ݵ�XML�ļ��еķֲ�����Ϣ��
    gridInput = InputData.parameterInputFactory("grid", contentType=InputData.StringType) 

    gridInput.addParam("type", InputData.StringType)  ����Ǹ�DET�ĺ�����ֵ��������CDF����value��ͬ��
    gridInput.addParam("construction", InputData.StringType) ����ǵȲ��������Զ��塣
    gridInput.addParam("steps", InputData.IntegerType)  ����ǲ�����Ϣ��

    newDistributionInput.addSub(gridInput) 
    inputSpecification.addSub(newDistributionInput)

    #Strict mode off because basically this allows things to be passed to
    # sub Samplers, which will be checked later.
    hybridSamplerInput = InputData.parameterInputFactory("HybridSampler", strictMode=False)  �����ǻ�ϳ�������
    hybridSamplerInput.addParam("type", InputData.StringType)

    for nodeName in ['variable','Distribution']:#���ֺ������ѭ�����������XML���νṹ���ӽڵ���ѭ����
      nodeInput = InputData.parameterInputFactory(nodeName, strictMode=False)
      nodeInput.addParam("name", InputData.StringType)
      hybridSamplerInput.addSub(nodeInput)
    inputSpecification.addSub(hybridSamplerInput)

    return inputSpecification

  def __init__(self):��ʼ�����֣�
    """
    Default Constructor that will initialize member variables with reasonable
    defaults or empty lists/dictionaries where applicable.

    @ In, None
    @ Out, None
    """
    Grid.__init__(self)  ����һ��DET�ഫ�ݵ�����Ĳ��������Գ�ʼ����grid�������һ���ࡣ��Ҫ��ʼ����
	���ﻹҪ��һ��Grid�ĳ�ʼ�������ݡ�
    # Working directory (Path of the directory in which all the outputs,etc. are stored) 
    self.workingDir                        = "" ���������ĵ�ַ
    # (optional) if not present, the sampler will not change the relative keyword in the input file
    self.maxSimulTime                      = None ѡ���Ե����ԡ�
    # print the xml tree representation of the dynamic event tree calculation
    # see variable 'self.TreeInfo'
    self.printEndXmlSummary                = False ���ǳ�ʼֵ��
    # flag to control if the branch info xml file needs to be removed after reading   ����XML�ļ��Ƿ�ɾ����û�гɹ���
     ͨ�����ԣ�������ֲ����޸ġ�Ҳ���Ƿ�֧��XML�ļ�һ���ᱻɾ���ġ�
    self.removeXmlBranchInfo               = True 
    # Dictionary of the probability bins for each distribution that have been ÿһ��ʹ�õķֲ����Ը���Ƭ�洢���ֵ䡣
    #  inputted by the user ('distName':[Pb_Threshold_1, Pb_Threshold_2, ..., Pb_Threshold_n])
    self.branchProbabilities               = {}  ������������֧���ʡ���֧�ĸ��ʡ���ͨ����ֵ���ߺ�������ĸ��ʡ�
	#��֧������һ���ֵ䡣��1����֧���� 1����֧����������ʽ��
    # Dictionary of the Values' bins for each distribution that have been
    #  inputted by the user ('distName':[Pb_Threshold_1, Pb_Threshold_2, ..., Pb_Threshold_n])
	#����Ƿֲ��ĸ�����ֵ��distName�����������ʲô���Ƿֲ������𣿻��Ƿֲ����������֣�

    # these are the invCDFs of the PBs inputted in branchProbabilities (if ProbabilityThresholds have been inputted)

    self.branchValues                      = {}����Ƿ�֧��ֵ��
    # List of Dictionaries of the last probability bin level (position in the array) reached for each distribution ('distName':IntegerValue)
	#��֧��ֵ����ʽ�ֲ�����+һ������������ĺ����Ǵﵽÿһ���ֲ����һ��������ɢ�����ֵ����ÿһ����֧���������߽��ϵ�ֵ��
    # This container is a working dictionary. The branchedLevels are stored in the xml tree "self.TreeInfo" since they must track
    # the evolution of the dynamic event tree
	#���������ָ�������ļ��䡣dictionary�����level��Ϣ��self.treeinfo�С�
    self.branchedLevel                     = []
    # Counter for the branch needs to be run after a calculation branched (it is a working variable) �����֧�����Ժ�ķ�֧��Ŀ��
	#��������Ƿ�֧ˮƽ����¼�����Ժ���Ҫ��֧�Ĳ㼶�����������������жϵģ�ʵ������һ���ֲ�����������
    self.branchCountOnLevel                = 0
    # Dictionary tha contains the actual branching info
    # (i.e. distribution that triggered, values of the variables that need to be changed, etc)
	#ʵ�ʷ�֧��Ϣ�����������ķֲ�����Ҫ�仯�ı�����ֵ�ȡ�
    self.actualBranchInfo                  = {} ������֧��Ϣ���ֵ䡣
    # Parent Branch end time (It's a working variable used to set up the new branches need to be run.
	#ͨ�����������RAVEN��ͨ��ʱ������DET�ķ�֧���п��ơ�
    #   The new branches' start time will be the end time of the parent branch )
	#���ڵ����ʱ�䣬�½ڵ�Ŀ�ʼʱ����Ǹ��ڵ������ʱ�䡣
    self.actualEndTime                     = 0.0
    # Parent Branch end time step (It's a working variable used to set up the new branches need to be run.
    #  The end time step is used to construct the filename of the restart files needed for restart the new branch calculations)
	#����ʱ�䡰�����������ڹ����ļ���������ļ��������������µķ�֧���㣿
    self.actualEndTs                       = 0
    # Xml tree object. It stored all the info regarding the DET. It is in continue evolution during a DET calculation
	#TreeInfo��һ��XML�����ݶ��󡣴洢������DET��ص���Ϣ��ÿһ��DET�ļ��㶼������ݻ���

    self.TreeInfo                          = None
    # List of Dictionaries. It is a working variable used to store the information needed to create branches from a Parent Branch
	#һ���б���¼���ڵ���Ϣ���������ӽڵ�ķ�֧��

    self.endInfo                           = []
    # Queue system. The inputs are waiting to be run are stored in this queue dictionary
	#��һ���ֵ䣬�洢����ϵͳ������һ��������Կ�����������ֵ�ļ��а�����ʶ���������DET1-1��
    self.RunQueue                          = {}
    # identifiers of the inputs in queue (name of the history... for example DET_1,1,1)
	#����һ����ʶ������һ���б����ַ�ʽ��ʾ����һ���ֵ�ļ���
    self.RunQueue['identifiers']           = []
    # Corresponding inputs
    self.RunQueue['queue']                 = []
    # mapping from jobID to rootname in TreeInfo {jobID:rootName}
	#ӳ�䣬�ӹ���ID����DET_test_1-1-2-3-3����TreeInfo�и������ơ�
    self.rootToJob                         = {}
    # dictionary of Hybrid Samplers available
    self.hybridSamplersAvail               = {'MonteCarlo':MonteCarlo,'Stratified':Stratified,'Grid':Grid}
	#�����ֵ�ĸ�ֵ����������ֵ��ȷ����ֻ�����ַ���������һ�����е���𣬾���ֻ��������
    # dictionary of inputted hybridsamplers need to be applied
	#��ҪӦ�õĻ�ϳ������ֵ䡣�����ʵ����Ӧ�õĻ�ϳ���������
    self.hybridStrategyToApply             = {}
    # total number of hybridsampler samples (combination of all different hybridsampler strategy)
	#�����ܵĴ�����
    self.hybridNumberSamplers              = 0
    # List of variables that represent the aleatory space
	#һ���б��г�����DET�д���Ĳ�����Ҳ���Ǳ�׼��DET�Ĵ˲�������������ͨ��������Ʋ⣬Ӧ���Ǳ��������֡�
    self.standardDETvariables              = []
    # Dictionary of variables that represent the epistemic space (hybrid det). Format => {'epistemicVarName':{'HybridTree name':value}}
	#�����ֵ����ʽ��������֪��ȷ���Բ������Լ���ϳ��������Ƽ���ֵ���������ֵ��ʲô�����������ȷ���Բ�����
    self.epistemicVariables                = {}

  def _localWhatDoINeed(self): ����һ����sample�ж���ķ�����
    """
      This method is a local mirror of the general whatDoINeed method.
	  def�Ǻ�����Ҳ��һ�ַ�����һ������Ҫʲô�ķ�����
      It is implmented here because this Sampler requests special objects
      @ In, None
      @ Out, needDict, dict, dictionary of objects needed
    """
    needDict = Sampler._localWhatDoINeed(self) 
	#����Ӧ���˳��������һ���������������Ƹ�needDict��������һ��ѡ��ķֲ�������Dict�Ƿֲ����
	#�²�needDict����Ҫ�����ķֲ���
    for hybridsampler in self.hybridStrategyToApply.values():
	#�����ǽ���ϳ��������е�ֵ��ѭ����������������
      preNeedDict = hybridsampler.whatDoINeed()
      for key,value in preNeedDict.items():����һ�������ֵ��ѭ����
        if key not in needDict.keys():
          needDict[key] = []
        needDict[key] = needDict[key] + value
		#��仰���Ǻ����ף����߲²�value���Ƿֲ����͡�
    return needDict

  def localStillReady(self, ready):
    """
      first perform some check to understand what it needs to be done possibly perform an early return
	  ��һ�μ�顣��������������������������Ϊʲô�ڹ���Ŀ¼�н��е�һ���ܽ��Ե�XML�ļ�������һ�����ԡ�
	  ���ǵ����Ժ󣬲�֪��Ϊʲô���޸��ˡ�
	  �о�����дһ���ܽ��XML�ļ��Ĺ��̡�
      ready is returned
      @ In,  ready, bool, a boolean representing whether the caller is prepared for another input.
	  ������һ�������߼�����������Ƿ�׼�����ˡ�
      @ Out, ready, bool, a boolean representing whether the caller is prepared for another input.
    """
    self._endJobRunnable = max((len(self.RunQueue['queue']),1))
	#�²��ǵ�ǰ�����������Ƿ��м������С�
    if(len(self.RunQueue['queue']) != 0 or self.counter == 0):
	#
      ready = True
    else:
      if self.printEndXmlSummary: ����һ���߼��жϡ���ΪprintEndXmlSummary��һ���߼����������ҿ���д�ļ���
        myFile = open(os.path.join(self.workingDir,self.name + "11_outputSummary.xml"),'w') 
		�ɹ����顣��������ط���ͨ��һ�������������������������������ʽ����Ҫ�����ṹ��֪ʶ�ˡ�
		���ǽ���һ���ļ���ͨ���򿪵ķ�ʽ����һ��xml�ļ���ͨ��·���ķ�ʽ�����ƶ���·�������ƽ���һ���ļ��� 
        for treeNode in self.TreeInfo.values():
		     #treeNode��һ����treeinfo.value�е�һ��������������һЩ���ԣ�
          treeNode.writeNodeTree(myFile)
        myFile.close()
      ready = False
    return ready

  def _retrieveParentNode(self,idj):
    """
      Grants access to the parent node of a particular job
      @ In, idj, string, the identifier of a job object
	  ������һ��job���ַ�����
      @ Out, parentNode, TreeStructure.Node, the parent node of the job linked to idj
	  ÿһ��job����һ��ID������Ӧÿһ��ID����һ�����νṹ��������һЩ��Ϣ��
	  ����Ǹ��ڵ㣬һ�����νṹ��
    """
    if(idj == self.TreeInfo[self.rootToJob[idj]].getrootnode().name):
	#���Կ�����ô��ķ��������ϲ����������Ϣ��Ȼ���ǻ��ID��������ݵĲ�����ȣ��Ͱ����Խṹ����Ϣ
	#���ݸ����ڵ㡣
      parentNode = self.TreeInfo[self.rootToJob[idj]].getrootnode()

    else:
      parentNode = list(self.TreeInfo[self.rootToJob[idj]].getrootnode().iter(idj))[0]
	  #�������ƥ�䣬���ǻḳֵ�������ʲô�����أ�
    return parentNode

  def localFinalizeActualSampling(self,jobObject,model,myInput,genRunQueue=True):
    """
      General function (available to all samplers) that finalize the sampling
      calculation just ended.����һ��ͨ�õķ������߷��̣�ÿһ���������������á�ȥ
	  finalize��ʲô��˼��
	  In this case (DET), The function reads the
      information from the ended calculation, updates the working variables, and
      creates the new inputs for the next branches
	  �ǳ���Ҫ��1�����ڡ���Ҫ������µķ�֧��Ϣ��������
	  �ӽ����ļ����ж�ȡ��Ϣ�����¹���������Ȼ��Ϊ�µķ�֧����һ���µı�����
      @ In, jobObject, instance, an instance of a JobHandler һ����������ʵ����
      @ In, model, model instance, it is the instance of a RAVEN model
      @ In, myInput, list, the generating input  # myinput��һ���б�������һ������
      @ In, genRunQueue, bool, optional, True if the RunQueue needs to be updated
      @ Out, None
    """
    self.workingDir = model.workingDir  
	#���ǻ��ģ�͵Ĺ���Ŀ¼��Ҳ���ǿ�ִ�г����Ŀ¼��
    # returnBranchInfo = self.__readBranchInfo(jobObject.output)
    # Get the parent element tree (xml object) to retrieve the information needed to create the new inputs
	#��ø��ڵ����Ϣ��
    parentNode = self._retrieveParentNode(jobObject.identifier)
	#jobObject��һ����������ʵ�������еı�ʶ����job���������ݵ�ʶ�����
    # set runEnded and running to true and false respectively
	#���ý�������������û���жϣ�û���߼�ֵ��ֱ���жϣ�
    parentNode.add('runEnded',True)
    parentNode.add('running',False)
    parentNode.add('endTime',self.actualEndTime)
	#��Щ�������νڵ�����ԡ������ֵ䡣��addȥ���ӡ������Ǹ��¡�addӦ���ǽ������õ���˼��
    # Read the branch info from the parent calculation (just ended calculation)
    # This function stores the information in the dictionary 'self.actualBranchInfo'��˵����ǰ�ķ�֧��Ϣ��һ���ֵ������ݽṹ��
    # If no branch info, this history is concluded => return

    ## There are two ways to get at the working directory from the job instance
    ## and both feel a bit hacky and fragile to changes in the Runner classes.
    ## They are both listed below and the second inevitably stems from the first.
    ## I am wondering if there is a reason we cannot use the model.workingDir
    ## from above here? Granted the job instance should have a snapshot of
    ## whatever the model's current working directory was for that evaluation,
    ## and it could have changed in the meantime, so I will keep this as is for
    ## now, but note this should be re-evaluated in the future. -- DPM 4/12/17
    # codeModel = jobObject.args[0] ���ڵ�����������ԣ�����code�����͡�
    # jobWorkingDir = codeModel.workingDir
    kwargs = jobObject.args[3]
	#������²⣬�������Ӧ����һ���б�
    stepWorkingDir = kwargs['WORKING_DIR']
    jobWorkingDir = os.path.join(stepWorkingDir,kwargs['prefix'] if 'prefix' in kwargs.keys() else '1')

    ## This appears to be the same, so I am switching to the model's workingDir
    ## since it is more directly available and less change to how data is stored
    ## in the args of a job instance. -- DPM 4/12/17
    # jobWorkingDir = self.workingDir

    if not self.__readBranchInfo(jobObject.getMetadata()['outfile'], jobWorkingDir):
      parentNode.add('completedHistory', True)
      return False
    # Collect the branch info in a multi-level dictionary ����֧��Ϣ�洢��һ����ά�ֵ䣿��
    endInfo = {'endTime':self.actualEndTime,'endTimeStep':self.actualEndTs,'branchDist':list(self.actualBranchInfo.keys())[0]}
    endInfo['branchChangedParams'] = self.actualBranchInfo[endInfo['branchDist']]
	# self.actualEndTs����һ������ʱ��Ĳ�����
    # check if RELAP7 mode is activated, in case prepend the "<distribution>" string
    if any("<distribution>" in s for s in self.branchProbabilities.keys()):
      endInfo['branchDist'] = list(self.toBeSampled.keys())[list(self.toBeSampled.values()).index(endInfo['branchDist'])]
	  #toBeSampled ��һ���ֵ䣬�����˳��������Ͳ������ӵķֲ���
      #endInfo['branchDist'] = "<distribution>"+endInfo['branchDist']
	  #ȷʵ�����ָ�ʽ��
    parentNode.add('actualEndTimeStep',self.actualEndTs)
    # # Get the parent element tree (xml object) to retrieve the information needed to create the new inputs
	#��ø��ڵ���Ϣ�������µ��ӽڵ㡣
    # if(jobObject.identifier == self.TreeInfo[self.rootToJob[jobObject.identifier]].getrootnode().name):
	#
	#endInfo['parentNode'] = self.TreeInfo[self.rootToJob[jobObject.identifier]].getrootnode()
    # else: endInfo['parentNode'] = list(self.TreeInfo[self.rootToJob[jobObject.identifier]].getrootnode().iter(jobObject.identifier))[0]
    endInfo['parentNode'] = parentNode
    # get the branchedLevel dictionary
    branchedLevel = {}  �������ֵ䣬[]���б�������Ԫ�飬{}���ֵ䣬����key����ֵ����һ��һ�Ĺ�ϵ��
	#����������Ǹ��ڵ��г�������������ֵ��
    for distk, distpb in zip(endInfo['parentNode'].get('SampledVarsPb').keys(),endInfo['parentNode'].get('SampledVarsPb').values()):
	#zip�������ǰ��������������һ��Ԫ�档Ȼ��ѭ����Ҳ����ѭ�����������ļ�����ֵ����ѭ����
      if distk not in self.epistemicVariables.keys():#������˵�Ƿ��л�ϳ����Ĺؼ��֡�
	  #�������Ĳ�ȷ���Բ����ļ�����Ҫ�����ļ���һ�£�����û�С�
	  #�������ֵ��key
        branchedLevel[distk] = utils.index(self.branchProbabilities[distk],distpb)
		#��֧ˮƽ�Ƿ�֧����
    if not branchedLevel:
      self.raiseAnError(RuntimeError,'branchedLevel of node '+jobObject.identifier+'not found!')
    # Loop of the parameters that have been changed after a trigger gets activated
	#�������������Ժ�ѭ���ı�Ĳ�����
    for key in endInfo['branchChangedParams']: #������Ƿ�֧�Ĳ�������һ���ֵ䣬Ӧ�����кܶ�Ĳ�������ֵ�ɡ�
	#��������У�Ϊʲô�е�ʱ����X�е�ʱ���Ǳõ������أ�ͨ��һ�����Խṹ������ͨ��triggerNode���������������壿
	#����������Ѿ������ˡ������Ƿ����Ƿ�ͨ�á�
	#  var = ET.SubElement(triggerNode,'Variable')�����������ӵĳ���
     #var.text=triggerVariable
      endInfo['n_branches'] = 1 + int(len(endInfo['branchChangedParams'][key]['actualValue']))
	  #���������п�����һ���ط����ж��м�����֧�ĵط�������������ֵ�Ժ����ʵ�ʷ�֧����Ӱ��ġ�������3����֪��Ϊʲô
	  #��ʵ�ʵķ�֧����������ĳ������йصġ�
	  #���ǲ���ȱ���˼����˼ά���ղŲ���һ�����⣬����˵�������������Ҫ��֧����ô��֧�����Ƿ��ܹ���Ӧ��
	  #��������ڼ������˵�����ǲ���ģ�����������Ƿ�֧���������ѡ���ˣ����������ͨ�õģ���������Ҫ���Լ��ĳ����н��п��ơ�Ҳ����
	  #���ò�ͬ���ж�������������Ҫ��֧�Ĳ�������������Ϣ���ɡ������������ݻ��Ǵ��ڱ��ֵ�״̬��
	  #�ⲿ��������Լ������ж����������Ǹ��ʷ�֧��β����ж�������
      if(len(endInfo['branchChangedParams'][key]['actualValue']) > 1):
        #  Multi-Branch mode => the resulting branches from this parent calculation (just ended)
        # will be more then 2
		#����ĺ�����˵������仯�Ĳ���ֵ��������1��Ҳ�������ٵ���2����ô��֧��������3����
		#������߼��Ƿ��ǣ�����һ��״̬�Ǳ��ֲ��䣿
        # unchangedPb = probability (not conditional probability yet) that the event does not occur
		#���仯�ĸ���=�¼��������ĸ��ʡ��������������ʡ���
        unchangedPb = 0.0
        try:
          # changed_pb = probability (not conditional probability yet) that the event A occurs and the final state is 'alpha' """
		  #�仯�ĸ���=���Ƿ�֧���ʣ�
          for pb in range(len(endInfo['branchChangedParams'][key]['associatedProbability'])):
		  #�ǳ��ص�Ĳ��֡���һ��ѭ�����仯����״̬����ظ��ʡ����ѭ����һ��ѭ��������ȡ����������ظ����еĶ��١�
            unchangedPb = unchangedPb + endInfo['branchChangedParams'][key]['associatedProbability'][pb]
			#����ĸ���=һ���ۼӹ��̡��Ǳ仯��������ظ��ʵ��б�����мӺ͡�
			#����һ��ѭ���ۼӣ����仯�ĸ���=associatedProbability*һ�����������Ǳ�������һ���ۼӵ�ѭ����
        except KeyError:
          self.raiseAWarning("KeyError:"+str(key))
        if(unchangedPb <= 1):
          endInfo['branchChangedParams'][key]['unchangedPb'] = 1.0-unchangedPb
		  #��ֵ��䣬�����õĲ��仯�ĸ���С��1.��ô�����ֵ�������ݽṹ��
		  #���⣺�����Ƿ�����߼�����ΪʲôҪ��1��һ���أ�
        else:
          self.raiseAWarning("unchangedPb > 1:"+str(unchangedPb))
      else:
        # Two-Way mode => the resulting branches from this parent calculation (just ended) = 2
		#�����Ƕ���֧������Ҳ���Ǹ��ڵ����ݲ����Լ��仯�Ĺ��̡�
        if branchedLevel[endInfo['branchDist']] > len(self.branchProbabilities[endInfo['branchDist']])-1:
		#��������Ƚϣ���ô��֧ˮƽ�����һ����������֪��ʲô���塣
          pb = 1.0
        else:
          pb = self.branchProbabilities[endInfo['branchDist']][branchedLevel[endInfo['branchDist']]]
		  #������������жϣ����Ӧ����һ������ֵ��������һ��ʲô���ݽṹ�أ�
        endInfo['branchChangedParams'][key]['unchangedPb'] = 1.0 - pb
        endInfo['branchChangedParams'][key]['associatedProbability'] = [pb]
		#����ĸ��ʺ���ػ��Э�����ʵĺ���1.ʵ�����н�����ǣ��ش�ʵ�ʽ���������ġ��ؼ�����ôȡ��֧�еĸ��ʡ�
		#Ҳ������elf.branchProbabilities�ľ���ṹ��
    self.branchCountOnLevel = 0
    # # set runEnded and running to true and false respectively
    # endInfo['parentNode'].add('runEnded',True)
    # endInfo['parentNode'].add('running',False)
    # endInfo['parentNode'].add('endTime',self.actualEndTime)
    # The branchedLevel counter is updated ���ó�ʼֵ
    if branchedLevel[endInfo['branchDist']] < len(self.branchProbabilities[endInfo['branchDist']]):
      branchedLevel[endInfo['branchDist']] += 1
	  #��������ʽ�ƶϣ�branchedLevel[endInfo['branchDist']]��һ���б��ֵ��
    # Append the parent branchedLevel (updated for the new branch/es) in the list tha contains them
    # (it is needed in order to avoid overlapping among info coming from different parent calculations)
    # When this info is used, they are popped out
    self.branchedLevel.append(branchedLevel)
    # Append the parent end info in the list tha contains them
    # (it is needed in order to avoid overlapping among info coming from different parent calculations)
    # When this info is used, they are popped out
    self.endInfo.append(endInfo)
    # Compute conditional probability
    self.computeConditionalProbability()  ������ר�ŵļ����������ʵĺ�����
    # Create the inputs and put them in the runQueue dictionary (if genRunQueue is true)
    if genRunQueue:
      self._createRunningQueue(model,myInput)
    return True

  def computeConditionalProbability(self,index=None):
    """
      Function to compute Conditional probability of the branches that are going to be run.
      The conditional probabilities are stored in the self.endInfo object
	  �ǳ��ص��һ�δ��룬�����֧�����ǵ��������ʡ�������ʴ洢�ڽ�����Ϣ�Ķ������档endinfo�������档
      @ In, index, int, optional, position in the self.endInfo list (optional). Default = 0
      @ Out, None
    """
    if not index:
      index = len(self.endInfo)-1
	  #len(self.endInfo)�������һ��ʲô�����أ����ж���ʵ�����Եģ�����������һ���������ж��ٸ�ʵ�����󡣿��ܷ���
	  #����endInfo����������ı�ʶ�������ǲ�ͬ�İɡ�
    try:һ���쳣�Ĵ���
      parentCondPb = self.endInfo[index]['parentNode'].get('conditionalPbr')
	  #ͨ��endInfo��һ�������е����࣬��ø��ڵ���������ʡ�
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
						  #��֧�仯�����Ĳ�������Ǹ��ڵ�����������뵱ǰ�ڵ�Ĳ�����ʵĳ˻���
      for pb in range(len(self.endInfo[index]['branchChangedParams'][key]['associatedProbability'])):
	  #pb��һ��������
        self.endInfo[index]['branchChangedParams'][key]['changedConditionalPb']
		      .append(parentCondPb*float(self.endInfo[index]['branchChangedParams'][key]['associatedProbability'][pb]))

  def __readBranchInfo(self,outBase=None,currentWorkingDir=None):
    """
      Function to read the Branching info that comes from a Model
	  ��������һ�����á���������Ƕ�ȡ��ģ�����ķ�֧��Ϣ��������һ���ص㡣
      The branching info (for example, distribution that triggered, parameters must be changed, etc)
      are supposed to be in a xml format
	  �����Ƕ�ȡ������ģ�͵ķ�֧��Ϣ�����紥���ķֲ�������Ĳ����ȣ���Щ�ǻ���XML��ʽ���ļ���
      @ In, outBase, string, optional, it is the output root that, if present, 
	  is used to construct the file name the function is going to try reading.

      @ In, currentWorkingDir, string, optional, it is the current working directory.
	   If not present, the branch info are going to be looked in the self.workingDir
      @ Out, branchPresent, bool, true if the info are present (a set of new branches need to be run),
	        false if the actual parent calculation reached an end point
	  ����ǲ����߼���������棬������Ϣ���еġ�����Ǽ٣����֧�Ѿ��������յ㡣
    """
    # Remove all the elements from the info container
    del self.actualBranchInfo
    branchPresent = False
    self.actualBranchInfo = {}#�������ǰ�ڵ���Ϣ���г�ʼ����
    # Construct the file name adding the outBase root if present
    filename   = outBase + "_actual_branch_info.xml" if outBase else "actual_branch_info.xml"
	#outBase��һ��ѡ������ѡ�񣬾�����������ȡ��XML�ļ��������û�о�����Ĭ�ϵ��ļ�����
    workingDir = currentWorkingDir if currentWorkingDir is not None else self.workingDir

    if not os.path.isabs(filename):
	#��һ���ж���䣬����ļ����Ǿ���·��������true
      filename = os.path.join(workingDir,filename)

    if not os.path.exists(filename):
	#�ж��ļ����Ƿ���ڡ����������Ϊtrue��
      self.raiseADebug('branch info file ' + os.path.basename(filename) +' has not been found. => No Branching.')
      return branchPresent
    # Parse the file and create the xml element tree object#�������һ����֧��Ϣ��������µķ�֧XML�ļ���
    #try:
    branchInfoTree = ET.parse(filename)
	#�²������xml������һ�����ܡ��������ļ���Ϣ�ľ�����ݸ���֧��Ϣ���ϡ�
    self.raiseADebug('Done parsing '+filename)
    root = branchInfoTree.getroot()
	#��XMl�����νṹ�ĸ�Ԫ�ظ���root��
    # Check if endTime and endTimeStep (time step)  are present... In case store them in the relative working vars
    #try: #Branch info written out by program, so should always exist.
	#�ж��Ƿ��֧�ļ��и��˽���ʱ�������������Ƿ����ֵ���ʱ����ƻ��ǲ������ƣ�
	#�²⣬�Ƿ��������֧������Ϊ�Ȳ���������������Ϣ�����Զ��������Ϊ����ʱ�䣿һ����������ϵ�ʱ�䡣
    self.actualEndTime = float(root.attrib['end_time'])
	#ͨ����ȡ����XML�ļ����ѽ���ʱ�丳��������
    self.actualEndTs   = int(root.attrib['end_ts']) if  'end_ts' in root.attrib.keys() else -1
    #except? pass
    # Store the information in a dictionary that has as keywords the distributions that triggered
    for node in root: 
	#���Ӧ����һ��ET���еĺ���������ѭ�����νṹ�е�Ԫ�ػ��ӽڵ㡣
      if node.tag == "Distribution_trigger":
        distName = node.attrib['name'].strip()
		#��ȡ�ֲ����ơ�
        self.actualBranchInfo[distName] = {}
        for child in node:
          self.actualBranchInfo[distName][child.text.strip()] =
		  {'varType':child.attrib['type'].strip(),'actualValue':child.attrib['actual_value'].strip().split(),
		  'oldValue':child.attrib['old_value'].strip()}
          if 'probability' in child.attrib:
            asPb = child.attrib['probability'].strip().split()
			#��ֵ�������ʡ�
            self.actualBranchInfo[distName][child.text.strip()]['associatedProbability'] = []
            #self.actualBranchInfo[distName][child.text.strip()]['associatedProbability'].append(float(asPb))
            for index in range(len(asPb)):
              self.actualBranchInfo[distName][child.text.strip()]['associatedProbability'].append(float(asPb[index]))
			  #����ܹؼ�����䣬û������
      # we exit the loop here, because only one trigger at the time can be handled  right now
	  #�ǳ��ص���ǣ�ѭ��Ҫ��������Ϊ��ǰֻ��һ�����������Լ��
	  #���⣬������������������������޸ģ�
      break
    # remove the file
    if self.removeXmlBranchInfo:
      os.remove(filename) ΪʲôҪ������ļ�ɾ����
    branchPresent = True
    return branchPresent

  def _createRunningQueueBeginOne(self,rootTree,branchedLevel, model,myInput):
  #�Ӻ���˵�������ǵ�һ���ڵ㣿
    """
      Method to generate the running internal queue for one point in the epistemic
      space. It generates the initial information to instantiate the root of a
      Deterministic Dynamic Event Tree.
	  ����һ��������֪��ȷ���Եķ�����
      @ In, rootTree, Node object, the rootTree of the single coordinate in the epistemic space.

      @ In, branchedLevel, dict, dictionary of the levels reached by the rootTree mapped in the internal grid dictionary 
	  (self.branchProbabilities)
      @ In, model, Models object, the model that is used to explore the input space (e.g. a code, like RELAP-7)
	  ����д��һ�����Զ�̬�¼�����ģ��
      @ In, myInput, list, list of inputs for the Models object (passed through the Steps XML block)
	  �����ע������Ϣ��ͨ��step��XMLģ�������code��Ҫ�����������ļ���
      @ Out, None
    """
    # add additional edits if needed
    model.getAdditionalInputEdits(self.inputInfo)

    precSampled = rootTree.getrootnode().get('hybridsamplerCoordinate')
	#����Ӧ����һ���߼�������
    rootnode    =  rootTree.getrootnode()
    rname       = rootnode.name
    rootnode.add('completedHistory', False)
	#ͨ������֪��add�����õĵ���˼�����ǽ�һ�����νṹ����������Ϊһ��ֵ��
    # Fill th values dictionary in
    if precSampled:
      self.inputInfo['hybridsamplerCoordinate'  ] = copy.deepcopy(precSampled)
	  #��precSampled��ֵ��ȿ��������ֵ���Ӷ������Ƿǳ������ı�����һ���ı���һ�����䡣
    self.inputInfo['prefix'                    ] = rname
    self.inputInfo['initiatorDistribution'     ] = []
    self.inputInfo['PbThreshold'               ] = []
    self.inputInfo['ValueThreshold'            ] = []
    self.inputInfo['branchChangedParam'        ] = [b'None']
    self.inputInfo['branchChangedParamValue'   ] = [b'None']
    self.inputInfo['startTime'                 ] = -sys.float_info.max
	#�����һ���ǳ�ʼ��һ������ϵͳʱ�䣬Ҳ���ǵ�һ����ʱ�䡣
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
	#�����һ���б���һ�������ȷ���ԣ�Ҳ����DET��֧�Ĳ������������������ơ�Ŀǰ�����ֻ��һ��ֵ��
      self.inputInfo['SampledVars'  ][varname] = self.branchValues[varname][branchedLevel[varname]]
	  #��������������ڼ�����ɢ��֧����ֵ��
      #self.inputInfo['SampledVars'  ][varname] = self.branchValues[self.toBeSampled[varname]][branchedLevel[self.toBeSampled[varname]]]
      self.inputInfo['SampledVarsPb'][varname] = self.branchProbabilities[varname][branchedLevel[varname] ]
	  #�����ȷ���Բ�������һ��������Ӧ�ĸ���ֵ��
      #self.inputInfo['SampledVarsPb'][varname] = self.branchProbabilities[self.toBeSampled[varname]][branchedLevel[self.toBeSampled[varname]]]
    # constant variables
    self._constantVariables()
	#���û�����û�ϳ������������ǹ̶�ֵ��

    if precSampled:
      for precSample in precSampled:
        self.inputInfo['SampledVars'  ].update(precSample['SampledVars'])
        self.inputInfo['SampledVarsPb'].update(precSample['SampledVarsPb'])
    self.inputInfo['PointProbability' ] = reduce(mul, self.inputInfo['SampledVarsPb'].values())
	#reduce�����ǰѺ���ĵ��������еĵ�һ�������͵ڶ�������������mul������Ҳ������ˣ�Ȼ�����ڵ���������ˡ�
	#һֱ�����
    self.inputInfo['ProbabilityWeight'] = self.inputInfo['PointProbability' ]
    self.inputInfo.update({'ProbabilityWeight-'+key.strip():value for key,value in self.inputInfo['SampledVarsPb'].items()})

    if(self.maxSimulTime):
	#Raven���ڿ��Ʒ���ʱ��ı�����
      self.inputInfo['endTime'] = self.maxSimulTime
	  #Ҳ�����������ָ����������ʱ�䣬��������Ϣ�еĽ���ʱ��������ʱ�䡣
    # Add the new input path into the RunQueue system
	#�������Ժ������µ�����·�����������ϵͳ�С�
    newInputs = {'args':[str(self.type)], 'kwargs':dict(self.inputInfo)}
    for key,value in self.inputInfo.items():
      rootnode.add(key,copy.copy(value))
    self.RunQueue['queue'].append(newInputs)
	#����ǰ���ĵĺ��壬RunQueue��һ�����ж��е��ֵ䣬����queue��һ������ֵ�����͡������м������С�
	#append�����������������Ԫ�أ�
    print(self.inputInfo['prefix'])#��Ӧ����һ��DET�ı�ʶ����
    self.RunQueue['identifiers'].append(self.inputInfo['prefix'])
    self.rootToJob[self.inputInfo['prefix']] = rname
    del newInputs
    self.counter += 1#�������ۼӣ�������ʲô��

  def _createRunningQueueBegin(self,model,myInput):
    """
      Method to generate the running internal queue for all the points in
      the epistemic space. 
	  Ϊ����֪��ȷ���Կռ��е����е㣬�������е��ڲ����С�
	  It generates the initial information to
      instantiate the roots of all the N-D coordinates to construct multiple
      Deterministic Dynamic Event Trees.
      @ In, model, Models object, the model that is used to explore the input space (e.g. a code, like RELAP-7)
	  #��Ҫ�˽⣬����Ҫ����һ����R7����Ĳ��ԣ�������ʲô���ӡ�
      @ In, myInput, list, list of inputs for the Models object (passed through the Steps XML block)
      @ Out, None
    """
    # We construct the input for the first DET branch calculation'
    # Increase the counter
	#Ϊ��һ��DET���㹹��һ�����룬�ۼӼ�������
    # The root name of the xml element tree is the starting name for all the branches
    # (this root name = the user defined sampler name)
    # Get the initial branchedLevel dictionary (=> the list gets empty)
    branchedLevel = self.branchedLevel.pop(0)
    for rootTree in self.TreeInfo.values():
      self._createRunningQueueBeginOne(rootTree,branchedLevel, model,myInput)
	  #�����һ�����õĹ��̡�

  def _createRunningQueueBranch(self,model,myInput,forceEvent=False):
    """
      ����һ�����еĶ��з�֧���ǳ���Ҫ��һ��������
	  Method to generate the running internal queue right after a branch occurred
      It generates the the information to insatiate the branches' continuation of the Deterministic Dynamic Event Tree
	  ����һ������ȷ����DET��������������DET����˵��ÿһ�ε�DET��ȷ����DET������ȷ��������������ѭ����
      @ In, model, Models object, the model that is used to explore the input space (e.g. a code, like RELAP-7)
	  ����һ��ģ�ͣ���ɢ����ս�
      @ In, myInput, list, list of inputs for the Models object (passed through the Steps XML block)
	  ͨ��stepXML�ļ���ͨ���ҵ����룬�г���Ҫ����ģ�͵Ĳ������������������
      @ In, forceEvent, bool, if True the events are forced to happen (basically, the "unchanged event" is not created at all)
	  ��ֻһ�������߼������Ϊ�棬��ʱ��ǿ�Ʒ�����
      @ Out, None
    """
    # The first DET calculation branch has already been run'
	Ϊʲô˵��һ��DET�����֧�Ѿ������ˣ���Ϊ��һ��one�ļ�����С�
    # Start the manipulation:

    #  Pop out the last endInfo information and the branchedLevel
    branchedLevelParent     = self.branchedLevel.pop(0)
    endInfo                 = self.endInfo.pop(0)
    self.branchCountOnLevel = 0 #����һ�����ͱ���������ֵΪ0-2���õ�ǰ��֧ˮƽΪ0
    # n_branches = number of branches need to be run  �е���XML�ܽ�����д�������ж��ٸ���֧�Ĳ��֡�������
    nBranches = endInfo['n_branches']
    # Check if the distribution that just triggered hitted the last probability threshold .
	#����Ƿ񴥷��ķֲ��ҵ����ĸ�����ֵ��
    # In case we create a number of branches = endInfo['n_branches'] - 1 => the branch in
    # which the event did not occur is not going to be tracked
    if branchedLevelParent[endInfo['branchDist']] >= len(self.branchProbabilities[endInfo['branchDist']]):
	#������ڵ��з�֧�ֲ�����������ʵ�����ķ�֧�ֲ����²�˵���Ѿ��ﵽ�˷ֲ������һ����ֵ��
      self.raiseADebug('Branch ' + endInfo['parentNode'].get('name') + ' hit last Threshold for distribution ' + endInfo['branchDist'])

      self.raiseADebug('Branch ' + endInfo['parentNode'].get('name') + ' is dead end.')
      self.branchCountOnLevel = 1
      nBranches -= 1
    else:
      if forceEvent == True:
	  #������һ��ǿ���Եı�ʶ������ǿ�Ʒ�֧��
        self.branchCountOnLevel = 1
        nBranches -= 1
    # Loop over the branches for which the inputs must be created
	�ڷ�֧��ѭ����
    for _ in range(nBranches):#����һ��ѭ����nBranches��һ�����ͱ������������ʻ������������Ϊ3��2.
	      del self.inputInfo #��ɾ��������Ϣ
      self.counter += 1 #�������ۼ�
      self.branchCountOnLevel += 1 #��֧ˮƽ�ۼӡ�
      branchedLevel = copy.deepcopy(branchedLevelParent)
	  #��ȸ��ƣ������ڵ�ķ�֧ˮƽ��ֵ����ǰ�Ľڵ㡣
      # Get Parent node name => the branch name is creating appending to this name  a comma and self.branchCountOnLevel counter
	  #�ǳ���Ҫ������������ݻ��Ľڵ���ļ����ơ�ԭ����ͨ����ȡ���ڵ�ı�ʶ����Ȼ��ӡ�_���ټ��ϵ�ǰ�ķ�֧ˮƽ�ļ�������
	  #����branchCountOnLevel��һ�������ͱ���������ǰ�ӽڵ��֧��ˮƽ��һ�����1-3֮�䡣
      rname = endInfo['parentNode'].get('name') + '-' + str(self.branchCountOnLevel)
	  #�������ԣ��Ѿ�����������䡣rname�ǵ�ǰ�ӽڵ�����ơ�
	  #��������Ƿֲ��ʾ��һ�����������ֶ��Ǹ��ڵ������+��_��+��֧�����������Ƿ�֧�����������ȷ�����أ�
	  #��֧����������nBranches��ȷ���ġ��������֤�����ѭ����
      # create a subgroup that will be appended to the parent element in the xml tree structure
	  #����һ�����ڵ�Ԫ��XML�ļ��е��ӽڵ㡣
      subGroup = ETS.HierarchicalNode(self.messageHandler,rname)
	  #���⣺���������֪����ʲô��˼��self.messageHandlerҲ��֪��ʲô��˼��
      subGroup.add('parent', endInfo['parentNode'].get('name'))
	  #�����ӽڵ��и��ڵ����
      subGroup.add('name', rname)
	  #�����ӽڵ�������Ѿ����˷�֧��
      subGroup.add('completedHistory', False)
	  #��Ȼ�Ѿ������ӽڵ㣬��ô��ɵ���ʷ���Ǽ١�
      # condPbUn = conditional probability event not occur
      # condPbC  = conditional probability event/s occur/s
      condPbUn = 0.0
      condPbC  = 0.0
      # Loop over  branchChangedParams (events) and start storing information,
      # such as conditional pb, variable values, into the xml tree object
	  #ѭ����֧���������洢���ʡ���������ֵ���������ʣ��Լ���������
      branchChangedParamValue = []
      branchChangedParamPb    = []
      branchParams            = []
	  #�����ǳ�ʼ���ӽڵ�仯���ʵ��б���������ֵ�����������Լ��������ơ��ǵ�ǰ�����еı������ȸ�ֵ�ڲ�����
      #subGroup.add('branchChangedParam',endInfo['branchChangedParams'].keys())

      for key in endInfo['branchChangedParams'].keys():
        #subGroup.add('branchChangedParam',key)
        branchParams.append(key)
        if self.branchCountOnLevel != 1:#�����ǰ�ķ�֧ˮƽ����1��1�����䡣��ô����2����3.
          branchChangedParamValue.append(endInfo['branchChangedParams'][key]['actualValue'][self.branchCountOnLevel-2])
		  #branchChangedParamValue.append(endInfo['branchChangedParams'][key]['actualValue'][0����1]��
		  #���⣺����������﷨�����Բ²��֧�仯����ֵ���շ�֧ˮƽ��ֵ��
		  #������������һ�����Ի�ʵ�����������Ϣ��һ���б�Ԫ�ص������뵱ǰ��֧����ˮƽ��ء�
          branchChangedParamPb.append(endInfo['branchChangedParams'][key]['associatedProbability'][self.branchCountOnLevel-2])

          #subGroup.add('branchChangedParamValue',endInfo['branchChangedParams'][key]['actualValue'][self.branchCountOnLevel-2])
          #subGroup.add('branchChangedParamPb',endInfo['branchChangedParams'][key]['associatedProbability'][self.branchCountOnLevel-2])
          #condPbC.append(endInfo['branchChangedParams'][key]['changedConditionalPb'][self.branchCountOnLevel-2])
          condPbC = condPbC + endInfo['branchChangedParams'][key]['changedConditionalPb'][self.branchCountOnLevel-2]
		  #�¼���������������=�����һ���б�
          subGroup.add('happenedEvent',True)
		  #�з�֧�����¼�����Ϊ��
        else:#�����ǵ�ǰ��֧����Ϊ1
          subGroup.add('happenedEvent',endInfo['parentNode'].get('happenedEvent'))
		  #�ӽڵ�������һ���������¼����߼�ֵ��
          branchChangedParamValue.append(endInfo['branchChangedParams'][key]['oldValue'])
		  #����1�ķ�֧����ֵ�Ǹ��ڵ�ľ�ֵ��
          branchChangedParamPb.append(endInfo['branchChangedParams'][key]['unchangedPb'])
		  #�ӽڵ�ĸ����Ǹ��ڵ�Ĳ���ĸ���
          #subGroup.add('branchChangedParamValue',endInfo['branchChangedParams'][key]['oldValue'])
          #subGroup.add('branchChangedParamPb',endInfo['branchChangedParams'][key]['unchangedPb'])
          #condPbUn.append(endInfo['branchChangedParams'][key]['unchangedConditionalPb'])
          condPbUn =  condPbUn + endInfo['branchChangedParams'][key]['unchangedConditionalPb']
		  #����ĸ��ʾ��Ǹ��ڵ��в���ĸ��ʡ�
      subGroup.add('branchChangedParam',branchParams)
	  #����һ���仯�������Ƶ���Ϣ��
      # add conditional probability
	  #������������
      if self.branchCountOnLevel != 1:#������1���Ǳ仯�ķ�֧����仯����ֵ�������Լ����ƽ��и�ֵ��
        subGroup.add('conditionalPbr',condPbC)
        subGroup.add('branchChangedParamValue',branchChangedParamValue)
        subGroup.add('branchChangedParamPb',branchChangedParamPb)
      else:#����ǵ�ǰ��֧��������1.Ҳ���ǲ���ġ�
        subGroup.add('conditionalPbr',condPbUn)
        subGroup.add('branchChangedParamValue',branchChangedParamValue)
        subGroup.add('branchChangedParamPb',branchChangedParamPb)
      # add initiator distribution info, start time, etc.

      subGroup.add('initiatorDistribution',self.toBeSampled[endInfo['branchDist']])
	  #��ֵ�ӽڵ�ķֲ���Ϣ��ֵ������Ҫ�����ķֲ����͡�
      subGroup.add('startTime', endInfo['parentNode'].get('endTime'))
	  #�ӽڵ�Ŀ�ʼʱ����Ǹ��ڵ�Ľ���ʱ�䣬ΪʲôҪ��һ��ʱ������أ�������ͬ���������
      # initialize the endTime to be equal to the start one... It will modified at the end of this branch
	  #�ȳ�ʼ������ʱ��Ϊ��ʼʱ�䣬Ȼ���ڷ�֧�������ڽ��б����
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
	  #�ڽ������ڵ���Ϣ����������ӽڵ���Ϣ��
      # Fill the values dictionary that will be passed into the model in order to create an input
      # In this dictionary the info for changing the original input is stored
	  #����һ����Ҫ���ݸ�ģ�͵��ֵ䣬��Ϊģ�͵����롣
      self.inputInfo = {'prefix':rname,'endTimeStep':endInfo['endTimeStep'],
                'branchChangedParam':subGroup.get('branchChangedParam'),
                'branchChangedParamValue':subGroup.get('branchChangedParamValue'),
                'conditionalPb':subGroup.get('conditionalPbr'),
                'startTime':endInfo['parentNode'].get('endTime'),
				#���µĽڵ㿪ʼ��ʲôʱ�����������֧�����ﵽ�Ժ��������������п���������������δ��ݵġ������ԡ�
				#���²⣬����ﵽ�˷�֧����������Ҫ��¼��֧������һЩ���ԣ������֧���ʣ�ʱ�䣬�����ݡ�������code��ʲô��ϵ������������أ�
                'RAVEN_parentID':subGroup.get('parent'),
                'RAVEN_isEnding':True}���������ʲô��û�о��庬�塣������
			#inputInfo��һ��������Ϣ�ֵ䣬�����Ĺؼ�����Ϣ�����У���ֵ��Ҫ���ú�����á�

      #'RAVEN_parentID','RAVEN_isEnding'
      self.inputInfo['happenedEvent'] = subGroup.get('happenedEvent')
      # add additional edits if needed
	  #������һ��ģ���еķ�����
      model.getAdditionalInputEdits(self.inputInfo)
      # add the newer branch name to the map
      self.rootToJob[rname] = self.rootToJob[subGroup.get('parent')]
	  #�����get��add������������������жԶ������ԵĲ�����get����ȡֵ��add���Ǹ�ֵ�����ٲ²���������
      # check if it is a preconditioned DET sampling, if so add the relative information
      precSampled = endInfo['parentNode'].get('hybridsamplerCoordinate')
      if precSampled:
	  #�²�����ϳ����������û�У�Ϊnone����ִ�С������Ϊ�գ���ִ�С�
        self.inputInfo['hybridsamplerCoordinate'] = copy.deepcopy(precSampled)
        subGroup.add('hybridsamplerCoordinate', precSampled)
      # Check if the distribution that just triggered hitted the last probability threshold .
	  #����Ƿ�ֲ����ü���������һ��������ֵ��
      #  In this case there is not a probability threshold that needs to be added in the input
      #  for this particular distribution
      if not (branchedLevel[endInfo['branchDist']] >= len(self.branchProbabilities[endInfo['branchDist']])):
	  #�²����Ѿ���֧�������Ƿ���ڷ�֧������ʵ������������֧����ʵ�������������˸����������ɢ������������ڵ����ˡ���Ϊ�棬�ͽ�����
        self.inputInfo['initiatorDistribution'] = [self.toBeSampled[endInfo['branchDist']]]
        self.inputInfo['PbThreshold'           ] = [self.branchProbabilities[endInfo['branchDist']][branchedLevel[endInfo['branchDist']]]]
        self.inputInfo['ValueThreshold'        ] = [self.branchValues[endInfo['branchDist']][branchedLevel[endInfo['branchDist']]]]
      #  For the other distributions, we put the unbranched thresholds
      #  Before adding these thresholds, check if the keyword 'initiatorDistribution' is present...
      #  (In the case the previous if statement is true, this keyword is not present yet
      #  Add it otherwise
      if not ('initiatorDistribution' in self.inputInfo.keys()):
	  #�ж���������Ϣ�ļ����Ƿ��зֲ������ã�
        self.inputInfo['initiatorDistribution' ] = []
        self.inputInfo['PbThreshold'           ] = []
        self.inputInfo['ValueThreshold'        ] = []
      # Add the unbranched thresholds  ����ǲ������ڽضϵĲ��֣��������С��һ������ֵ�Ͳ���֦�ˣ�
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
	  #����ĵ���Ƹ���=�����������ʵ��۳˻���Ȼ���ڳ����ӽڵ���������ʡ�
      self.inputInfo['ProbabilityWeight'] = self.inputInfo['PointProbability' ]
	  #����Ȩ�ؾ��Ƿ�֧��ĸ��ʡ�
      self.inputInfo.update({'ProbabilityWeight-'+key.strip():value for key,value in self.inputInfo['SampledVarsPb'].items()})
      # Add the new input path into the RunQueue system
      newInputs = {'args': [str(self.type)], 'kwargs':dict(self.inputInfo)}
	  #����������ʽnewInputs��һ���ֵ��ͱ�����
      self.RunQueue['queue'].append(newInputs)
	  #���ж����ж�����һ���б����б��Ԫ����һ���ֵ䡣�������ķ�����
      self.RunQueue['identifiers'].append(self.inputInfo['prefix'])
      for key,value in self.inputInfo.items():#ϰ���˾ͺ��ˡ������ڱ���һ���ֵ䡣Ҳ����������Ϣ��Ԫ�ض����ֵ䡣
        subGroup.add(key,copy.copy(value))
      popped = endInfo.pop('parentNode')
      subGroup.add('endInfo',copy.deepcopy(endInfo))
      endInfo['parentNode'] = popped
      del branchedLevel

  def _createRunningQueue(self, model, myInput, forceEvent=False):#�����Ǵ���һ�����еĶ��з�֧�������Ǵ���һ�����ж��С����ڻ�ϳ�����
    """
      Function to create and append new inputs to the queue. It uses all the containers have been updated by the previous functions
      @ In, model, Model instance, model instance that can be a Code type, ROM, etc.
      @ In, myInput, list, List of the original inputs
      @ In, forceEvent, bool, True if a branching needs to be forced
	  #forceEvent��һ���߼��������������ڿ���ǿ�Ʒ�֧��
      @ Out, None
    """
    if self.counter >= 1:#����������1.�����������������������ʲô�أ�
      # The first DET calculation branch has already been run��Ҳ���һ����֧����һ�������ķ�֧��
      # Start the manipulation:
      #  Pop out the last endInfo information and the branchedLevel
      self._createRunningQueueBranch(model, myInput, forceEvent)
    else:#�������������1.��˵���ǵ�һ��DET���������е�һ�εĲ��ԡ�
      # We construct the input for the first DET branch calculation'
      self._createRunningQueueBegin(model, myInput)
    return

  def __getQueueElement(self):#�²���߼����ȸ��ݷ�ֵ����������У�Ȼ����ͨ���������ȥ����code���㣿
    """
      Function to get an input from the internal queue system
	  ���������һ������ϵͳ����ô����ϵͳ���е��߼���ʲô��Ҳ����˵��һ���������е��¼��ڵ㣬���ǰ�����з֣�
	  �����н�������о��ǰ��ղ����֣�ÿһ�������Ȼ��������
	  �ڶ���ϵͳ�У��õ�һ�����롣
      @ In, None
      @ Out, jobInput, list, the list of inout (First input in the queue)
	  �����һ��job���롣һ���б�
    """
    # Pop out the first input in queue
	#pop�ķ����ǲ���ȡ������˼�����������˼����ˡ�pop�ĺ�����ɾ���б��е�Ԫ�أ��������Ԫ�ص�ֵ���ء�
	#�ر��ʺϽ��ж��еĲ�������˵����ȡ��һ��ɾ��һ����
    jobInput  = self.RunQueue['queue'      ].pop(0)
	#������Ǵ����ж�����ȡ��һ���ļ�����Ϣ����ɾ��ԭ�����е�Ԫ�ء�
    jobId     = self.RunQueue['identifiers'].pop(0)
	#ȡ�������е�һ����ʶ������ֵ��ɾ�������е���Ϣ��
    #set running flags in self.TreeInfo
    root = self.TreeInfo[self.rootToJob[jobId]].getrootnode()
	#ͨ����ʶ������ýڵ���Ϣ��
    # Update the run information flags
    if (root.name == jobId):#�ڽڵ���Ϣ�У��ڵ�����ֺͶ����е�IDӦ����һ�µġ�
      root.add('runEnded',False)
	  #add�Ǹ���������Ԫ�ء�
      root.add('running',True)
      root.add('queue',False)
    else:
      subElm = list(root.iter(jobId))[0]
      if(subElm):
        subElm.add('runEnded',False)
        subElm.add('running',True)
        subElm.add('queue',False)
		#������ֵ����һ���ģ��Ǹ�ֵ��λ�ò��ԣ�

    return jobInput

  def generateInput(self,model,oldInput):
    """
      This method has to be overwritten to provide the specialization for the specific sampler
      The model instance in might be needed since, especially for external codes,
      only the code interface possesses ӵ��֧�����˼ the dictionary for reading the variable definition syntax
	  �������������д�Ѿ�ȷ�����ض�����������������п�����Ҫģ�͵�ʵ�����ر�����ⲿcode
	  ��Ϊcode�ӿ�ӵ�ж�ȡ���������﷨���ļ��У����ֵ䣿
      @ In, model, model instance, it is the instance of a RAVEN model
      @ In, oldInput, list, a list of the original needed inputs for the model (e.g. list of files, etc. etc)


      @ Out, generateInput, (0,list), list containing the new inputs -in reality it is the model that returns this; 
	  the Sampler generates the value to be placed in the input of the model.
    """
    #NB:����ʾע�����˼�� if someday the DET handles restarts as other samplers do in generateInput, the return code 1 indicates the result
    #  is stored in a restart data object, while 0 indicates a new run has been found.
	#�²���ǣ�δ��DET���������������н�����Ҳ����DET��һЩ�������ܻ����code��������̱仯���仯����ôDETִ�й���������Ҫ����һ��
	#�м������������������ݽṹ����������������ڱ�ʶ�������1�������������ɵģ������0������һ��ȫ�µļ������⡣
    #model.getAdditionalInputEdits(self.inputInfo)
    return 0, self.localGenerateInput(model, oldInput)

  def localGenerateInput(self,model,myInput):
    """
      Function to select the next most informative point for refining the limit
      surface search.
	  ѡ������Ч����һ�������ķ������Ӷ������Ż����������������
      After this method is called, the self.inputInfo should be ready to be sent
      to the model
	  �������������������Ϣ��Ҫ׼�����ݸ�ģ�͡�
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
	  #��������߼������������С�ڵ���1����Ҫ����һ���µĶ��С�Ȼ���ȡ����Ԫ�أ��������Ԫ��Ϊ�ա���˵���Ѿ�������

    ## It turns out the "newerInput" contains all of the information that should
    ## be in inputInfo (which should actually be returned and not stored in the
	#�����е�Ԫ�������е���Ϣ�������ϢҪ��inputInfo���и�ֵ���Ӷ����м��㡣
    ## sampler object, but all samplers do this for now) -- DPM 4/26/17
    self.inputInfo = newerInput['kwargs']
	#['kwargs']���ָ�ֵ��ʽ��ʲô���壿
    return myInput

  def _generateDistributions(self,availableDist,availableFunc):#û���û��������������������DET���ԣ�ע�ͺ�û��Ӱ��
    """
      Generates the distrbutions and functions. 
      It is overloaded here because we need to manage the sub-sampling
      strategies for the Hybrid DET approach
	  �ظ��Ĳ��֣���ΪҪ������ϳ����ķ�����
	 
      @ In, availDist, dict, dict of distributions
      @ In, availableFunc, dict, dict of functions
      @ Out, None
    """
    Grid._generateDistributions(self,availableDist,availableFunc)
    for hybridsampler in self.hybridStrategyToApply.values():
      hybridsampler._generateDistributions(availableDist,availableFunc)

  def localInputAndChecks(self,xmlNode, paramInput):#�����ǣ��������û�б����á�
    """
      Class specific xml inputs will be read here and checked for validity.
	  ��ȡXML�ļ��������Ч�ԡ�
      @ In, xmlNode, xml.etree.ElementTree.Element, The xml element node that will be checked against 
	  the available options specific to this Sampler.
      @ In, paramInput, InputData.ParameterInput, the parsed parameters
      @ Out, None
    """
    #TODO remove using xmlNode�������������ں��涼�С�һ�����ڼ�DET�ļ�飬һ�����ڻ��DET�ļ�顣
    self._localInputAndChecksDET(xmlNode, paramInput)
    self._localInputAndChecksHybrid(xmlNode, paramInput)

  def _localInputAndChecksDET(self,xmlNode, paramInput):
    """
      Class specific inputs will be read here and checked for validity.
	  ��ȡ����������룬���Ҽ����Ч�ԡ�
      This method reads the standard DET portion only (no hybrid)
	  �����������DET
      @ In, xmlNode, xml.etree.ElementTree.Element, The xml element node that will be
	  checked against the available options specific to this Sampler.
	  ����ΪXML�Ľڵ㣬�Լ�XML�Ľڵ���Ϣ��
      @ In, paramInput, InputData.ParameterInput, the parsed parameters
	  ����Ϊ�������롢����������Լ�������
      @ Out, None
    """
    Grid.localInputAndChecks(self,xmlNode, paramInput)
	#������һ����������ļ�鷽������ΪDET��������һ���������������ʲô��ͬ�أ�
    if 'printEndXmlSummary'  in xmlNode.attrib.keys():
      self.printEndXmlSummary  = xmlNode.attrib['printEndXmlSummary'].lower()  in utils.stringsThatMeanTrue()
	  #utils.stringsThatMeanTrue��utilsģ���е�һ����������֪��ʲô���塣

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
	#self.axisName�ڳ�����û�е��á����������ģ�
	#�ش����������grid�����ж����һ���б�ı������������¡�������ÿһ��������ƣ�Ҳ���ǳ����������ƣ�
	#self.axisName             = []           # the name of each axis (variable) X��Ĳ�������
      branchedLevel[keyk] = 0 
	  #��֧ˮƽ��һ�����������ڵ�ǰ�ڵ��¾����һ���ӽڵ������
	  #��
      #branchedLevel[self.toBeSampled[keyk]] = 0
      self.standardDETvariables.append(keyk)
	  #append�����б������һ��Ԫ�ء��ڱ�׼��DET����������һ��keyk��һ������ֵ��Ҳ����������һ������������
	  #������ֵ����axisName�еġ�
      if self.gridInfo[keyk] == 'CDF':
	  #����һ���ֲ�������б������ѡ��һ���������֣�CDF��value
        self.branchProbabilities[keyk] = gridInfo[keyk][2]
		#gridInfo��һ���ֵ䡣{'name of the variable':Type}
		#��ѧϰ����˵��һ���ֵ䣬������[]�������Ԫ�ء����ԣ����������Ƿ�֧������һ���ֵ䡣
		#����֧�����ֵ�ļ��ǳ���������ֵ�����
		#gridInfo[keyk][2]�����DET���û��������ɢ�ľ�����ֵ����һ���б�ķ�ʽ���֡�
		#
        self.branchProbabilities[keyk].sort(key=float)
		#sort����һ�����������п����û��������ʱ�򣬲����ǰ���˳�����ɢ�������롣�����п��������ֲ��㡣
        if max(self.branchProbabilities[keyk]) > 1:
		#branchProbabilities[keyk]��һ���б�������DET��ɢ����ֵ�������Ǹ��ʻ��ǲ���ֵ��
          errorMsgs += "One of the Thresholds for distribution " + str(gridInfo[keyk][2]) + " is > 1 \n"
		  #�Ѿ�ȷ�����ⲿ�ֵ�������ܡ�
          errorFound = True
        probMultiplicities = Counter(self.branchProbabilities[keyk])
		#�ظ��Լ�顣����б����ظ���Ԫ�ء�����ظ�Ԫ�ػ���һ���б����ʽ��
        multiples = [prob for prob,mult in probMultiplicities.items() if mult > 1]
        ## Only the multiple variables remain
        for prob in multiples:
          errorMsgs += "In variable " + str(keyk) + " the Threshold " + str(prob)+" appears multiple times!!\n"
		  #ͨ������ָ����keyk��һ���ֲ�+�ֲ����ơ�In variable <distribution>zeroToOne the Threshold 0.2 appears multiple times!!
		  #��Ҫ�������Ǽ���������ǣ��Ƿ����ظ��Ĳ��֡�
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
        self.branchValues[keyk] = gridInfo[keyk][2]  ������ǻ�����ֵ�ķ�֧������
        self.branchValues[keyk].sort(key=float)
        valueMultiplicities = Counter(self.branchValues[keyk])
		#Counter�����ĺ����ǲ����Ƿ��ظ���
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
	#���ڼ��ģ���еķֲ��Ƿ���ǰ��ĳ���һ�¡�
      associatedDists = self.toBeSampled.values()
      if len(list(set(associatedDists))) != len(associatedDists):
        errorMsgs += "Distribution-mode sampling activated in " + self.name+". In this case every <distribution> needs to be assocaited
		with one single <Distribution> block!\n"
        errorFound = True
    if errorFound:
      self.raiseAnError(IOError,"In sampler named " + self.name+' the following errors have been found: \n'+errorMsgs )
	  #self.name������ָ���������ơ�
    # Append the branchedLevel dictionary in the proper list
    self.branchedLevel.append(branchedLevel)

  def _localInputAndChecksHybrid(self,xmlNode, paramInput): ��������Ի��DET�Ĳ��֡�
    """
      Class specific inputs will be read here and checked for validity.
      This method reads the hybrid det portion only
      @ In, xmlNode, xml.etree.ElementTree.Element, The xml element node that will be checked against the available options specific to this Sampler.
      @ In, paramInput, InputData.ParameterInput, the parsed parameters
      @ Out, None
    """
    for child in xmlNode:
	#����ж�xml�ļ��е��ӽڵ�ġ�ѭ��ÿһ��xmlNode���ӽڵ㡣
      if child.tag == 'HybridSampler':
	  #ר�����ڻ�ϳ�����⡣���ó�����־λʶ��
        if not 'type' in child.attrib.keys():
		#��Ϊ�������ļ��У����ʹ�û�ϳ�������ôtype�������Ǳ������ú�ѡ��ġ����򱨴�
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
        childCopy = copy.deepcopy(child)#����ǰ�xml�ļ����ӽڵ㶼��ȸ�ֵ��childCopy��
        childCopy.tag = child.attrib['type']
        childCopy.attrib.pop('type')#ΪʲôҪ�Ƴ�type��
		#pop���Ƴ��б��е�һ��Ԫ�档
        self.hybridStrategyToApply[child.attrib['type']]._readMoreXML(childCopy)
        # store the variables that represent the epistemic space
        self.epistemicVariables.update(dict.fromkeys(self.hybridStrategyToApply[child.attrib['type']].toBeSampled.keys(),{}))

  def localGetInitParams(self):
  #û�к������ú�ʹ�á��ѵ�����������ʹ�ã�
    """
      Appends a given dictionary with class specific member variables and their
      associated initialized values.
      @ In, None
      @ Out, paramDict, dict, dictionary containing the parameter names as keys
        and each parameter's initial value as the dictionary values
		����һ���ֵ���ʽ�����ݣ��ؼ����ǲ������ƣ��ټ��ϳ�ʼ��ֵ��
    """
    paramDict = {}  �����ǲ����ֵ䡣��ʼ��һ���ա�
    for key in self.branchProbabilities.keys(): ����Ƿ�֧����
      paramDict['Probability Thresholds for var ' + str(key) + ' are: '] = [str(x) for x in self.branchProbabilities[key]]
    for key in self.branchValues.keys()       :  ����Ƿ�֧��ֵ
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

  def localInitialize(self):�����Ǹ������ľֲ���ʼ��������
  #�������û���κ�һ���������ã�������У���ʲô���壿
    """
      Will perform all initialization specific to this Sampler. ִ����������������г�ʼ�����̡�
	  For instance,
      creating an empty container to hold the identified surface points, error
      checking the optionally provided solution export and other preset values,
      and initializing the limit surface Post-Processor used by this sampler.
	  ����һ������ʶ��ļ�������ļ����ṹ��
	  �������������ʼ��һ��������ĺ�������
      @ In, None
      @ Out, None
    """
    if len(self.hybridStrategyToApply.keys()) > 0:
	#�ж��Ƿ��л�ϳ�����ѡ�
      hybridlistoflist = []  
    for cnt, preckey  in enumerate(self.hybridStrategyToApply.keys()):
	#�������ݶԵ�ѭ��������һ��ѭ����Ҳ����cnt������������preckey�ǳ����������͡�
	#enumerate�ĺ����ǽ���ϳ������Ե���������һ�����ݶԣ���ѭ������1 һ�ַ����� ��2 һ�ַ�����
      hybridsampler =  self.hybridStrategyToApply[preckey]
	  #ȡ����ϳ�������
      hybridlistoflist.append([])
      hybridsampler.initialize()#��ϳ�������ʼ��
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
	  #��ʼ������ʱ��Ϊ��ʼʱ�䣬��ÿ�η�֧������仯��
      elm.add('endTime', str(0.0))
      elm.add('runEnded',False)
      elm.add('running',True)
      elm.add('queue',False)
	  #���add�ķ������������ԣ��������������Եĺ��塣
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
