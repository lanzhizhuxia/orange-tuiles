# 导入绘图库matplotlib和词云制作库wordcloud
import matplotlib.pyplot as plt
import jieba
from wordcloud import WordCloud,ImageColorGenerator

# 将外部文件包含的文本保存在text变量中
text = open('wordcloud.txt').read()

# 导入imageio库中的imread函数，并用这个函数读取本地图片queen2.jfif，作为词云形状图片
import imageio
mk = imageio.imread("WechatIMG43.jpeg")

# 构建词云对象w
wc = WordCloud(background_color="white",
               mask=mk,
               scale=5,
               min_font_size=4,
               max_font_size=65,
               font_path = 'msyhl.ttc')
# 对来自外部文件的文本进行中文分词，得到string
txtlist = jieba.lcut(text)
string = " ".join(txtlist)
# 将text字符串变量传入w的generate()方法，给词云输入文字
wc.generate(string)

# 调用wordcloud库中的ImageColorGenerator()函数，提取模板图片各部分的颜色
image_colors = ImageColorGenerator(mk)

# 显示原生词云图、按模板图片颜色的词云图和模板图片，按左、中、右显示
fig, axes = plt.subplots(1, 3)
# 最左边的图片显示原生词云图
axes[0].imshow(wc)
# 中间的图片显示按模板图片颜色生成的词云图，采用双线性插值的方法显示颜色
axes[1].imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
# 右边的图片显示模板图片
axes[2].imshow(mk, cmap=plt.cm.gray)
for ax in axes:
    ax.set_axis_off()
plt.show()

# 给词云对象按模板图片的颜色重新上色
wc_color = wc.recolor(color_func=image_colors)
# 将词云图片导出到当前文件夹
wc_color.to_file('output10-alice.png')