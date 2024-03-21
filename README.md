# nfo to vsmeta
通过 Emby/Jellyfin/TinyMediaManager 等刮削到的nfo元数据，转换成群晖 Video Station 专用 vsmeta 元数据。共享刮削数据

使用方法
-----------------
1. 保存 transfer.py 到群晖任意目录
2. 修改 directory = r'/volume1/video/Links/' 为视频文件实际目录；建议配合NasTool使用硬链目录
3. 修改 poster = 'poster.jpg' 为刮削到的海报图文件名
4. 修改 fanart = 'fanart.jpg' 为刮削到的背景图文件名
5. 在群晖控制面板 > 任务计划，新增 > 计划的任务 > 用户定义的脚本
6. 计划名称、执行时间、执行频率按需设置
7. 自定义脚本栏输入命令（注意修改路径为实际保存 transfer.py 的路径）： python3 /volume1/xxx/transfer.py
8. 已转换过的不会重复转换，需要重置，可以手动删除 *.vsmeta 文件后再运行脚本；也可以放开 19 20 两行注释，会自动删除所有 vsmeta ，并重新转换。重置后，需手动点 设置 > 视频库 > 再次搜索所有视频信息 刷新元数据缓存

使用效果
-----------------
![image](https://github.com/JuanWoo/nfo-to-vsmeta/assets/4869539/5c089d2c-8064-4c94-bf42-c6e3117e2492)
