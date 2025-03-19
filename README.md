# AutoGenFridaHookAndroidCode

* Update: `20250319`

## Repo

https://github.com/crifan/AutoGenFridaHookAndroidCode

https://github.com/crifan/AutoGenFridaHookAndroidCode.git

## Function

Auto generate Frida hook js code for Android class and functions from config or (jadx/JEB decompiled) java source file

## Usage

## 1. Prepare config

Support two config type:

* Load to hook from **file**
  * Demo/Example
    * copy content from `input/demo/config/settings_file.json` to `input/settings.json`
* Load to hook from **config**
  * Demo/Example
    * copy content from `input/demo/config/settings_config.json` (or with Frida define one: `input/demo/config/settings_config_withFridaDefine.json`) to `input/settings.json`

you can choose any one you want

### About: Load to hook from **file**

most common used one

you just need copy your jadx/JEB decompiled java source file full path into config

look like:

```json
{
  "config": {
    "displayFuncNameWithParas": false
  },
  "toHook": {
    "fromFile": [
      "/Users/crifan/dev/xxx/staticAnalysis/decompile/JEB/xxx_JEB/xbb.java"
    ],
    "fromConfig": []
  }
}
```

then all done !

### About: Load to hook from **config**

this type is useful when you no (jadx/JEB decompiled) java source file, such as Android build-in Classes

