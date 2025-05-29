# Function: Auto generate Frida hook js code for Android class and functions from config or (jadx/JEB decompiled) java source file
# Author: Crifan Li
# Update: 20250529
# Link: https://github.com/crifan/AutoGenFridaHookAndroidCode/blob/main/AutoGenFridaHookAndroidCode.py

import json
import codecs
import string
import os
import re
from datetime import datetime

################################################################################
# Config
################################################################################

# displayFuncNameWithParas = True
displayFuncNameWithParas = False

inputJsonFile = "input/settings.json"

outputFilename = "fridaHookAndroid"

################################################################################
# Const
################################################################################

mainDelimeterNum = 40
mainDelimeterChar = "="
mainDelimeterStr = mainDelimeterChar*mainDelimeterNum

subDelimeterNum = 30
subDelimeterChar = "-"
subDelimeterStr = subDelimeterChar*subDelimeterNum

# hookClassTemplate = string.Template("""var clsName_$classNameVar = "$classPackage.$className"
hookClassTemplate = string.Template("""var clsName_$classNameVar = "$clsPkgName"
    FridaAndroidUtil.printClassAllMethodsFields(clsName_$classNameVar)

    var cls_$classNameVar = Java.use(clsName_$classNameVar)
    console.log("cls_$classNameVar=" + cls_$classNameVar)""")

funcCallTemplate = string.Template("this.$toCallFuncName($parasStr)")

retPartTemplate_void = string.Template("""return $funcCallCode""")
retPartTemplate_nonVoid = string.Template("""var $retValName = $funcCallCode
        console.log(funcName + " => $retValName=" + $retValName)
        return $retValName""")
retPartTemplate_ctor = string.Template("""$funcCallCode
        var $retValName = this
        console.log(funcName + " => $retValName=" + $retValName)
        return""")

hookCurFuncTemplate = string.Template("""
    $funcDefSrcHookCode
    // $funcDefFrida
    var $hookFuncName = cls_$classNameVar.$toFindFuncName
    console.log("$hookFuncName=" + $hookFuncName)
    if ($hookFuncName) {
      $hookFuncName.implementation = function ($parasStr) {
        var funcName = "$displayFuncName"
        var funcParaDict = {$paraDictStr}
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        $retPartCode
      }
    }""")

hookClassFuncTemplate = string.Template("""
  static $classNameVar() {
    $hookClassStr

    $hookAllFuncStr
  }
""")

allClassHookTemplate = string.Template("""
class HookAppJava {
$allClassHookCode
}""")


# public PersistedInstallationEntry withRegisteredFid(String str, String str2, long j, String str3, long j2) {
# private PersistedInstallationEntry getPrefsWithGeneratedIdMultiProcessSafe() {
# private void insertOrUpdatePrefs(PersistedInstallationEntry persistedInstallationEntry) {
# private String getSubtype() {
# FirebaseInstallations(FirebaseApp firebaseApp, Provider provider, Provider provider2) {
# public final void lambda$getToken$1(final boolean isClearAuthToken) {
# boolean tokenNeedsRefresh(Store.Token token) {
# Store.Token getTokenWithoutTriggeringSync() {
# synchronized Task getOrStartGetTokenRequest(final String str, GetTokenRequest getTokenRequest) {
# abstract void    disconnect()
# static boolean    getFollowRedirects()
# "@Override public final void connect() throws IOException {",
# public void myMethod() throws ArithmeticException, NullPointerException
# @Override public final Map<String, List<String>> getHeaderFields() {
# public final Task<TResult> addOnSuccessListener(Activity activity, OnSuccessListener<? super TResult> onSuccessListener) {
# public final <X extends Throwable> TResult getResult(Class<X> cls) {
# public final <TContinuationResult> Task<TContinuationResult> continueWithTask(Executor executor, Continuation<TResult, Task<TContinuationResult>> continuation) {
# private final void zzf() {
# static final void zza(TaskCompletionSource taskCompletionSource) {

# overrideP = r"((?P<overrideStr>\@Override)\s+)?"
overrideP = r"((?P<overrideStr>\@Override)[ \t]+)?"

# protected final boolean s(String s, byte[] arr_b, String s1, String s2) {
funcModifierP = r"(?P<funcModifier>(((protected)|(public)|(private)|(static)|(final)|(synchronized)|(abstract))\s+)*)"

retTypeP = r"((?P<retType>[\w\.\[\]\<\>\, ]+)\s+)?"
funcNameP = r"(?P<funcName>[\w\$]+)"
typeParasP = r"(?P<typeParas>[^\)]+)?"
throwsP = r"(\s+throws\s+(?P<throwsStr>((,\s+)?\w+)+))?"

