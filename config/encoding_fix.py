# encoding_fix.py：统一Python环境编码，解决中文解码问题
import sys
import io
import locale

# 1. 强制标准输出/错误流使用UTF-8编码（解决终端流解码）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 2. 设置系统区域编码为UTF-8（适配Windows）
try:
    locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
except:
    # 若UTF-8不兼容，降级为GBK（Windows默认），但仍保证解码不崩溃
    locale.setlocale(locale.LC_ALL, 'zh_CN.GBK')

# 3. 强制Python默认编码为UTF-8
import _locale
_locale._getdefaultlocale = (lambda *args: ['zh_CN', 'utf8'])