* eg:
  * you want hook Android build-in class `Message`, but no java source, then you can
    * goto official website: [Message](https://developer.android.com/reference/android/os/Message), copy functions definitions
      * ctors
        * `Message()`
      * methods
        * `void	copyFrom(Message o)`
        * `static Message	obtain()`
        * ...
    * then put these info into config files, look like this

```json
{
  "config": {
    "displayFuncNameWithParas": false
  },
  "toHook": {
    "fromFile": [],
    "fromConfig": [
      {
        "class": {
          "name": "Message",
          "package": "android.os"
        },
        "functions": [
          {
            "defineSource": "Message()",
            "defineFrida": ""
          },
          {
            "defineSource": "void	copyFrom(Message o)",
            "defineFrida": ""
          },
          {
            "defineSource": "static Message	obtain()",
            "defineFrida": ""
          }
        ]
      }
    ]
  }
}
```

then can use current script to generate hook code

## 2. Run script

run current script:

```bash
python AutoGenFridaHookAndroidCode.py
```

will generate Frida hook Android js code into:

`output/fridaHookAndroid_<DATE>_<TIME>.js`

---

## Appendix

### Generated hook code

#### Example

The generated `output/fridaHookAndroid_20250319_112814.js` file, content look like this:

```js

class HookAppJava {

  static Aoi() {
    var clsName_Aoi = "com.aSIIoEMUzSX.Aoi"
    FridaAndroidUtil.printClassAllMethodsFields(clsName_Aoi)

    var cls_Aoi = Java.use(clsName_Aoi)
    console.log("cls_Aoi=" + cls_Aoi)

    
    // public Aoi(AAk aAk) {
    // 
    var func_Aoi_Aoi = cls_Aoi.$init
    console.log("func_Aoi_Aoi=" + func_Aoi_Aoi)
    if (func_Aoi_Aoi) {
      func_Aoi_Aoi.implementation = function (aAk) {
        var funcName = "Aoi"
        var funcParaDict = {
          "aAk": aAk,
        }
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        var newAoi = this.$init(aAk)
        console.log("Aoi => newAoi=" + newAoi)
        return newAoi
      }
    }

    // public static IBinder b(String str) {
    // public static android.os.IBinder com.aSIIoEMUzSXAoi.b(java.lang.String)
    var func_Aoi_b_1ps = cls_Aoi.b.overload("java.lang.String")
    console.log("func_Aoi_b_1ps=" + func_Aoi_b_1ps)
    if (func_Aoi_b_1ps) {
      func_Aoi_b_1ps.implementation = function (str) {
        var funcName = "Aoi.b_1ps"
        var funcParaDict = {
          "str": str,
        }
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        var retIBinder_1ps = this.b(str)
        console.log("Aoi.b_1ps => retIBinder_1ps=" + retIBinder_1ps)
        return retIBinder_1ps
      }
    }

    // private static long getNativePtr(Parcel parcel) {
    // 
    var func_Aoi_getNativePtr = cls_Aoi.getNativePtr
    console.log("func_Aoi_getNativePtr=" + func_Aoi_getNativePtr)
    if (func_Aoi_getNativePtr) {
      func_Aoi_getNativePtr.implementation = function (parcel) {
        var funcName = "Aoi.getNativePtr"
        var funcParaDict = {
          "parcel": parcel,
        }
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        var retNativePtr = this.getNativePtr(parcel)
        console.log("Aoi.getNativePtr => retNativePtr=" + retNativePtr)
        return retNativePtr
      }
    }

    // public static void main(String[] strArr) {
    // 
    var func_Aoi_main = cls_Aoi.main
    console.log("func_Aoi_main=" + func_Aoi_main)
    if (func_Aoi_main) {
      func_Aoi_main.implementation = function (strArr) {
        var funcName = "Aoi.main"
        var funcParaDict = {
          "strArr": strArr,
        }
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        return this.main(strArr)
      }
    }

    // public final int a(String str, String str2) {
    // public final int a(java.lang.String,java.lang.String)
    var func_Aoi_a_2pss = cls_Aoi.a.overload("java.lang.String", "java.lang.String")
    console.log("func_Aoi_a_2pss=" + func_Aoi_a_2pss)
    if (func_Aoi_a_2pss) {
      func_Aoi_a_2pss.implementation = function (str, str2) {
        var funcName = "Aoi.a_2pss"
        var funcParaDict = {
          "str": str,
          "str2": str2,
        }
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        var retInt_2pss = this.a(str, str2)
        console.log("Aoi.a_2pss => retInt_2pss=" + retInt_2pss)
        return retInt_2pss
      }
    }

    // public final void a() {
    // public final void a()
    var func_Aoi_a_0p = cls_Aoi.a.overload()
    console.log("func_Aoi_a_0p=" + func_Aoi_a_0p)
    if (func_Aoi_a_0p) {
      func_Aoi_a_0p.implementation = function () {
        var funcName = "Aoi.a_0p"
        var funcParaDict = {}
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        return this.a()
      }
    }

    // public final void b() {
    // public final void b()
    var func_Aoi_b_0p = cls_Aoi.b.overload()
    console.log("func_Aoi_b_0p=" + func_Aoi_b_0p)
    if (func_Aoi_b_0p) {
      func_Aoi_b_0p.implementation = function () {
        var funcName = "Aoi.b_0p"
        var funcParaDict = {}
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        return this.b()
      }
    }

    // public boolean b(Intent intent) {
    // public boolean b(android.content.Intent)
    var func_Aoi_b_1pi = cls_Aoi.b.overload("android.content.Intent")
    console.log("func_Aoi_b_1pi=" + func_Aoi_b_1pi)
    if (func_Aoi_b_1pi) {
      func_Aoi_b_1pi.implementation = function (intent) {
        var funcName = "Aoi.b_1pi"
        var funcParaDict = {
          "intent": intent,
        }
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        var retBoolean_1pi = this.b(intent)
        console.log("Aoi.b_1pi => retBoolean_1pi=" + retBoolean_1pi)
        return retBoolean_1pi
      }
    }

    // public final void c() {
    // 
    var func_Aoi_c = cls_Aoi.c
    console.log("func_Aoi_c=" + func_Aoi_c)
    if (func_Aoi_c) {
      func_Aoi_c.implementation = function () {
        var funcName = "Aoi.c"
        var funcParaDict = {}
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        return this.c()
      }
    }

    // public final void d() {
    // 
    var func_Aoi_d = cls_Aoi.d
    console.log("func_Aoi_d=" + func_Aoi_d)
    if (func_Aoi_d) {
      func_Aoi_d.implementation = function () {
        var funcName = "Aoi.d"
        var funcParaDict = {}
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        return this.d()
      }
    }

    // public final void e() {
    // 
    var func_Aoi_e = cls_Aoi.e
    console.log("func_Aoi_e=" + func_Aoi_e)
    if (func_Aoi_e) {
      func_Aoi_e.implementation = function () {
        var funcName = "Aoi.e"
        var funcParaDict = {}
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        return this.e()
      }
    }

    // public final Parcel getPa(int i) {
    // 
    var func_Aoi_getPa = cls_Aoi.getPa
    console.log("func_Aoi_getPa=" + func_Aoi_getPa)
    if (func_Aoi_getPa) {
      func_Aoi_getPa.implementation = function (i) {
        var funcName = "Aoi.getPa"
        var funcParaDict = {
          "i": i,
        }
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        var retPa = this.getPa(i)
        console.log("Aoi.getPa => retPa=" + retPa)
        return retPa
      }
    }

    // public final void h() {
    // 
    var func_Aoi_h = cls_Aoi.h
    console.log("func_Aoi_h=" + func_Aoi_h)
    if (func_Aoi_h) {
      func_Aoi_h.implementation = function () {
        var funcName = "Aoi.h"
        var funcParaDict = {}
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        return this.h()
      }
    }

    // public final void ra() {
    // 
    var func_Aoi_ra = cls_Aoi.ra
    console.log("func_Aoi_ra=" + func_Aoi_ra)
    if (func_Aoi_ra) {
      func_Aoi_ra.implementation = function () {
        var funcName = "Aoi.ra"
        var funcParaDict = {}
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        return this.ra()
      }
    }

    // public final void ra2() {
    // 
    var func_Aoi_ra2 = cls_Aoi.ra2
    console.log("func_Aoi_ra2=" + func_Aoi_ra2)
    if (func_Aoi_ra2) {
      func_Aoi_ra2.implementation = function () {
        var funcName = "Aoi.ra2"
        var funcParaDict = {}
        FridaAndroidUtil.printFunctionCallAndStack(funcName, funcParaDict)

        return this.ra2()
      }
    }
  }

}
```

#### How to use

copy the hook code

```js
static <ClassName>() {
  ...
}
```

into you Frida (hook Android java) js file

then continue to do your normal Frida debug android work


#### About FridaAndroidUtil

the generated hook code contain some util funtions, such as:

* `FridaAndroidUtil.printClassAllMethodsFields`
* `FridaAndroidUtil.printFunctionCallAndStack`

you can find `FridaAndroidUtil` full code from:

https://github.com/crifan/JsFridaUtil/blob/main/frida/FridaAndroidUtil.js

### How to write Frida hook (Android java) js code

you can refer:

https://github.com/crifan/FridaHookTemplate/blob/main/Android/frida/fridaHookAndroidSomeApp.js

in my template:

https://github.com/crifan/FridaHookTemplate

### About parameters in `settings.json`

#### `"isOverload": true`

for some special case:

some functions have same function name, that is: `overload`

then related config part is:

```json
          {
            "defineSource": "public final int a(String str, String str2) {",
            "defineFrida": "",
            "isOverload": true
          },
          {
            "defineSource": "public final void a() {",
            "defineFrida": "",
            "isOverload": true
          },
          ...
          {
            "defineSource": "public static IBinder b(String str) {",
            "defineFrida": "",
            "isOverload": true
          },
          {
            "defineSource": "public final void b() {",
            "defineFrida": "",
            "isOverload": true
          },
          {
            "defineSource": "public boolean b(Intent intent) {",
            "defineFrida": "",
            "isOverload": true
          },
```

=> generated frida hook code for overload function is:

```js
    // public final int a(String str, String str2) {
    // 
    var func_Aoi_a_2pss = cls_Aoi.a.overload()
    ...

    // public final void a() {
    // 
    var func_Aoi_a_0p = cls_Aoi.a.overload()
    ...

    // public static IBinder b(String str) {
    // 
    var func_Aoi_b_1ps = cls_Aoi.b.overload()
    ...

    // public final void b() {
    // 
    var func_Aoi_b_0p = cls_Aoi.b.overload()
    ...

    // public boolean b(Intent intent) {
    // 
    var func_Aoi_b_1pi = cls_Aoi.b.overload()
    ...
```

but as we know the `.overload()` no parameter type will fail when Frida js running

so if we want to fix it, then should:

( after first run hook code 

```js
FridaAndroidUtil.printClassAllMethodsFields(clsName_Aoi)
```

it will generated the frida found/print function definition, with parameter type )

manually added related parameter type, into `defineFrida`, like this:


```json
          {
            "defineSource": "public final int a(String str, String str2) {",
            "defineFrida": "public final int a(java.lang.String,java.lang.String)",
            "isOverload": true
          },
          {
            "defineSource": "public final void a() {",
            "defineFrida": "public final void a()",
            "isOverload": true
          },
          ...
          {
            "defineSource": "public static IBinder b(String str) {",
            "defineFrida": "public static android.os.IBinder com.aSIIoEMUzSXAoi.b(java.lang.String)",
            "isOverload": true
          },
          {
            "defineSource": "public final void b() {",
            "defineFrida": "public final void b()",
            "isOverload": true
          },
          {
            "defineSource": "public boolean b(Intent intent) {",
            "defineFrida": "public boolean b(android.content.Intent)",
            "isOverload": true
          },
```

=> then the generated code auto added parater type for `.overload()`:

```js
    // public final int a(String str, String str2) {
    // public final int a(java.lang.String,java.lang.String)
    var func_Aoi_a_2pss = cls_Aoi.a.overload("java.lang.String", "java.lang.String")
    ...

    // public final void a() {
    // public final void a()
    var func_Aoi_a_0p = cls_Aoi.a.overload()
    ...

    // public static IBinder b(String str) {
    // public static android.os.IBinder com.aSIIoEMUzSXAoi.b(java.lang.String)
    var func_Aoi_b_1ps = cls_Aoi.b.overload("java.lang.String")
    ...

    // public final void b() {
    // public final void b()
    var func_Aoi_b_0p = cls_Aoi.b.overload()
    ...

    // public boolean b(Intent intent) {
    // public boolean b(android.content.Intent)
    var func_Aoi_b_1pi = cls_Aoi.b.overload("android.content.Intent")
    ...
```

then the frida hook code will work normally, can find the overloaed function and triggered normally.

#### `displayFuncNameWithParas`

default is `displayFuncNameWithParas: false`, effect: display function name without parameters

```js
        var funcName = "Aoi.b_1ps"
        ...
        console.log("Aoi.b_1ps => retIBinder_1ps=" + retIBinder_1ps)
```

if set to `"displayFuncNameWithParas": true`, effect: display function name with parameters

```js
        var funcName = "Aoi.b_1ps(str)"
        ...
        console.log("Aoi.b_1ps(str) => retIBinder_1ps=" + retIBinder_1ps)
```