# tailP = r"( \{)?"
#     INITIATOR_CATEGORY_UNSPECIFIED(0),
tailP = r"( \{)?$"
# gFuncDefPattern = overrideP + funcModifierP + retTypeP + funcNameP + r"\(" + typeParasP + r"\)" + throwsP + tailP
gFuncDefPattern = r"(?P<functionDefine>" + overrideP + funcModifierP + retTypeP + funcNameP + r"\(" + typeParasP + r"\)" + throwsP + tailP + r")"


################################################################################
# Util Functions
################################################################################

def datetimeToStr(inputDatetime, format="%Y%m%d_%H%M%S"):
    """Convert datetime to string

    Args:
        inputDatetime (datetime): datetime value
    Returns:
        str
    Raises:
    Examples:
        datetime.datetime(2020, 4, 21, 15, 44, 13, 2000) -> '20200421_154413'
    """
    datetimeStr = inputDatetime.strftime(format=format)
    # print("inputDatetime=%s -> datetimeStr=%s" % (inputDatetime, datetimeStr)) # 2020-04-21 15:08:59.787623
    return datetimeStr

def getCurDatetimeStr(outputFormat="%Y%m%d_%H%M%S"):
    """
    get current datetime then format to string

    eg:
        20171111_220722

    :param outputFormat: datetime output format
    :return: current datetime formatted string
    """
    curDatetime = datetime.now() # 2017-11-11 22:07:22.705101
    # curDatetimeStr = curDatetime.strftime(format=outputFormat) #'20171111_220722'
    curDatetimeStr = datetimeToStr(curDatetime, format=outputFormat)
    return curDatetimeStr

def loadJsonFromFile(fullFilename, fileEncoding="utf-8"):
    """load and parse json dict from file"""
    with codecs.open(fullFilename, 'r', encoding=fileEncoding) as jsonFp:
        jsonDict = json.load(jsonFp)
        # logging.debug("Complete load json from %s", fullFilename)
        return jsonDict

def saveJsonToFile(fullFilename, jsonValue, indent=2, fileEncoding="utf-8"):
    """
        save json dict into file
        for non-ascii string, output encoded string, without \\u xxxx
    """
    with codecs.open(fullFilename, 'w', encoding=fileEncoding) as jsonFp:
        json.dump(jsonValue, jsonFp, indent=indent, ensure_ascii=False)
        # logging.debug("Complete save json %s", fullFilename)

def loadTextFromFile(fullFilename, fileEncoding="utf-8"):
    """load file text content from file"""
    with codecs.open(fullFilename, 'r', encoding=fileEncoding) as fp:
        allText = fp.read()
        # logging.debug("Complete load text from %s", fullFilename)
        return allText

def saveTextToFile(fullFilename, text, fileEncoding="utf-8"):
    """save text content into file"""
    with codecs.open(fullFilename, 'w', encoding=fileEncoding) as fp:
        fp.write(text)
        fp.close()

################################################################################
# Current Functions
################################################################################

def toVariableName(origName):
  varName = re.sub(r"\W", "_", origName)
  return varName

def genClassHookCode(classConfigDict, className, classNameVar, classPackage):
  global hookClassTemplate

  needGenClass = True
  if "needGenClass" in classConfigDict:
    needGenClass = classConfigDict["needGenClass"]
    print("needGenClass=%s" % needGenClass)

  if needGenClass:
    if classPackage:
      clsPkgName = "%s.%s" % (classPackage, className)
    else:
      clsPkgName = className
    hookClassStr = hookClassTemplate.safe_substitute(className=className, classNameVar=classNameVar, clsPkgName=clsPkgName)
  else:
    hookClassStr = ""
  print("hookClassStr=%s" % hookClassStr)
  return hookClassStr

