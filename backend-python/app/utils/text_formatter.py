"""文本格式化工具"""

import re
from typing import Optional, List


class TextFormatter:
    """文本格式化工具类"""
    
    @staticmethod
    def clean_markdown(text: str) -> str:
        """
        清理和规范化 Markdown 文本
        - 移除多余的空行
        - 确保标题前后有空行
        - 规范化列表格式
        """
        if not text:
            return ""
        
        # 移除首尾空白
        text = text.strip()
        
        # 将多个连续空行替换为单个空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 确保标题前后有空行（除非在文本开头）
        text = re.sub(r'([^\n])\n(#{1,6}\s)', r'\1\n\n\2', text)
        text = re.sub(r'(#{1,6}\s[^\n]+)\n([^\n#])', r'\1\n\n\2', text)
        
        # 规范化列表项（确保列表项前有空格）
        text = re.sub(r'\n-([^\s])', r'\n- \1', text)
        text = re.sub(r'\n\*([^\s*])', r'\n* \1', text)
        
        # 确保加粗标记周围没有多余空格
        text = re.sub(r'\*\*\s+', '**', text)
        text = re.sub(r'\s+\*\*', '**', text)
        
        return text
    
    @staticmethod
    def add_paragraph_breaks(text: str) -> str:
        """
        为纯文本添加段落分隔
        适用于 LLM 没有返回 Markdown 格式的情况
        """
        if not text:
            return ""
        
        # 如果已经包含 Markdown 标题，直接返回
        if re.search(r'#{1,6}\s', text):
            return TextFormatter.clean_markdown(text)
        
        # 按句号、问号、感叹号分句
        sentences = re.split(r'([。！？\.\!\?])', text)
        
        # 重新组合句子
        result = []
        current_paragraph = []
        sentence_count = 0
        
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]
            else:
                sentence = sentences[i]
            
            sentence = sentence.strip()
            if not sentence:
                continue
            
            current_paragraph.append(sentence)
            sentence_count += 1
            
            # 每3-4句话分一段
            if sentence_count >= 3:
                result.append(''.join(current_paragraph))
                current_paragraph = []
                sentence_count = 0
        
        # 添加剩余的句子
        if current_paragraph:
            result.append(''.join(current_paragraph))
        
        # 用双换行符连接段落
        return '\n\n'.join(result)
    
    @staticmethod
    def format_divination_result(text: str, add_structure: bool = True) -> str:
        """
        格式化占卜结果文本
        
        Args:
            text: 原始文本
            add_structure: 是否自动添加结构（当文本没有 Markdown 格式时）
        
        Returns:
            格式化后的文本
        """
        if not text:
            return ""
        
        # 清理文本
        text = text.strip()
        
        # 检查是否已经是 Markdown 格式
        has_markdown = bool(re.search(r'#{1,6}\s', text))
        
        if has_markdown:
            # 已有 Markdown 格式，只做清理
            return TextFormatter.clean_markdown(text)
        elif add_structure:
            # 尝试自动添加段落分隔
            return TextFormatter.add_paragraph_breaks(text)
        else:
            # 只做基本清理
            return text
    
    @staticmethod
    def extract_key_points(text: str) -> List[str]:
        """
        从文本中提取关键要点
        适用于生成摘要或重点提示
        """
        key_points = []
        
        # 提取加粗的内容
        bold_matches = re.findall(r'\*\*([^*]+)\*\*', text)
        key_points.extend(bold_matches)
        
        # 提取列表项
        list_matches = re.findall(r'[-*]\s+([^\n]+)', text)
        key_points.extend(list_matches)
        
        # 去重并返回
        return list(dict.fromkeys(key_points))
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 150, suffix: str = '...') -> str:
        """
        截断文本到指定长度，保持完整性
        
        Args:
            text: 原始文本
            max_length: 最大长度
            suffix: 截断后缀
        
        Returns:
            截断后的文本
        """
        if not text or len(text) <= max_length:
            return text
        
        # 移除 Markdown 标记
        clean_text = re.sub(r'#{1,6}\s', '', text)
        clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_text)
        clean_text = re.sub(r'[-*]\s+', '', clean_text)
        
        # 截断到最近的句子结束
        truncated = clean_text[:max_length]
        last_period = max(
            truncated.rfind('。'),
            truncated.rfind('！'),
            truncated.rfind('？'),
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?')
        )
        
        if last_period > max_length * 0.7:  # 如果找到的句号位置合理
            return truncated[:last_period + 1]
        else:
            return truncated + suffix
    
    @staticmethod
    def ensure_markdown_format(text: str) -> str:
        """
        确保文本是 Markdown 格式
        如果不是，尝试转换
        """
        if not text:
            return ""
        
        # 检查是否已经有 Markdown 标题
        if re.search(r'#{1,6}\s', text):
            return TextFormatter.clean_markdown(text)
        
        # 尝试识别结构并转换
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append('')
                continue
            
            # 识别可能的标题（短句、以数字或关键词开头）
            if len(line) < 20 and (
                re.match(r'^[一二三四五六七八九十\d]+[、\.．]', line) or
                any(keyword in line for keyword in ['建议', '解读', '展望', '分析', '总结'])
            ):
                # 转换为二级标题
                formatted_lines.append(f'## {line}')
            # 识别列表项
            elif re.match(r'^[•·\-]\s*', line):
                pattern = r'^[•·\-]\s*'
                cleaned = re.sub(pattern, '', line)
                formatted_lines.append(f'- {cleaned}')
            else:
                formatted_lines.append(line)
        
        return '\n\n'.join(formatted_lines)
