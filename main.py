import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.clipboard import Clipboard
from kivy.uix.label import Label
from kivy.clock import mainthread, Clock
from kivy.core.text import LabelBase, DEFAULT_FONT, Label as CoreLabel
from kivy.config import Config
from kivy.graphics import Color, Rectangle
import requests
from functools import partial
import os
import sys


# -------------------------- 字体配置 --------------------------
def setup_chinese_font():
    local_font = "simhei.ttf"
    if os.path.exists(local_font):
        LabelBase.register(DEFAULT_FONT, local_font)
        print(f"成功加载本地字体：{local_font}")
    else:
        font_paths = {
            'win32': 'C:/Windows/Fonts/simhei.ttf',
            'linux': '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            'darwin': '/System/Library/Fonts/PingFang.ttc',
            'android': '/system/fonts/NotoSansCJK-SC.ttf'
        }
        platform = sys.platform
        fallback_font = font_paths.get(platform)
        if fallback_font and os.path.exists(fallback_font):
            LabelBase.register(DEFAULT_FONT, fallback_font)
            print(f"加载系统备选字体：{fallback_font}")
        else:
            print("警告：未找到中文字体文件，部分中文可能显示异常！")
            LabelBase.register(DEFAULT_FONT, DEFAULT_FONT)


setup_chinese_font()


# -------------------------- 爬取函数（内存保护） --------------------------
def get_url_text(url, headers):
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        r.raise_for_status()
        r.encoding = 'utf-8' if not r.encoding else r.apparent_encoding
        content = r.text
        # 内存保护：超过5万字符截断
        if len(content) > 100000:
            content = content[:100000] + "\n\n【⚠️ 内容超过10万字符，已截断保护内存】"
        return content
    except requests.exceptions.Timeout:
        return "爬取失败：请求超时（网址可能无法访问）"
    except requests.exceptions.ConnectionError:
        return "爬取失败：网络连接错误（请检查网络）"
    except Exception as e:
        return f"爬取失败：{str(e)}"


