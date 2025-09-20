from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib import colors


class PDFExporter:
    def __init__(self, filename, title="文档标题"):
        # 注册简体中文字体
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

        self.filename = filename
        self.title = title
        self.styles = getSampleStyleSheet()

        # 定义样式
        self.style_normal = ParagraphStyle(
            'ChineseNormal',
            parent=self.styles['Normal'],
            fontName='STSong-Light',
            fontSize=12,
            leading=20
        )
        self.style_title = ParagraphStyle(
            'ChineseTitle',
            parent=self.styles['Title'],
            fontName='STSong-Light',
            fontSize=18,
            leading=24,
            alignment=1  # 居中
        )
        self.story = []

    def add_title(self, text=None):
        """添加标题"""
        text = text if text else self.title
        self.story.append(Paragraph(text, self.style_title))
        self.story.append(Spacer(1, 20))

    def add_paragraph(self, text):
        """添加正文段落"""
        self.story.append(Paragraph(text, self.style_normal))
        self.story.append(Spacer(1, 12))

    def add_table(self, data, col_widths=None, row_heights=None):
        """添加表格"""
        table = Table(data, colWidths=col_widths, rowHeights=row_heights)
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'STSong-Light'),  # 中文字体
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # 表头背景色
        ]))
        self.story.append(table)
        self.story.append(Spacer(1, 12))

    def add_image(self, image_path, width=200, height=150):
        """添加图片"""
        img = Image(image_path, width, height)
        self.story.append(img)
        self.story.append(Spacer(1, 12))

    def add_page_break(self):
        """分页"""
        self.story.append(PageBreak())

    def _header_footer(self, canvas, doc):
        """页眉页脚"""
        canvas.saveState()
        # 页眉
        canvas.setFont("STSong-Light", 10)
        canvas.drawString(30, A4[1] - 30, self.title)
        # 页脚
        page_num = canvas.getPageNumber()
        canvas.drawRightString(A4[0] - 30, 30, f"第 {page_num} 页")
        canvas.restoreState()

    def export(self):
        """导出 PDF"""
        doc = SimpleDocTemplate(self.filename, pagesize=A4)
        doc.build(self.story, onFirstPage=self._header_footer, onLaterPages=self._header_footer)


if __name__ == "__main__":
    pdf = PDFExporter("output_full.pdf", title="自动化测试报告")

    # 标题
    pdf.add_title()

    # 正文
    pdf.add_paragraph("这是一个包含文本、表格和图片的 PDF 导出示例。")

    # 表格
    table_data = [
        ["序号", "项目", "结果"],
        ["1", "登录功能", "通过"],
        ["2", "数据导出", "通过"],
        ["3", "异常处理", "失败"]
    ]
    pdf.add_table(table_data, col_widths=[60, 200, 100])

    # 图片
    pdf.add_paragraph("下面是测试截图：")
    pdf.add_image("example.png", width=300, height=200)

    # 分页
    pdf.add_page_break()
    pdf.add_paragraph("这是第二页内容。")

    # 导出
    pdf.export()