def parseFunctionDefineSource(funcIdx, funcDefSrc):
  global gFuncDefPattern

  funcDefMatch = re.search(gFuncDefPattern, funcDefSrc)
  if funcDefMatch:
    overrideStr = funcDefMatch.group("overrideStr")
    print("overrideStr=%s" % overrideStr)
    funcModifier = funcDefMatch.group("funcModifier")
    print("funcModifier=%s" % funcModifier)
    retType = funcDefMatch.group("retType")
    print("retType=%s" % retType)
    if retType:
      retType = retType.strip()
      print("stripped retType=%s" % retType)
    funcName = funcDefMatch.group("funcName")
    print("funcName=%s" % funcName)
    typeParas = funcDefMatch.group("typeParas")
    print("typeParas=%s" % typeParas)
    throwsStr = funcDefMatch.group("throwsStr")
    print("throwsStr=%s" % throwsStr)
  else:
    raise Exception("Not support format for function define source: %s" % funcDefSrc)

  defineSourceDict = {
    "overrideStr": overrideStr,
    "funcModifier": funcModifier,
    "retType": retType,
    "funcName": funcName,
    "throwsStr": throwsStr,
  }
  print("part defineSourceDict=%s" % defineSourceDict)

  print("%s [%s] %s %s" % (subDelimeterStr, funcIdx, funcName, subDelimeterStr))
  print("funcDefSrc=%s" % funcDefSrc)

  typeParaDictList = []
  if typeParas:
    # String str, String str2, long j, String str3, long j2
    # final boolean isClearAuthToken
    # final String str, GetTokenRequest getTokenRequest
    # Store.Token token
    # typeParasPattern = r"((?P<paraModifier>(final)|(private)) )?(?P<paraType>[\w\$]+) (?P<paraName>\w+)(, )?"
    # typeParasPattern = r"((?P<paraModifier>(final)|(private)) )?(?P<paraType>[\w\$\[\]]+) (?P<paraName>\w+)(, )?"    

    # Activity activity, OnCompleteListener<TResult> onCompleteListener
    # typeParasPattern = r"((?P<paraModifier>(final)|(private)) )?(?P<paraType>[\w\$\[\]\<\>]+) (?P<paraName>\w+)(, )?"

    # Activity activity, OnSuccessListener<? super TResult> onSuccessListener
    # typeParasPattern = r"((?P<paraModifier>(final)|(private)) )?(?P<paraType>[\w\$\[\]\<\> \?]+) (?P<paraName>\w+)(, )?"

    # Continuation<TResult, TContinuationResult> continuation
    # typeParasPattern = r"((?P<paraModifier>(final)|(private)) )?(?P<paraType>\w+((\[\])|(\<[^\>]+\>))?) (?P<paraName>\w+)(, )?"

    # Executor executor, Continuation<TResult, Task<TContinuationResult>> continuation
    # typeParasPattern = r"((?P<paraModifier>(final)|(private)) )?(?P<paraType>\w+((\[\])|(\<[^\<]+(\<[^\>]+\>)?\>))?) (?P<paraName>\w+)(, )?"

    # String s, UrlRequest.Callback urlRequest$Callback0, Executor executor0
    # typeParasPattern = r"((?P<paraModifier>(final)|(private)) )?(?P<paraType>\w+((\[\])|(\<[^\<]+(\<[^\>]+\>)?\>))?) (?P<paraName>[\w\$]+)(, )?"

    """
            CronetUrlRequestContext requestContext,
            String url,
            int priority,
            UrlRequest.Callback callback,
            Executor executor,
            Collection<Object> requestAnnotations,
            boolean disableCache,
            boolean disableConnectionMigration,
            boolean allowDirectExecutor,
            boolean trafficStatsTagSet,
            int trafficStatsTag,
            boolean trafficStatsUidSet,
            int trafficStatsUid,
            RequestFinishedInfo.Listener requestFinishedListener,
            int idempotency,
            long networkHandle,
            String method,
            ArrayList<Map.Entry<String, String>> requestHeaders,
            UploadDataProvider uploadDataProvider,
            Executor uploadDataProviderExecutor,
            byte[] dictionarySha256Hash,
            ByteBuffer dictionary,
            @NonNull String dictionaryId
    """
    # typeParasPattern = r"((?P<paraModifier>(final)|(private)|(@[\w\.]+)) )?(?P<paraType>\w+((\[\])|(\<[^\>]+(\<[^\>]+\>)?\>))?) (?P<paraName>[\w\$]+)(, )?"

    # final VersionSafeCallbacks.UrlRequestStatusListener listener, final int loadState
    # typeParasPattern = r"((?P<paraModifier>(final)|(private)|(@[\w\.]+)) )?(?P<paraType>[\w\.]+((\[\])|(\<[^\>]+(\<[^\>]+\>)?\>))?) (?P<paraName>[\w\$]+)(, )?"
    paraModifierP = r"((?P<paraModifier>(final)|(private)|(@[\w\.]+)) )?"

    # paraTypeP = r"(?P<paraType>[\w\.]+((\[\])|(\<[^\>]+(\<[^\>]+\>)?\>))?)"
    # public fjgj(byte[] arr_b, byte[][] arr2_b) {
    paraTypeP = r"(?P<paraType>[\w\.]+((\[\])+|(\<[^\>]+(\<[^\>]+\>)?\>))?)"

    paraName = r"(?P<paraName>[\w\$]+)"
    separatorP = r"(, )?"
    typeParasPattern = paraModifierP + paraTypeP + " " + paraName + separatorP

    typeParasMatchIter = re.finditer(typeParasPattern, typeParas)
    typeParasMatchList = list(typeParasMatchIter)
    if typeParasMatchList:
      for eachTypeParaMatch in typeParasMatchList:
        paraModifier = eachTypeParaMatch.group("paraModifier")
        print("paraModifier=%s" % paraModifier)
        paraType = eachTypeParaMatch.group("paraType")
        print("paraType=%s" % paraType)
        paraName = eachTypeParaMatch.group("paraName")
        print("paraName=%s" % paraName)
        paraName = toVariableName(paraName)
        print("paraName=%s" % paraName)
        curTypeParaDict = {
          "paraModifier": paraModifier,
          "paraType": paraType,
          "paraName": paraName,
        }
        typeParaDictList.append(curTypeParaDict)
    else:
      raise Exception("Unsupport format for type para strings: %s" % typeParas)
  # else:
  #   raise Exception("Not support format for type para strings: %s" % typeParas)
  print("typeParaDictList=%s" % typeParaDictList)

  # defineSourceDict = {
  #   "overrideStr": overrideStr,
  #   "funcModifier": funcModifier,
  #   "retType": retType,
  #   "funcName": funcName,
  #   "throwsStr": throwsStr,
  #   "typeParaDictList": typeParaDictList,
  # }
  defineSourceDict["typeParaDictList"] = typeParaDictList
  print("funcDefSrc=%s -> defineSourceDict=%s" % (funcDefSrc, defineSourceDict))

  return defineSourceDict