# -------------------------- 主布局类（纯基础API，兼容所有Kivy版本） --------------------------
class WebCrawlerLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 20
        self.spacing = 15

        # 基础窗口配置
        self.min_width = 300
        Config.set('graphics', 'width', '300')
        Config.set('graphics', 'height', '600')
        Config.set('graphics', 'multisamples', '0')
        os.environ['KIVY_GL_BACKEND'] = 'gl'

        # 1. 网址输入框
        self.url_input = TextInput(
            hint_text="请输入网址（如：www.baidu.com）",
            size_hint_y=None,
            height=60,
            multiline=False,
            font_name=DEFAULT_FONT,
            font_size=18,
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[10, 15]
        )
        self.add_widget(self.url_input)

        # 2. 功能按钮布局
        btn_layout = BoxLayout(size_hint_y=None, height=70, spacing=15)
        # 爬取按钮
        self.crawl_btn = Button(
            text="爬取",
            size_hint=(0.5, 1),
            background_color=(0.2, 0.7, 0.2, 1),
            font_name=DEFAULT_FONT,
            font_size=22,
            color=(1, 1, 1, 1)
        )
        self.crawl_btn.bind(on_press=self.start_crawl)
        btn_layout.add_widget(self.crawl_btn)
        # 复制按钮
        self.copy_btn = Button(
            text="复制",
            size_hint=(0.5, 1),
            background_color=(0.2, 0.2, 0.7, 1),
            font_name=DEFAULT_FONT,
            font_size=22,
            color=(1, 1, 1, 1),
            disabled=True
        )
        self.copy_btn.bind(on_press=self.copy_content)
        btn_layout.add_widget(self.copy_btn)
        self.add_widget(btn_layout)

        # 3. 结果展示区域（核心：纯基础API计算高度）
        result_box = BoxLayout(size_hint=(1, 1), orientation='vertical', spacing=10)
        result_title = Label(
            text="爬取结果（可上下滑动）：",
            size_hint_y=None,
            height=40,
            font_name=DEFAULT_FONT,
            font_size=20,
            color=(0, 0, 0, 1),
            halign='left'
        )
        result_box.add_widget(result_title)

        # 滚动视图（仅用公开属性）
        self.result_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            scroll_type=['content', 'bars'],
            scroll_wheel_distance=15,
            bar_width=8,
            bar_color=(0.4, 0.4, 0.4, 1),
            bar_inactive_color=(0.8, 0.8, 0.8, 1)
        )
        # 白色背景
        with self.result_scroll.canvas.before:
            Color(1, 1, 1, 1)
            self.scroll_bg = Rectangle(size=self.result_scroll.size, pos=self.result_scroll.pos)
        self.result_scroll.bind(size=lambda i, s: setattr(self.scroll_bg, 'size', s))
        self.result_scroll.bind(pos=lambda i, p: setattr(self.scroll_bg, 'pos', p))

        # 🔥 终极方案：用CoreLabel计算高度（纯基础API，无版本兼容问题）
        self.result_input = TextInput(
            text="点击“爬取”按钮获取内容...",
            size_hint=(1, None),
            font_name=DEFAULT_FONT,
            font_size=16,
            background_color=(0.98, 0.98, 0.98, 1),
            foreground_color=(0, 0, 0, 1),
            readonly=True,
            multiline=True,
            padding=[10, 10]
        )
        # 初始高度（用CoreLabel计算）
        self.result_input.height = self.get_text_height(self.result_input.text, self.result_input)
        # 绑定文本变化，自动更新高度
        self.result_input.bind(text=self.update_text_height)

        self.result_scroll.add_widget(self.result_input)
        result_box.add_widget(self.result_scroll)
        self.add_widget(result_box)

        # 4. 状态提示
        self.status_label = Label(
            size_hint_y=None,
            height=40,
            color=(1, 0, 0, 1),
            font_name=DEFAULT_FONT,
            font_size=16,
            halign='left'
        )
        self.add_widget(self.status_label)

        # 延迟初始化，降低启动负载
        Clock.schedule_once(self.init_delayed, 0.1)

    # 核心：用CoreLabel计算文本高度（纯基础API，兼容所有版本）
    def get_text_height(self, text, text_input):
        # 创建CoreLabel（Kivy基础文本渲染类，无版本差异）
        core_label = CoreLabel(
            text=text,
            font_name=text_input.font_name,
            font_size=text_input.font_size,
            width=text_input.width - 20,  # 减去padding
            halign='left',
            valign='top'
        )
        # 刷新布局计算
        core_label.refresh()
        # 返回文本真实高度 + padding
        return core_label.texture.size[1] + 20

    # 文本变化时更新高度
    def update_text_height(self, instance, new_text):
        # 延迟计算，避免频繁触发
        Clock.schedule_once(lambda dt: self._do_update_height(instance), 0.02)

    def _do_update_height(self, instance):
        # 确保宽度有效
        if instance.width <= 0:
            instance.height = 200  # 兜底高度
            return
        # 计算并设置高度
        instance.height = self.get_text_height(instance.text, instance)

    # 延迟初始化
    def init_delayed(self, dt):
        self._do_update_height(self.result_input)
        self.result_scroll.scroll_y = 1.0  # 滚动到顶部

    # 爬取逻辑
    def start_crawl(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = "❌ 请输入有效网址！"
            return

        # 清空旧内容，设置加载提示
        self.result_input.text = "🔄 正在爬取...请稍候..."
        self._do_update_height(self.result_input)  # 更新提示文字高度
        self.status_label.text = "🔄 正在爬取...（内容较长请稍等）"
        self.crawl_btn.disabled = True
        self.copy_btn.disabled = True

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept-Charset": "utf-8"
        }

        # 异步爬取，避免阻塞UI
        from threading import Thread
        Thread(target=partial(self.crawl_worker, url, headers), daemon=True).start()

    def crawl_worker(self, url, headers):
        result = get_url_text(url, headers)
        self.update_result_ui(result)

    # 更新UI（主线程执行）
    @mainthread
    def update_result_ui(self, content):
        # 设置内容
        self.result_input.text = content
        # 更新高度
        self._do_update_height(self.result_input)
        # 滚动到顶部
        self.result_scroll.scroll_y = 1.0

        # 状态提示
        if "爬取失败" in content:
            self.status_label.text = content
        else:
            content_len = len(content.replace("【⚠️ 内容超过5万字符...】", ""))
            self.status_label.text = f"✅ 爬取完成！共{content_len}字符，可滑动查看"

        self.crawl_btn.disabled = False
        self.copy_btn.disabled = False

    # 复制功能
    def copy_content(self, instance):
        content = self.result_input.text
        # 过滤无效内容
        if content and not content.startswith("点击“爬取”") and not content.startswith("🔄 正在爬取"):
            Clipboard.copy(content)
            self.status_label.text = "📋 完整内容已复制到剪贴板！"
        else:
            self.status_label.text = "❌ 无有效内容可复制！"


# -------------------------- 主应用类 --------------------------
class WebCrawlerApp(App):
    def build(self):
        self.title = "网页爬取工具"
        # 通用配置，兼容所有设备
        Config.set('graphics', 'fullscreen', 'auto')
        Config.set('graphics', 'resizable', True)
        Config.set('graphics', 'borderless', False)
        Config.set('graphics', 'disable_multitouch', True)
        return WebCrawlerLayout()

    def on_stop(self):
        # 恢复默认配置
        Config.set('graphics', 'multisamples', '2')


if __name__ == "__main__":
    # 强制稳定渲染模式
    os.environ['KIVY_TEXT'] = 'pil'
    os.environ['KIVY_DPI'] = '144'
    os.environ['KIVY_NO_CONFIG'] = '1'
    WebCrawlerApp().run()
