# m3u8-MultithreadingDownload
多线程下载m3u8链接电影并自动整合.ts文件

# 使用

-u -> m3u8路径

-d -> 下载路径

-t -> 线程数默认3

## 使用方式:
```sh
python m3u8Download.py -u https://up.imgupio.com/demo/birds.m3u8 -d d:/backup -t 102
```


## 更新记录
v1.0 采用多线程下载M3u8的视频地址

## 待优化
-   多个m3u8下载并发下载
-   增加线程池保证下载稳定型
-   增加下载重试次数保证稳定
    
    