def genRetValueName(isCtor, className, retType, funcNameVar, isFuncOverload, overloadFuncNameSuffix):
  if isCtor:
    retType = className
    retPref = "new"
  else:
    retPref = "ret"
  print("retPref=%s" % retPref)

  getXxxMatch = re.search(r"^get(?P<getValue>[A-Z]\w+)$", funcNameVar)
  print("getXxxMatch=%s" % getXxxMatch)
  if getXxxMatch:
    getValue = getXxxMatch.group("getValue")
    print("getValue=%s" % getValue)
    retValName = "%s%s" % (retPref, getValue)
    print("retValName=%s" % retValName)
  else:
    retTypeVar = toVariableName(retType)
    print("retTypeVar=%s" % retTypeVar)

    # for debug
    if retType != retTypeVar:
      print("retType=%s -> retTypeVar=%s" % (retType, retTypeVar))
      # retType=<TContinuationResult> Task<TContinuationResult> -> retTypeVar=_TContinuationResult__Task_TContinuationResult_

    retTypeFirstChar = retTypeVar[0]
    retTypeFirstCharUpper = retTypeFirstChar.upper()
    retTypeRest = retTypeVar[1:]
    firstCharUpperedRetType = retTypeFirstCharUpper + retTypeRest

    retValName = "%s%s" % (retPref, firstCharUpperedRetType)
    # retboolean -> retBoolean

  if isFuncOverload:
    retValName = "%s_%s" % (retValName, overloadFuncNameSuffix)

  print("isCtor=%s, className=%s, retType=%s, funcNameVar=%s -> retValName=%s" % (isCtor, className, retType, funcNameVar, retValName))
  return retValName

def genToFindFuncionName(toCallFuncName, isFuncOverload, funcDefFrida):
  if isFuncOverload:
    overloadParas = ""

    # // public static int getInt(ContentResolver cr, String name)
    # // public static int android.provider.Settings$Secure.getInt(android.content.ContentResolver,java.lang.String) throws android.provider.Settings$SettingNotFoundException
    # // static int	getInt(ContentResolver cr, String name, int def)
    # // public static int android.provider.Settings$Secure.getInt(android.content.ContentResolver,java.lang.String,int)

    # public void java.net.HttpURLConnection.setFixedLengthStreamingMode(int)
    # public void java.net.HttpURLConnection.setFixedLengthStreamingMode(long)

    if funcDefFrida:
      paraTypesStrPattern = r"\((?P<paraTypesStr>[\w\.,]+)?\)"
      print("paraTypesStrPattern=%s" % paraTypesStrPattern)

      paraTypesStrMatch = re.search(paraTypesStrPattern, funcDefFrida)
      print("paraTypesStrMatch=%s" % paraTypesStrMatch)

      if paraTypesStrMatch:
        paraTypesStr = paraTypesStrMatch.group("paraTypesStr")
        print("paraTypesStr=%s" % paraTypesStr)
        if paraTypesStr:
          paraTypeListStrPattern = r"(?P<paraType>[\w\.]+),?"
          print("paraTypeListStrPattern=%s" % paraTypeListStrPattern)
          paraTypeListStrIter = re.finditer(paraTypeListStrPattern, paraTypesStr)
          print("paraTypeListStrIter=%s" % paraTypeListStrIter)
          paraTypeListStrMatchList = list(paraTypeListStrIter)
          print("paraTypeListStrMatchList=%s" % paraTypeListStrMatchList)
          if paraTypeListStrMatchList:
            paraTypeList = []
            for earchParaTypeMatch in paraTypeListStrMatchList:
              earchParaType = earchParaTypeMatch.group("paraType")
              print("earchParaType=%s" % earchParaType)
              paraTypeList.append(earchParaType)
            
            overloadParaTypeStrList = []
            for earchParaType in paraTypeList:
              overloadParaTypeStr = '"%s"' % earchParaType
              print("overloadParaTypeStr=%s" % overloadParaTypeStr)
              overloadParaTypeStrList.append(overloadParaTypeStr)
            
            overloadParas = ", ".join(overloadParaTypeStrList)
    else:
      print("Warning: no frida hook function definition -> can NOT generate overload function name for find !")

    toFindFuncName = "%s.overload(%s)" % (toCallFuncName, overloadParas)
  else:
    toFindFuncName = toCallFuncName

  print("toCallFuncName=%s, isFuncOverload=%s, funcDefFrida=%s -> toFindFuncName=%s" % (toCallFuncName, isFuncOverload, funcDefFrida, toFindFuncName))
  return toFindFuncName

