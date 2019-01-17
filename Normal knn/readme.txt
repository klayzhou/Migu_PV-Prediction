不建议knn相关算法，真的太慢了。。。

目前的算法是先用全量的knn预测出前一个小时的点击量，之后根据前一小时的点击量和时间的vector，去预测下一个小时的点击量

(all the features removing the week vector)------predicted by knn-----------previous click

previous+week vector--------------random forest---------------next hour click

可能的改进是，直接用全部的特征通过knn计算出下一个小时的点击量
但是真的不建议用，速度太慢了，毕竟是个O(n2)的遍历算法