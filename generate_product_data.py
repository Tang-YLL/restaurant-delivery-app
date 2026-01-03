"""
为商品生成测试数据
1. 生成白底黑字的主图（使用菜品名字）
2. 添加商品详情内容（故事、营养等）
"""
import sqlite3
from PIL import Image, ImageDraw, ImageFont
import os

# 数据库配置
DB_PATH = "backend/restaurant.db"

# 商品详情内容模板
PRODUCT_DETAILS = {
    "宫保鸡丁": {
        "story": """<h2>经典川菜</h2><p>宫保鸡丁是四川省传统名菜，属于川菜系。相传由清代四川总督丁宝桢所创，色泽红亮，肉质鲜嫩，酸甜微辣，鲜香可口。</p><p>选用嫩鸡胸肉，配以花生米、干辣椒、花椒等，经过精心炒制而成。鸡肉嫩滑，花生香脆，是一道色香味俱全的经典菜肴。</p>""",
        "nutrition": {
            "serving_size": "1份(300g)",
            "calories": 280,
            "protein": 24.5,
            "fat": 12.3,
            "carbohydrates": 18.6,
            "sodium": 850
        },
        "ingredients": """<h2>精选食材</h2><ul><li><strong>主料</strong>：嫩鸡胸肉 200g</li><li><strong>配菜</strong>：花生米 80g、干辣椒 10g</li><li><strong>调料</strong>：花椒、生抽、老抽、料酒</li><li><strong>特点</strong>：无添加剂，纯天然食材</li></ul>""",
        "process": """<h2>制作工艺</h2><ol><li>鸡肉切丁，用料酒、生抽腌制15分钟</li><li>花生米炸制至金黄酥脆</li><li>热锅下油，先炒干辣椒和花椒出香味</li><li>下鸡丁快速翻炒至变色</li><li>加入调味料和花生米翻炒即可</li></ol>""",
        "tips": """<h2>食用贴士</h2><ul><li>建议趁热食用，口感最佳</li><li>可搭配米饭或面条</li><li>微辣，适合大众口味</li><li>冷藏保存24小时内食用完</li></ul>"""
    },
    "鱼香肉丝": {
        "story": """<h2>川菜代表</h2><p>鱼香肉丝是一道闻名中外的经典川菜，距今已有百年历史。虽名"鱼香"，但实际并不含鱼，而是通过泡红辣椒、葱、姜、蒜、糖、盐、酱油等调味品调制而成，具有鱼香味。</p><p>这道菜色泽红亮，肉丝嫩滑，味道酸甜微辣，非常下饭。</p>""",
        "nutrition": {
            "serving_size": "1份(280g)",
            "calories": 320,
            "protein": 22.1,
            "fat": 15.8,
            "carbohydrates": 21.3,
            "sodium": 920
        },
        "ingredients": """<h2>精选食材</h2><ul><li><strong>主料</strong>：猪里脊肉 250g</li><li><strong>配菜</strong>：木耳 50g、胡萝卜 50g、青笋 50g</li><li><strong>调料</strong>：泡红辣椒、葱姜蒜、白糖、醋</li><li><strong>特点</strong>：正宗川菜风味</li></ul>""",
        "process": """<h2>制作工艺</h2><ol><li>猪肉切丝，用淀粉上浆</li><li>配菜切丝备用</li><li>调制鱼香汁（醋、糖、生抽等）</li><li>滑炒肉丝至变色盛出</li><li>炒配料和调料，下肉丝翻炒均匀</li></ol>""",
        "tips": """<h2>食用贴士</h2><ul><li>鱼香味浓郁，开胃下饭</li><li>适合喜欢酸甜微辣口味的人群</li><li>建议现炒现吃</li></ul>"""
    },
    "麻婆豆腐": {
        "story": """<h2>百年老店</h2><p>麻婆豆腐是清同治年间成都万福桥一家名为"陈兴盛饭铺"的小饭店，由老板娘陈刘氏所创。因其脸上有麻点，人称陈麻婆，她做的豆腐便被称为"麻婆豆腐"。</p><p>特点是麻、辣、烫、香、酥、嫩、鲜、活八字，称之为八字箴言。</p>""",
        "nutrition": {
            "serving_size": "1份(350g)",
            "calories": 260,
            "protein": 18.5,
            "fat": 16.2,
            "carbohydrates": 12.8,
            "sodium": 1250
        },
        "ingredients": """<h2>精选食材</h2><ul><li><strong>主料</strong>：嫩豆腐 400g</li><li><strong>肉末</strong>：牛肉末或猪肉末 80g</li><li><strong>调料</strong>：郫县豆瓣、花椒面、辣椒面</li><li><strong>特点</strong>：麻辣鲜香，豆腐嫩滑</li></ul>""",
        "process": """<h2>制作工艺</h2><ol><li>豆腐切块，用盐水焯烫</li><li>热锅下油，炒肉末至酥香</li><li>加入豆瓣酱炒出红油</li><li>下豆腐和调料，小火焖煮</li><li>用水淀粉勾芡，撒花椒面出锅</li></ol>""",
        "tips": """<h2>食用贴士</h2><ul><li>麻辣味重，建议搭配米饭</li><li>豆腐要趁热吃，嫩滑最佳</li><li>不适合不吃辣的人群</li></ul>"""
    },
    "水煮鱼": {
        "story": """<h2>重庆名菜</h2><p>水煮鱼是重庆渝北风味，起源于重庆渝北地区，发明于1980年代。通常以草鱼为主料，配以豆芽、辣椒等辅料烹制而成。</p><p>菜品口感麻辣鲜香，汤汁浓郁，鱼肉滑嫩，是川菜中的代表性菜品之一。</p>""",
        "nutrition": {
            "serving_size": "1份(500g)",
            "calories": 420,
            "protein": 35.6,
            "fat": 22.8,
            "carbohydrates": 18.5,
            "sodium": 1680
        },
        "ingredients": """<h2>精选食材</h2><ul><li><strong>主料</strong>：草鱼 1条（约750g）</li><li><strong>配菜</strong>：豆芽 200g、青菜 150g</li><li><strong>调料</strong>：豆瓣酱、干辣椒、花椒、姜蒜</li><li><strong>特点</strong>：鱼肉鲜嫩，麻辣味浓</li></ul>""",
        "process": """<h2>制作工艺</h2><ol><li>鱼肉切片，用蛋清淀粉上浆</li><li>豆芽、青菜焯水垫底</li><li>炒调料和配菜，加汤煮开</li><li>滑入鱼片煮熟即可</li><li>撒上干辣椒和花椒，浇热油激香</li></ol>""",
        "tips": """<h2>食用贴士</h2><ul><li>麻辣味重，适合重口味人群</li><li>鱼肉嫩滑，小心刺</li><li>建议配米饭食用</li></ul>"""
    },
    "回锅肉": {
        "story": """<h2>家常之王</h2><p>回锅肉是四川传统名菜，属于川菜系。制作原料主要有猪肉、青椒、蒜苗等，口味独特，色泽红绿相间，肉质微焦，香气扑鼻。</p><p>所谓"回锅"，就是再次烹饪的意思，是川菜中最为经典的菜肴之一。</p>""",
        "nutrition": {
            "serving_size": "1份(320g)",
            "calories": 480,
            "protein": 22.3,
            "fat": 38.5,
            "carbohydrates": 8.6,
            "sodium": 980
        },
        "ingredients": """<h2>精选食材</h2><ul><li><strong>主料</strong>：五花肉 400g</li><li><strong>配菜</strong>：蒜苗 150g、青椒 50g</li><li><strong>调料</strong>：豆瓣酱、甜面酱、豆豉</li><li><strong>特点</strong>：肥而不腻，香辣下饭</li></ul>""",
        "process": """<h2>制作工艺</h2><ol><li>五花肉先煮至断生，切薄片</li><li>锅中煸出油脂，肉片呈灯盏窝状</li><li>加入豆瓣酱和豆豉炒香</li><li>下配菜翻炒至断生</li><li>调味出锅，保持微焦</li></ol>""",
        "tips": """<h2>食用贴士</h2><ul><li>经典家常菜，老少皆宜</li><li>油脂含量较高，适量食用</li><li>配蒜苗最佳，也可用青椒</li></ul>"""
    },
    "酸菜鱼": {
        "story": """<h2>开胃佳品</h2><p>酸菜鱼是重庆一带的经典江湖菜，以其独特的调味和烹饪技法而闻名。选用鲜鱼，配以老坛酸菜，烹制而成，汤汁酸辣鲜美，鱼肉细嫩。</p><p>这道菜既有鱼的鲜美，又有酸菜的爽口，非常开胃下饭。</p>""",
        "nutrition": {
            "serving_size": "1份(480g)",
            "calories": 340,
            "protein": 32.5,
            "fat": 18.6,
            "carbohydrates": 15.8,
            "sodium": 1420
        },
        "ingredients": """<h2>精选食材</h2><ul><li><strong>主料</strong>：草鱼或黑鱼 1条</li><li><strong>配菜</strong>：老坛酸菜 200g</li><li><strong>调料</strong>：野山椒、姜蒜、花椒</li><li><strong>特点</strong>：酸辣开胃，汤鲜味美</li></ul>""",
        "process": """<h2>制作工艺</h2><ol><li>鱼肉切片，用蛋清和淀粉腌制</li><li>酸菜洗净切碎备用</li><li>炒酸菜和野山椒出香味</li><li>加汤煮开，下鱼片烫熟</li><li>调味出锅，撒上葱花</li></ol>""",
        "tips": """<h2>食用贴士</h2><ul><li>酸辣开胃，食欲不振者的首选</li><li>汤可以喝，非常鲜美</li><li>可加粉丝或豆皮</li></ul>"""
    },
    "夫妻肺片": {
        "story": """<h2>成都小吃</h2><p>夫妻肺片是四川省成都市的一种传统小吃，属于川菜系。由郭朝华、张田政夫妻创制，因其经营时夫唱妇随而得名。</p><p>主料是牛头皮、牛心、牛舌、牛肚等，经过精心卤制，切片后拌入红油、花椒面、芝麻面等，色泽红亮，质地软嫩，麻辣浓香。</p>""",
        "nutrition": {
            "serving_size": "1份(250g)",
            "calories": 380,
            "protein": 28.5,
            "fat": 26.8,
            "carbohydrates": 8.2,
            "sodium": 1850
        },
        "ingredients": """<h2>精选食材</h2><ul><li><strong>主料</strong>：牛头皮、牛心、牛舌、牛肚</li><li><strong>调料</strong>：红油、花椒面、芝麻面、卤水</li><li><strong>特点</strong>：麻辣鲜香，质地软嫩</li></ul>""",
        "process": """<h2>制作工艺</h2><ol><li>牛杂清洗干净，焯水去腥</li><li>放入卤水中卤制至软烂</li><li>晾凉后切成薄片</li><li>调制麻辣汁，拌入牛杂片中</li><li>撒上芝麻和花生碎，淋红油</li></ol>""",
        "tips": """<h2>食用贴士</h2><ul><li>经典凉菜，麻辣爽口</li><li>作为开胃菜或下酒菜</li><li>适合喜欢重口味的人群</li></ul>"""
    },
    "蒜泥白肉": {
        "story": """<h2>家常凉菜</h2><p>蒜泥白肉是四川传统名菜，属于川菜系。选用猪里脊肉或后腿肉，经过煮熟、晾凉、切片，配以蒜泥、酱油、香油等调制而成。</p><p>肉片薄而均匀，蒜香浓郁，口感清爽不油腻，是夏季消暑的佳品。</p>""",
        "nutrition": {
            "serving_size": "1份(220g)",
            "calories": 340,
            "protein": 24.6,
            "fat": 25.2,
            "carbohydrates": 6.8,
            "sodium": 780
        },
        "ingredients": """<h2>精选食材</h2><ul><li><strong>主料</strong>：猪后腿肉 300g</li><li><strong>调料</strong>：蒜泥、酱油、香油、辣椒油</li><li><strong>配菜</strong>：黄瓜丝（可选）</li><li><strong>特点</strong>：蒜香浓郁，肥而不腻</li></ul>""",
        "process": """<h2>制作工艺</h2><ol><li>猪肉煮至断生，不能煮烂</li><li>晾凉后切薄片，越薄越好</li><li>调制蒜泥汁（蒜泥+酱油+香油）</li><li>肉片整齐码放，浇上蒜泥汁</li><li>可撒葱花或辣椒面增香</li></ol>""",
        "tips": """<h2>食用贴士</h2><ul><li>夏日凉菜首选，清爽开胃</li><li>肉片要切得薄而均匀</li><li>蒜泥要现捣现用</li></ul>"""
    },
    "辣子鸡": {
        "story": """<h2>重庆歌乐山</h2><p>辣子鸡是一道闻名中外的传统名菜，起源于重庆歌乐山。选用三黄鸡为主料，配以大量的干辣椒和花椒爆炒而成。</p><p>成菜色泽红亮，麻辣味浓，鸡肉外焦里嫩，是川菜中的经典之作。</p>""",
        "nutrition": {
            "serving_size": "1份(350g)",
            "calories": 420,
            "protein": 32.5,
            "fat": 22.8,
            "carbohydrates": 12.6,
            "sodium": 1450
        },
        "ingredients": """<h2>精选食材</h2><ul><li><strong>主料</strong>：三黄鸡 1只（约750g）</li><li><strong>调料</strong>：干辣椒 100g、花椒 20g</li><li><strong>辅料</strong>：芝麻、花生米、姜蒜</li><li><strong>特点</strong>：麻辣鲜香，鸡肉焦香</li></ul>""",
        "process": """<h2>制作工艺</h2><ol><li>鸡肉斩块，用料酒和盐腌制</li><li>油炸至金黄焦香</li><li>大量干辣椒和花椒炒香</li><li>下鸡块快速翻炒</li><li>撒芝麻和花生米，淋入料酒</li></ol>""",
        "tips": """<h2>食用贴士</h2><ul><li>麻辣味重，适合重口味人群</li><li>可作为下酒菜或聚会菜</li><li>配米饭或馒头均可</li></ul>"""
    },
    "东坡肉": {
        "story": """<h2>杭州名菜</h2><p>东坡肉是浙江杭州传统名菜，属于浙菜系。相传为北宋诗人苏东坡所创，故得名。选用半肥半瘦的猪肉，制成酱红色，入口肥而不腻，酥烂如豆腐而不碎。</p><p>这道菜色泽红亮，味醇汁浓，酥烂而形不碎，香糯而不腻口，是老少皆宜的美味佳肴。</p>""",
        "nutrition": {
            "serving_size": "1份(280g)",
            "calories": 580,
            "protein": 18.2,
            "fat": 48.5,
            "carbohydrates": 12.5,
            "sodium": 920
        },
        "ingredients": """<h2>精选食材</h2><ul><li><strong>主料</strong>：五花肉 500g</li><li><strong>调料</strong>：黄酒、酱油、冰糖、葱姜</li><li><strong>特点</strong>：肥而不腻，酥烂入味</li></ul>""",
        "process": """<h2>制作工艺</h2><ol><li>五花肉切成3cm见方的块</li><li>焯水去血沫，洗净沥干</li><li>砂锅垫葱姜，放上肉块</li><li>加黄酒、酱油、冰糖和清水</li><li>小火焖煮1.5小时至酥烂</li></ol>""",
        "tips": """<h2>食用贴士</h2><ul><li>经典浙菜，老少皆宜</li><li>油脂含量高，适量食用</li><li>可用汤汁拌饭，一绝</li></ul>"""
    },
    "糖醋排骨": {
        "story": """<h2>经典家常菜</h2><p>糖醋排骨是一道经典的中式家常菜，属于糖醋味型。选用猪小排，经过油炸、调味等工序制成，色泽红亮，口味酸甜，深受大人小孩喜爱。</p><p>这道菜外酥里嫩，酸甜开胃，既可作热菜上桌，也可作凉菜享用。</p>""",
        "nutrition": {
            "serving_size": "1份(300g)",
            "calories": 520,
            "protein": 26.8,
            "fat": 32.5,
            "carbohydrates": 22.6,
            "sodium": 890
        },
        "ingredients": """<h2>精选食材</h2><ul><li><strong>主料</strong>：猪小排 400g</li><li><strong>调料</strong>：白糖、醋、生抽、料酒</li><li><strong>特点</strong>：外酥里嫩，酸甜适口</li></ul>""",
        "process": """<h2>制作工艺</h2><ol><li>排骨洗净剁段，用料酒腌制</li><li>炸至金黄定型，捞出沥油</li><li>调制糖醋汁（糖:醋=1:1）</li><li>排骨放入锅中，加糖醋汁焖煮</li><li>大火收汁至浓稠油亮</li></ol>""",
        "tips": """<h2>食用贴士</h2><ul><li>大人小孩都爱吃的家常菜</li><li>糖醋比例可根据口味调整</li><li>趁热食用口感最佳</li></ul>"""
    },
    "京酱肉丝": {
        "story": """<h2>北京名菜</h2><p>京酱肉丝是北京传统名菜，属于京菜系。选用猪里脊肉为主料，配以北京特产"甜面酱"烹制而成，咸甜适中，酱香浓郁，肉丝滑嫩。</p><p>这道菜色泽红亮，酱香浓郁，肉丝滑嫩，是北京菜的代表作之一。</p>""",
        "nutrition": {
            "serving_size": "1份(260g)",
            "calories": 360,
            "protein": 25.6,
            "fat": 22.8,
            "carbohydrates": 10.5,
            "sodium": 1180
        },
        "ingredients": """<h2>精选食材</h2><ul><li><strong>主料</strong>：猪里脊肉 300g</li><li><strong>调料</strong>：甜面酱、白糖、香油</li><li><strong>配菜</strong>：豆腐皮、葱丝、黄瓜丝</li><li><strong>特点</strong>：酱香浓郁，咸甜适中</li></ul>""",
        "process": """<h2>制作工艺</h2><ol><li>里脊肉切丝，用蛋清淀粉上浆</li><li>滑炒至变色盛起</li><li>炒甜面酱出香味，加白糖调味</li><li>下肉丝翻炒均匀</li><li>用豆腐皮、葱丝、黄瓜丝卷着吃</li></ol>""",
        "tips": """<h2>食用贴士</h2><ul><li>经典京菜，老少皆宜</li><li>用豆腐皮卷着吃最有风味</li><li>葱丝和黄瓜丝不能少</li></ul>"""
    }
}