def genDisplayFunctionName(isCtor, className, funcName, isFuncOverload, overloadFuncNameSuffix, displayFuncNameWithParas, parasStr):
  if isCtor:
    displayFuncName = "%s" % className
  else:
    displayFuncName = "%s.%s" % (className, funcName)

  if isFuncOverload:
    displayFuncName = "%s_%s" % (displayFuncName, overloadFuncNameSuffix)

  if displayFuncNameWithParas:
    displayFuncName = "%s(%s)" % (displayFuncName, parasStr)
  print("displayFuncName=%s" % displayFuncName)
  return displayFuncName

def genReturnPartCode(retType, funcCallCode, isCtor, className, funcNameVar, isFuncOverload, overloadFuncNameSuffix, displayFuncName):
  global retPartTemplate_void, retPartTemplate_nonVoid, retPartTemplate_ctor
  if retType == "void":
    retPartCode = retPartTemplate_void.safe_substitute(funcCallCode=funcCallCode)
  else:
    retValName = genRetValueName(isCtor, className, retType, funcNameVar, isFuncOverload, overloadFuncNameSuffix)
    if isCtor:
      # ctor() function no return value, but self is the return value
      retPartCode = retPartTemplate_ctor.safe_substitute(funcCallCode=funcCallCode, retValName=retValName)
    else:
      retPartCode = retPartTemplate_nonVoid.safe_substitute(retValName=retValName, funcCallCode=funcCallCode)
  print("retPartCode=%s" % retPartCode)
  return retPartCode

