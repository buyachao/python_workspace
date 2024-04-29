@echo off

rem 设置需要生成的编号数组
set nums=4 6

rem 遍历编号数组
for %%i in (%nums%) do (
  rem 复制COM.py为COM{num}.py
  copy COM.py COM%%i.py

  rem 执行cxfreeze生成COM{num}.exe
  cxfreeze COM%%i.py --target-dir COM%%i --target-name COM%%i.exe

  rem 删除生成的多余文件
  del COM%%i.py
  #del COM%%i\python37.dll
  #del COM%%i\python3.dll
)