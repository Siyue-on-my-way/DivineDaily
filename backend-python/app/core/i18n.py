"""国际化工具类"""
from app.core.logger import get_logger
logger = get_logger("i18n")

import json
from pathlib import Path
from typing import Dict, Optional


class I18n:
    """国际化管理器"""
    
    def __init__(self):
        self.translations: Dict[str, Dict[str, str]] = {}
        self.default_locale = "zh_CN"
        self._load_translations()
    
    def _load_translations(self):
        """加载所有翻译文件"""
        locale_dir = Path(__file__).parent.parent / "locales"
        
        if not locale_dir.exists():
            return
        
        for locale_file in locale_dir.glob("*.json"):
            locale = locale_file.stem
            try:
                with open(locale_file, 'r', encoding='utf-8') as f:
                    self.translations[locale] = json.load(f)
            except Exception as e:
                logger.error("加载翻译文件失败", extra={"locale_file": str(locale_file)}, exc_info=True)
    
    def t(self, key: str, locale: Optional[str] = None, **kwargs) -> str:
        """
        翻译文本
        
        Args:
            key: 翻译键
            locale: 语言代码（如 zh_CN, en_US），默认使用 default_locale
            **kwargs: 格式化参数
        
        Returns:
            翻译后的文本，如果找不到则返回 key
        
        Examples:
            >>> i18n.t("welcome")
            "欢迎"
            >>> i18n.t("welcome", locale="en_US")
            "Welcome"
            >>> i18n.t("greeting", name="张三")
            "你好，张三"
        """
        if locale is None:
            locale = self.default_locale
        
        # 获取翻译文本
        text = self.translations.get(locale, {}).get(key, key)
        
        # 如果当前语言没有翻译，尝试使用默认语言
        if text == key and locale != self.default_locale:
            text = self.translations.get(self.default_locale, {}).get(key, key)
        
        # 格式化参数
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        return text
    
    def set_default_locale(self, locale: str):
        """设置默认语言"""
        self.default_locale = locale
    
    def get_available_locales(self) -> list:
        """获取可用的语言列表"""
        return list(self.translations.keys())
    
    def reload(self):
        """重新加载翻译文件"""
        self.translations.clear()
        self._load_translations()


# 全局单例
_i18n_instance = None


def get_i18n() -> I18n:
    """获取 i18n 实例"""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n()
    return _i18n_instance


# 便捷函数
def t(key: str, locale: Optional[str] = None, **kwargs) -> str:
    """翻译文本的便捷函数"""
    return get_i18n().t(key, locale, **kwargs)


def get_locale_from_header(accept_language: Optional[str]) -> str:
    """
    从 Accept-Language 请求头解析语言
    
    Args:
        accept_language: Accept-Language 请求头值
    
    Returns:
        语言代码（zh_CN 或 en_US）
    
    Examples:
        >>> get_locale_from_header("zh-CN,zh;q=0.9,en;q=0.8")
        "zh_CN"
        >>> get_locale_from_header("en-US,en;q=0.9")
        "en_US"
    """
    if not accept_language:
        return "zh_CN"
    
    # 解析 Accept-Language 头
    languages = []
    for lang in accept_language.split(','):
        parts = lang.strip().split(';')
        language = parts[0].strip()
        
        # 提取权重
        quality = 1.0
        if len(parts) > 1:
            try:
                quality = float(parts[1].split('=')[1])
            except (IndexError, ValueError):
                pass
        
        languages.append((language, quality))
    
    # 按权重排序
    languages.sort(key=lambda x: x[1], reverse=True)
    
    # 匹配语言
    for language, _ in languages:
        language_lower = language.lower()
        
        if language_lower.startswith('zh'):
            return "zh_CN"
        elif language_lower.startswith('en'):
            return "en_US"
    
    return "zh_CN"