def genHookCodeForSingleClass(curIdx, toHookClassDict):
  classConfigDict = toHookClassDict["class"]
  print("classConfigDict=%s" % classConfigDict)
  functionsConfigDictList = toHookClassDict["functions"]
  print("functionsConfigDictList=%s" % functionsConfigDictList)

  className = classConfigDict["name"]
  print("className=%s" % className)
  classPackage = classConfigDict["package"]
  print("classPackage=%s" % classPackage)

  print("%s [%s] %s %s" % (mainDelimeterStr, curIdx, className, mainDelimeterStr))

  classNameVar = toVariableName(className)
  print("classNameVar=%s" % classNameVar)

  hookClassStr = genClassHookCode(classConfigDict, className, classNameVar, classPackage)

  hookAllFuncCodeList = []

  for funcIdx, toHookFuncDict in enumerate(functionsConfigDictList):
    overloadFuncNameSuffix = ""

    funcDefSrc = toHookFuncDict["defineSource"]
    print("funcDefSrc=%s" % funcDefSrc)
    funcDefFrida = toHookFuncDict["defineFrida"]
    print("funcDefFrida=%s" % funcDefFrida)
    isFuncOverload = False
    if "isOverload" in toHookFuncDict:
      isFuncOverload = toHookFuncDict["isOverload"]
    print("isFuncOverload=%s" % isFuncOverload)

    defineSourceDict = parseFunctionDefineSource(funcIdx, funcDefSrc)
    print("defineSourceDict=%s" % defineSourceDict)
    retType = defineSourceDict["retType"]
    funcName = defineSourceDict["funcName"]
    typeParaDictList = defineSourceDict["typeParaDictList"]

    paraNameList = []
    paraLineStrList = []
    for curTypeParaDict in typeParaDictList:
      curParaName = curTypeParaDict["paraName"]
      paraNameList.append(curParaName)

      paraLineStr = '"%s": %s,' % (curParaName, curParaName)
      paraLineStrList.append(paraLineStr)
    print("paraNameList=%s" % paraNameList)
    print("paraLineStrList=%s" % paraLineStrList)

    parasStr = ", ".join(paraNameList)
    print("parasStr=%s" % parasStr)

    # paraDictPrefStr = "\n"
    paraDictSufixfStr = "\n        "
    paraDictPrefStr = paraDictSufixfStr + "  "
    if paraLineStrList:
      paraDictStr = paraDictPrefStr.join(paraLineStrList)
      paraDictStr = paraDictPrefStr + paraDictStr + paraDictSufixfStr
    else:
      paraDictStr = ""
    print("paraDictStr=%s" % paraDictStr)

    if isFuncOverload:
      funcParaNum = len(paraNameList)
      print("funcParaNum=%s" % funcParaNum)
      paraNameFirstChars = ""
      for eachParaName in paraNameList:
        curParaNameFirstChar = eachParaName[0]
        paraNameFirstChars += curParaNameFirstChar
      print("paraNameFirstChars=%s" % paraNameFirstChars)
      overloadFuncNameSuffix = "%sp%s" % (funcParaNum, paraNameFirstChars)
      print("overloadFuncNameSuffix=%s" % overloadFuncNameSuffix)

    isCtor = funcName == className
    print("isCtor=%s" % isCtor)

    toCallFuncName = funcName
    if isCtor:
      # do special check: is ctor -> $init
       toCallFuncName = "$init"
    print("toCallFuncName=%s" % toCallFuncName)

    funcCallCode = funcCallTemplate.safe_substitute(toCallFuncName=toCallFuncName, parasStr=parasStr)
    print("funcCallCode=%s" % funcCallCode)

    toFindFuncName = genToFindFuncionName(toCallFuncName, isFuncOverload, funcDefFrida)
    print("toFindFuncName=%s" % toFindFuncName)

    displayFuncName = genDisplayFunctionName(isCtor, className, funcName, isFuncOverload, overloadFuncNameSuffix, displayFuncNameWithParas, parasStr)
    print("displayFuncName=%s" % displayFuncName)

    funcNameVar = toVariableName(funcName)
    print("funcNameVar=%s" % funcNameVar)

    # # for debug
    # if funcName != funcNameVar:
    #   print("funcName=%s -> funcNameVar=%s" % (funcName, funcNameVar))

    retPartCode = genReturnPartCode(retType, funcCallCode, isCtor, className, funcNameVar, isFuncOverload, overloadFuncNameSuffix, displayFuncName)
    print("retPartCode=%s" % retPartCode)

    if isCtor:
      # funcNameForHook = "init"
      funcNameForHook = "ctor"
    else:
      funcNameForHook = funcNameVar
    print("funcNameForHook=%s" % funcNameForHook)
    hookFuncName = "func_%s_%s" % (classNameVar, funcNameForHook)
    print("hookFuncName=%s" % hookFuncName)

    if isFuncOverload:
      hookFuncName = "%s_%s" % (hookFuncName, overloadFuncNameSuffix)
      print("hookFuncName=%s" % hookFuncName)

    isFuncDefSrcMultiLine = ("\r" in funcDefSrc) or ("\n" in funcDefSrc)
    print("isFuncDefSrcMultiLine=%s" % isFuncDefSrcMultiLine)
    if isFuncDefSrcMultiLine:
      indentStr = "    "
      funcDefSrcHookCode = "/* %s%s%s*/" % (funcDefSrc, os.linesep, indentStr)
    else:
      funcDefSrcHookCode = "// %s" % funcDefSrc
    print("funcDefSrcHookCode=%s" % funcDefSrcHookCode)

    hookCurFuncCode = hookCurFuncTemplate.safe_substitute(
      funcDefSrcHookCode=funcDefSrcHookCode,
      funcDefFrida=funcDefFrida,
      hookFuncName=hookFuncName,
      classNameVar=classNameVar,
      funcNameVar=funcNameVar, 
      toFindFuncName=toFindFuncName,
      parasStr=parasStr,
      displayFuncName=displayFuncName,
      paraDictStr=paraDictStr,
      retPartCode=retPartCode,
    )
    print("hookCurFuncCode=%s" % hookCurFuncCode)

    hookAllFuncCodeList.append(hookCurFuncCode)
    print("hookAllFuncCodeList=%s" % hookAllFuncCodeList)

  hookAllFuncStr = "\n".join(hookAllFuncCodeList)
  print("hookAllFuncStr=%s" % hookAllFuncStr)

  classFuncStr = hookClassFuncTemplate.safe_substitute(classNameVar=classNameVar, hookClassStr=hookClassStr, hookAllFuncStr=hookAllFuncStr)
  print("classFuncStr=%s" % classFuncStr)

  return classFuncStr

def parseClassPackage(javaSrcStr):
    # package com.google.android.gms.auth.account.be.legacy;
    classPackagePattern = r"^package\s+(?P<classPackage>[\w\.]+);"
    # classPackageMatch = re.search(classPackagePattern, javaSrcStr)
    classPackageMatch = re.search(classPackagePattern, javaSrcStr, re.MULTILINE)
    classPackage = ""
    if classPackageMatch:
      classPackage = classPackageMatch.group("classPackage")

      # Note: special, for 'jadx/sources/defpackage/ccul.java' is 'package defpackage;' is 'defpackage', actually is None = no package
      if classPackage == "defpackage":
        classPackage = ""
    print("classPackage=%s" % classPackage)
    return classPackage