def create_product_image(product_name: str, output_path: str) -> str:
    """为商品生成白底黑字的主图"""
    # 创建图片（白底，800x600）
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # 使用默认字体
    try:
        # macOS系统字体
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        # 回退到默认字体
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 计算居中位置
    text_bbox = draw.textbbox((0, 0), product_name, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    x = (width - text_width) / 2
    y = (height - text_height) / 2

    # 绘制商品名称（黑色）
    draw.text((x, y), product_name, fill='black', font=font)

    # 添加副标题
    subtitle = "经典川菜"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_small)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) / 2
    draw.text((subtitle_x, y + 80), subtitle, fill='gray', font=font_small)

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 保存图片
    img.save(output_path)
    print(f"  ✓ 生成图片: {output_path}")

    return output_path


def generate_product_data():
    """生成商品测试数据"""
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 查询所有商品
    cursor.execute("SELECT id, title, local_image_path FROM products WHERE status = 'ACTIVE'")
    products = cursor.fetchall()

    print(f"\n找到 {len(products)} 个商品\n")

    for product_id, title, old_image_path in products:
        print(f"处理商品: {title}")

        # 1. 生成主图
        image_filename = f"{title}.jpg"
        image_path = f"backend/public/images/products/{image_filename}"

        try:
            create_product_image(title, image_path)

            # 更新商品图片路径
            cursor.execute(
                "UPDATE products SET local_image_path = ? WHERE id = ?",
                (f"public/images/products/{image_filename}", product_id)
            )
            print(f"  ✓ 更新主图路径")
        except Exception as e:
            print(f"  ✗ 生成图片失败: {e}")

        # 2. 添加商品详情
        if title in PRODUCT_DETAILS:
            details = PRODUCT_DETAILS[title]

            try:
                # 添加故事分区
                if 'story' in details:
                    cursor.execute("""
                        INSERT INTO content_sections (product_id, section_type, title, content, display_order)
                        VALUES (?, 'story', '品牌故事', ?, 1)
                    """, (product_id, details['story']))

                # 添加食材分区
                if 'ingredients' in details:
                    cursor.execute("""
                        INSERT INTO content_sections (product_id, section_type, title, content, display_order)
                        VALUES (?, 'ingredients', '食材来源', ?, 2)
                    """, (product_id, details['ingredients']))

                # 添加制作工艺
                if 'process' in details:
                    cursor.execute("""
                        INSERT INTO content_sections (product_id, section_type, title, content, display_order)
                        VALUES (?, 'process', '制作工艺', ?, 3)
                    """, (product_id, details['process']))

                # 添加食用贴士
                if 'tips' in details:
                    cursor.execute("""
                        INSERT INTO content_sections (product_id, section_type, title, content, display_order)
                        VALUES (?, 'tips', '食用贴士', ?, 4)
                    """, (product_id, details['tips']))

                # 添加营养数据
                if 'nutrition' in details:
                    nutrition = details['nutrition']
                    cursor.execute(f"""
                        INSERT INTO nutrition_facts (product_id, serving_size, calories, protein, fat, carbohydrates, sodium)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (product_id, nutrition['serving_size'], nutrition['calories'],
                          nutrition['protein'], nutrition['fat'], nutrition['carbohydrates'],
                          nutrition['sodium']))

                conn.commit()
                print(f"  ✓ 添加详情内容（故事+食材+工艺+贴士+营养）")
            except Exception as e:
                print(f"  ✗ 添加详情失败: {e}")
                conn.rollback()
        else:
            print(f"  ! 未找到预定义详情，跳过")

        print()

    conn.close()
    print("\n✅ 所有商品测试数据生成完成！")


if __name__ == "__main__":
    generate_product_data()
