# nfo to vsmeta
通过Emby/Jellyfin/TinyMediaManager等刮削到的nfo元数据，转换成群晖Video Station专用vsmeta元数据。共享刮削数据

使用方法
-----------------
1. 保存 transfer.py 到群晖任意目录
2. 修改其中 directory = r'/volume1/video/Links/' 为视频文件实际目录
3. 在群晖控制面板 > 任务计划，新增 > 计划的任务 > 用户定义的脚本
4. 计划名称、执行时间、执行频率按需设置
5. 自定义脚本栏输入命令（注意修改路径为实际保存transfer.py的路径）： python3 /volume1/xxx/transfer.py