def parseClassName(javaSrcStr):
    # public class AuthCronChimeraService extends GmsTaskChimeraService {
    # public final class xgd {
    # public final class ftzv implements ftzu {
    # public class TokenResponse extends AbstractSafeParcelable implements ReflectedParcelable {
    classModifierP = r"(?P<classModifier>(((public)|(private)|(static)|(final)|(synchronized)|(abstract))\s+)*)"

    # public enum arok implements fjgu {
    classOrEnumP = r"(((class)|(enum))\s+)"

    classNameP = r"(?P<className>[\w\$\.]+)"
    classSuffixP = r"(?P<classSuffix>\s+((extends)|(implements))\s+[^\{]+)?"
    classNamePatter = classModifierP + classOrEnumP + classNameP + classSuffixP + r"\s+\{"

    # TODO: for class name contain '.', convert to '$'
    # eg: xxx.yyy -> xxx$yyy

    classNameMatch = re.search(classNamePatter, javaSrcStr)

    classNameWholeStr = None
    classModifier = None
    className = None
    classSuffix = None

    if classNameMatch:
      classNameWholeStr = classNameMatch.group(0)
      print("classNameWholeStr=%s" % classNameWholeStr)
      classModifier = classNameMatch.group("classModifier")
      print("classModifier=%s" % classModifier)
      className = classNameMatch.group("className")
      print("className=%s" % className)
      classSuffix = classNameMatch.group("classSuffix")
      print("classSuffix=%s" % classSuffix)
    else:
      raise Exception("Unsupported format of class name for:\n%s" % javaSrcStr)

    # afl..ExternalSyntheticApiModelOutline6 -> afl$$ExternalSyntheticApiModelOutline6
    className = className.replace(".", "$")
    print("className=%s" % className)

    classNameDict = {
      "classNameWholeStr": classNameWholeStr,
      "classModifier": classModifier,
      "className": className,
      "classSuffix": classSuffix,
    }
    print("classNameDict=%s" % classNameDict)
    return classNameDict

def parseFunctionsList(javaSrcStr):
  global gFuncDefPattern

  functionsDictList = []

  #     public final int a(bxmk bxmk0) {
  #     static void d(ehsd ehsd0, ehse ehse0, String s) {
  #     public static final void e(Context context0) {
  #     public static final void f(long v, int v1) {
  #     public final void fO() {
  #     public final long A() {

  functionIndentP = r"^    "

  functionBodyP = r".+?"
  functionEndP = functionIndentP + r"\}$"

  # functionPrefixP = r"(?P<functionPrefix>([\w\.]+\s+)+)"
  # funcNameP = r"(?P<funcName>[\w\$\.]+)"
  # # functionParasP = r"(?P<functionParas>\([^\)]+\))"
  # functionParasP = r"(?P<functionParas>\([^\)]*\))"
  # functionSuffixP = r"\s+\{"
  # functionDefineP = r"(?P<functionDefine>" + functionPrefixP + funcNameP + functionParasP + functionSuffixP + r")"
  # functionPattern = functionIndentP + functionDefineP + functionBodyP + functionEndP

  functionPattern = functionIndentP + gFuncDefPattern + functionBodyP + functionEndP

  functionIter = re.finditer(functionPattern, javaSrcStr, re.MULTILINE | re.DOTALL)
  print("functionIter=%s" % functionIter)
  functionMatchList = list(functionIter)
  print("functionMatchList=%s, count=%d" % (functionMatchList, len(functionMatchList)))

  funcNameSet = set()
  overloadFuncNameSet = set()

  origFunctionsDictList = []
  for funcIdx, functionMatch in enumerate(functionMatchList):
    funcName = functionMatch.group("funcName")
    # typeParas = functionMatch.group("typeParas")
    # retType = functionMatch.group("retType")
    # print("funcName=%s" % funcName)
    print("[%d] %s" % (funcIdx, funcName))
    # functionStr = functionMatch.group(0)
    # print("functionStr=%s" % functionStr)
    functionDefine = functionMatch.group("functionDefine")
    print("functionDefine=%s" % functionDefine)
    hasMoreIndent = functionDefine.startswith(" ")
    print("hasMoreIndent=%s" % hasMoreIndent)
    # "    public void run() {" -> hasMoreIndent=True
    isSubClassFunc = hasMoreIndent
    print("isSubClassFunc=%s" % isSubClassFunc)
    if isSubClassFunc:
      print("WARN: omit sub/inner class function: %s" % functionDefine)
      continue

    curFunctionDict = {
      "funcName": funcName,
      # "typeParas": typeParas,
      # "retType": retType,
      "defineSource": functionDefine,
      "defineFrida": "",
    }

    # add support auto add '"isOverload": true' for same function name
    if funcName in funcNameSet:
      overloadFuncNameSet.add(funcName)
    else:
      funcNameSet.add(funcName)

    print("curFunctionDict=%s" % curFunctionDict)
    origFunctionsDictList.append(curFunctionDict)
  
  # generated for "isOverload"
  overloadFunctionsDictList = []
  for curOrigFunctionDict in origFunctionsDictList:
    funcName = curOrigFunctionDict["funcName"]
    functionDefine = curOrigFunctionDict["defineSource"]
    defineFrida = curOrigFunctionDict["defineFrida"]

    curOverloadFunctionsDict = {
      # "funcName": funcName,
      "defineSource": functionDefine,
      "defineFrida": defineFrida,
    }
    if funcName in overloadFuncNameSet:
      curOverloadFunctionsDict["isOverload"] = True

    overloadFunctionsDictList.append(curOverloadFunctionsDict)

  functionsDictList = overloadFunctionsDictList
  print("functionsDictList=%s" % functionsDictList)
  return functionsDictList

def genToHookClassConfig(hookFromFileList):
  toHookClassDictList = []

  for curIdx, curFilePath in enumerate(hookFromFileList):
    print("curFilePath=%s" % curFilePath)
    javaSrcStr = loadTextFromFile(curFilePath)
    print("javaSrcStr=%s" % javaSrcStr)

    classPackage = parseClassPackage(javaSrcStr)
    print("classPackage=%s" % classPackage)

    classNameDict = parseClassName(javaSrcStr)
    print("classNameDict=%s" % classNameDict)
    className = classNameDict["className"]
    print("className=%s" % className)

    classInfoDict = {
      "name": className,
      "package": classPackage
    }
    print("classInfoDict=%s" % classInfoDict)

    functionsDictList = parseFunctionsList(javaSrcStr)
    print("functionsDictList=%s" % functionsDictList)

    curClassConfig = {
      "class": classInfoDict,
      "functions": functionsDictList
    }

    print("[%s] file=%s -> class config: %s" % (curIdx, curFilePath, curClassConfig))

    toHookClassDictList.append(curClassConfig)

  print("toHookClassDictList=%s" % toHookClassDictList)
  return toHookClassDictList

################################################################################
# Main
################################################################################

print("outputFilename=%s" % outputFilename)
curDateTimeStr = getCurDatetimeStr()
print("curDateTimeStr=%s" % curDateTimeStr)
outputFileFullName = "%s_%s.js" % (outputFilename, curDateTimeStr)
print("outputFileFullName=%s" % outputFileFullName)
outputFileFullPath = os.path.join("output", outputFileFullName)
print("outputFileFullPath=%s" % outputFileFullPath)

print("inputJsonFile=%s" % inputJsonFile)
inputDict = loadJsonFromFile(inputJsonFile)
print("inputDict=%s" % inputDict)

configDict = inputDict["config"]
print("configDict=%s" % configDict)
toHookDict = inputDict["toHook"]
print("toHookDict=%s" % toHookDict)

hookFromFileList = toHookDict["fromFile"]
print("hookFromFileList=%s" % hookFromFileList)
hookFromConfigList = toHookDict["fromConfig"]
print("hookFromConfigList=%s" % hookFromConfigList)

if "displayFuncNameWithParas" in configDict:
  displayFuncNameWithParas = configDict["displayFuncNameWithParas"]
print("displayFuncNameWithParas=%s" % displayFuncNameWithParas)

if hookFromFileList:
  toHookDictList = genToHookClassConfig(hookFromFileList)

  # # for debug
  # dbgToHookDictFilename = "tmpToHookDict_%s.json" % curDateTimeStr
  # print("dbgToHookDictFilename=%s" % dbgToHookDictFilename)
  # dbgToHookDictFullPath = os.path.join("debugging", "tmpToHookDict", dbgToHookDictFilename)
  # print("dbgToHookDictFullPath=%s" % dbgToHookDictFullPath)
  # saveJsonToFile(dbgToHookDictFullPath, toHookDictList)
else:
  toHookDictList = hookFromConfigList
print("toHookDictList=%s" % toHookDictList)

allClassCodeList = []
for curIdx, toHookClassDict in enumerate(toHookDictList):
  classFuncStr = genHookCodeForSingleClass(curIdx, toHookClassDict)
  allClassCodeList.append(classFuncStr)

allClassHookCode = "\n".join(allClassCodeList)
print("allClassHookCode=%s" % allClassHookCode)

finalOutputCode = allClassHookTemplate.safe_substitute(allClassHookCode=allClassHookCode)
print("finalOutputCode=%s" % finalOutputCode)

saveTextToFile(outputFileFullPath, finalOutputCode)
print("Complete output result to: %s" % outputFileFullPath)
