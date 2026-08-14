# atguigu/query_process/nodes/node_rrf.py

from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.json_tool import json_tool
from atguigu.tool.logger import logger
from atguigu.tool.rerank_tool import rerank


class NodeRrf(NodeBase):
    """
    节点功能：Reciprocal Rank Fusion
    将多路召回的结果（向量、HyDE、Web）进行加权融合排序。
    """

    # 覆盖基类的 name 属性，标识节点名称
    name: str = "node_rrf"

    def process(self, state: QueryGraphState):
        """
        节点逻辑
        :param state: 工作流状态对象
        :return: 更新后的状态对象
        """
        rewritten_query = state.get("rewritten_query", "")
        rrf_chunks=state.get("rrf_chunks",'')
        web_search_docs=state.get("web_search_docs",'')
        if not rewritten_query:
            raise ValueError("rewritten_query is empty")
        if not rrf_chunks:
            raise ValueError("rrf_chunks is empty")
        if not web_search_docs:
            raise ValueError("web_search_docs is empty")
        print("rrf_chunks",rrf_chunks)
        # {
        #     "file_title": "hak180产品安全手册",
        #     "title": "## 设备",
        #     "content": "## 设备\n\n![设备需放置于平稳通风处，避免震动；搬运时双手托底，勿触危险区域；使用后断电，注意纸张边缘锋利。](http://192.168.100.88:9000/knowledge-base/upload-images/5067b2891ca4f761e2874921e0eb433aa742afbf38ca8dc509afecbf0aa6a6b5.jpg)",
        #     "item_name": "BrotherHAK180烫金机",
        #     "id": 468273558621788527,
        #     "score": 1.7101267329414707,
        #     "source": "local"
        # },
        print("merged_docs",web_search_docs)
        # {
        #     "content": "HAK180 烫金机 零售价 面议 最大15PPM烫金速度  可选7PPM烫金速度  无版烫印  配备最大44页标准ADF进纸器  支持省膜模式  10字符x2行LCD液晶屏  HAK180烫金机,凭借其高速、高品质、以及出色的细节小字烫印效果,成为定制化专属机型。可烫印90g/m²~350g/m²的A4各类型纸张,支持各类广泛的应用领域。 高效、稳定的进纸结构 配备44页标准ADF进纸器,支持90g/m²~350g/m²的各类纸张(普通纸、薄纸、再生纸、厚纸等),进纸通道结构稳定可靠,支持连续烫印。 * 350g/m²支持12页自动进纸 * 最大支持44页进纸容量(90g/m²)烫印面朝下 高速连续烫金 HAK180针对不同厚度、介质的纸张提供两种可选烫金速度。15ppm满足普通规格纸张的高效烫金需求,7ppm适合稍厚纸张的烫金。 10字符×2行LCD液晶屏 10字符×2行LCD液晶屏,2个自定义按键,操作直观,方便快捷。 产品规格  一般参数  正常工作环境(温度): 10 ~ 32 摄氏度(50 ~ 90 华氏度) 正常工作环境(相对湿度): 20 % ~ 80 % 机器尺寸: W 384.2mm×D 330.2mm×H 356.2mm 重量(含包装箱): 16.9kg 电源: 220~240 V 消费电力(烫印中): 少于340W 消费电力(待机中): 少于7W 消费电力(关机): 少于0.04W LCD液晶屏尺寸: 48.0mm×10.9mm 节省烫金膜功能: 支持(在省膜模式中“跳过”和“中间”功能, 仅适用全幅烫金膜盒) 烫印参数  最大烫印速度 (A4): 最高达15 ppm 可选烫印速度(A4): 7 ppm 视频 烫金机-HAK180-烫印速度调整-7PPM 烫金机-HAK180-安装耗材 烫金机-HAK180-更换耗材 兄弟机床公众号 数码打印机公众号 创意标签P-touch Candy",
        #     "title": "HAK180",
        #     "url": "https://www.brother.cn/hak/hak180",
        #     "source": "web"
        # },
        merged_docs = rrf_chunks + web_search_docs
        # print("merged_docs",merged_docs)
        merged_docs =[
            {
                'title': docs.get('item_name','title'),
                'content': docs.get('content',''),
                'url': docs.get('url',''),
                'source': docs.get('source','')
             } for docs in merged_docs
        ]
        texts=[docs['content'] for docs in merged_docs]
        res=rerank(texts=texts,query=rewritten_query,limit=len(merged_docs))
        # print(res)
        for r in res:
            merged_docs[r['index']]['score']=r['score']

        rrf_docs=sorted(merged_docs, key=lambda x: x['score'], reverse=True)

        # 动态 TopK：硬上限：最多取前 N 条（<=10）
        RERANK_MAX_TOPK: int = 10
        # 最小 TopK：至少保留前 N 条（>=1，且 <= RERANK_MAX_TOPK）
        RERANK_MIN_TOPK: int = 3  # 总数最少条数
        # 断崖阈值（相对）
        RERANK_GAP_RATIO: float = 0.20
        # 断崖阈值（绝对）
        RERANK_GAP_ABS: float = 0.10

        max_topk=min(RERANK_MAX_TOPK,len(rrf_docs))
        min_topk=min(RERANK_MIN_TOPK,max_topk)

        for i in range(min_topk-1, max_topk-1):
            gap=rrf_docs[i]['score']-rrf_docs[i+1]['score']
            if gap>RERANK_GAP_RATIO or gap>RERANK_GAP_ABS:
                rrf_docs=rrf_docs[:i+1]
                break

        print(json_tool(rrf_docs))
if __name__ == '__main__':
    node = NodeRrf()
    init_state = {
        "rewritten_query": "关于HAK180烫金机如何使用",
        "rrf_chunks": [
            {
                "file_title": "hak180产品安全手册",
                "title": "## 设备",
                "content": "## 设备\n\n![设备需放置于平稳通风处，避免震动；搬运时双手托底，勿触危险区域；使用后断电，注意纸张边缘锋利。](http://192.168.100.88:9000/knowledge-base/upload-images/5067b2891ca4f761e2874921e0eb433aa742afbf38ca8dc509afecbf0aa6a6b5.jpg)",
                "item_name": "BrotherHAK180烫金机",
                "id": 468273558621788527,
                "score": 1.7101267329414707,
                "source": "local"
            },
            {
                "file_title": "hak180产品安全手册",
                "title": "## 设备",
                "content": "## 设备\n\n![设备使用需注意防火、防触电，避免儿童接触塑料袋，使用后待冷却再开盖，防止烧伤。](http://192.168.100.88:9000/knowledge-base/upload-images/f3349cded08d6686a93d0a81b9a64ec1e50d9a82cbb88541b37027f085813a15.jpg)  \n儎⑟ഴḽ䆜઀ᛞ࠽व䀜᪮儎⑟Ⲻ䇴༽䜞ԬȾ",
                "item_name": "BrotherHAK180烫金机",
                "id": 468273558621788521,
                "score": 1.7088331785048168,
                "source": "local"
            },
            {
                "file_title": "hak180产品安全手册",
                "title": "## HAK 180 烫金机",
                "content": "## HAK 180 烫金机\n\n产品安全手册（简体中文）\n\n感谢您购买 HAK 180 烫金机。\n\n在使用本设备之前，请先阅读本手册，包括所有预防措施。阅读本手册后，请妥善保管。\n\n有关使用本设备的更多信息，请参阅使用说明书，其可在兄弟 (中国)商业有限公司技术服务支持网站 http://www.95105369.com/Web/Manuals.aspx 上找到。建议您先通读使用说明书，再使用本设备。\n\n如需获得常见问题解答、故障排除和说明书，请访问\n\nhttp://www.95105369.com。\n\n对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。",
                "item_name": "BrotherHAK180烫金机",
                "id": 468273558621788513,
                "score": 1.7012052545471796,
                "source": "local"
            },
            {
                "file_title": "hak180产品安全手册",
                "title": "## HAK 180 烫金机",
                "content": "## HAK 180 烫金机\n\n•\t对于保养、调整或维修事宜，请联系 Brother 呼叫中心或您当地的Brother 经销商。\n\n•\t如果本设备工作不正常或发生任何错误，请关闭本设备，拔下所有电缆，然后联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t本文档中提供的信息可能会随时更改，恕不另行通知。\n\n•\t严禁未经授权擅自复制或重制本文档的任何部分或全部内容。\n\n•\t请注意，对于使用通过本设备制作的产品造成的任何损坏或利润损失，或者故障、维修导致的数据消失或更改，或者第三方提出的任何索赔，我们不承担任何责任。",
                "item_name": "BrotherHAK180烫金机",
                "id": 468273558621788514,
                "score": 1.683707549716487,
                "source": "local"
            },
            {
                "file_title": "hak180产品安全手册",
                "title": "## 为设备选择一个安全的位置",
                "content": "## 为设备选择一个安全的位置\n\n![确保设备放置平稳，远离边缘，使用时勿将手伸入纸张边缘，搬运需双手托底，避免跌落造成伤害或损坏。](http://192.168.100.88:9000/knowledge-base/upload-images/cc5ee1ac24ebb2707d40dc7a234a8b243f55f5bf08fabc683859be6fdf096ffa.jpg)  \n确保本设备的任何部位均未伸出设备所在的桌面或支架。特别是当本设备位于桌面、支架等边缘时，请勿让出纸盒打开。确保本设备位于平整、水平且稳定的表面上，避免震动。不遵守这些预防措施可能导致设备跌落，从而导致用户的人身伤害以及设备严重损坏。",
                "item_name": "BrotherHAK180烫金机",
                "id": 468273558621788530,
                "score": 1.674561158288053,
                "source": "local"
            },
            {
                "file_title": "hak180产品安全手册",
                "title": "## 设备",
                "content": "## 设备\n\n![使用起搏器者需远离设备，注意高温部件防烫伤；设备须接220-240V交流电，禁用直流电源，防止触电或火灾。](http://192.168.100.88:9000/knowledge-base/upload-images/501bb8d2d681e4502d87badb15a68939eadfa086d309c3599f1c36b0bc559177.jpg)",
                "item_name": "BrotherHAK180烫金机",
                "id": 468273558621788522,
                "score": 1.6663713498923558,
                "source": "local"
            },
            {
                "file_title": "hak180产品安全手册",
                "title": "## 设备",
                "content": "## 设备\n\n•\t请勿拆解本设备。拆解本设备可能会导致火灾或触电。\n\n•\t请勿尝试自行维修本设备。打开或拆下盖子可能使您接触到危险电压点以及带来其他风险，并且可能使您的保修失效。对于所有维修事宜，请联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t请在以下环境使用本设备：温度保持在 10 °C 和 32 °C 之间，湿度保持在 20% 和 80% 之间，无冷凝。\n\n•\t请勿使本设备受到阳光直射、过热、接触明火、腐蚀性气体、湿气或灰尘。否则可能产生触电、短路或火灾的风险，从而导致损坏设备和/或导致设备无法运行。\n\n•\t请勿将设备放在加热器、空调、电风扇或水附近。",
                "item_name": "BrotherHAK180烫金机",
                "id": 468273558621788517,
                "score": 1.6536602097399093,
                "source": "local"
            },
            {
                "file_title": "hak180产品安全手册",
                "title": "无标题",
                "content": "![HAK 180烫金机产品安全手册，含使用前须知、安全提示及获取说明书的官方网址。](http://192.168.100.88:9000/knowledge-base/upload-images/677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg)  \nD01WD7001-00\n\nSCHN\n",
                "item_name": "BrotherHAK180烫金机",
                "id": 468273558621788512,
                "score": 1.5671407143429659,
                "source": "local"
            },
            {
                "file_title": "hak180产品安全手册",
                "title": "## 设备",
                "content": "## 设备\n\n•\t将本设备放置在平整、水平且稳定的表面上（如桌面），避免震动和冲击。\n\n•\t将本设备放置在通风良好的环境中。\n\n•\t为了防止人员受伤，请谨慎操作，避免将手指放置在图中所示的区域中。\n\n![本设备需接地使用，放置于平稳通风处，避免灰尘堆积和手指误入危险区域，搬运时用双手抓稳。](http://192.168.100.88:9000/knowledge-base/upload-images/c61a7f4e923881679f747508ae309c39dc221685344b068009256b1b3a40cc00.jpg)",
                "item_name": "BrotherHAK180烫金机",
                "id": 468273558621788526,
                "score": 1.5580205185622114,
                "source": "local"
            },
            {
                "id": 468273558621788532,
                "file_title": "hak180产品安全手册",
                "title": "## 设备",
                "content": "## 设备\n\n如果遵守了操作说明进行操作，但是设备不能正确运行，请仅调整操作说明中涵盖的控制。错误调整其他控制可能导致损坏并且通常需要合格技术进行全面工作以将本设备恢复到正常操作。Brother不建议使用 Brother 正品烫金膜盒以外的其他品牌烫金膜盒。如果使用与本设备不兼容的耗材导致损坏本设备的任何零件，由此导致的任何维修可能不在保修范围内。\n",
                "item_name": "BrotherHAK180烫金机",
                "score": 0.8346227532002464,
                "source": "local"
            }
        ],
        "web_search_docs": [
            {
                "content": "HAK180 烫金机 零售价 面议 最大15PPM烫金速度  可选7PPM烫金速度  无版烫印  配备最大44页标准ADF进纸器  支持省膜模式  10字符x2行LCD液晶屏  HAK180烫金机,凭借其高速、高品质、以及出色的细节小字烫印效果,成为定制化专属机型。可烫印90g/m²~350g/m²的A4各类型纸张,支持各类广泛的应用领域。 高效、稳定的进纸结构 配备44页标准ADF进纸器,支持90g/m²~350g/m²的各类纸张(普通纸、薄纸、再生纸、厚纸等),进纸通道结构稳定可靠,支持连续烫印。 * 350g/m²支持12页自动进纸 * 最大支持44页进纸容量(90g/m²)烫印面朝下 高速连续烫金 HAK180针对不同厚度、介质的纸张提供两种可选烫金速度。15ppm满足普通规格纸张的高效烫金需求,7ppm适合稍厚纸张的烫金。 10字符×2行LCD液晶屏 10字符×2行LCD液晶屏,2个自定义按键,操作直观,方便快捷。 产品规格  一般参数  正常工作环境(温度): 10 ~ 32 摄氏度(50 ~ 90 华氏度) 正常工作环境(相对湿度): 20 % ~ 80 % 机器尺寸: W 384.2mm×D 330.2mm×H 356.2mm 重量(含包装箱): 16.9kg 电源: 220~240 V 消费电力(烫印中): 少于340W 消费电力(待机中): 少于7W 消费电力(关机): 少于0.04W LCD液晶屏尺寸: 48.0mm×10.9mm 节省烫金膜功能: 支持(在省膜模式中“跳过”和“中间”功能, 仅适用全幅烫金膜盒) 烫印参数  最大烫印速度 (A4): 最高达15 ppm 可选烫印速度(A4): 7 ppm 视频 烫金机-HAK180-烫印速度调整-7PPM 烫金机-HAK180-安装耗材 烫金机-HAK180-更换耗材 兄弟机床公众号 数码打印机公众号 创意标签P-touch Candy",
                "title": "HAK180",
                "url": "https://www.brother.cn/hak/hak180",
                "source": "web"
            },
            {
                "content": "Brother兄弟(以下简称“兄弟”)推出的HAK180烫金机凭借其高速、高品质、以及出色的细节小字烫印效果,成为定制化专属机型,专业实力为邀请函、贺卡、请柬等个性化定制需求提供了更多的便利,最终帮助用户实现产业升级、促进文印服务往高端化发展。同时,无版烫印、支持省膜模式,大幅降低运营成本,使用效率更高,免去使用者的顾虑,为业务保驾护航。 紧凑体积,简约外观 外观方面,这款HAK180烫金机产品给人以沉稳扎实的感觉。产品颜色为黑色,磨砂的质感使得产品在使用时不易留下指纹,更具耐磨性。一体机整体观感棱角分明,但机身边角处均采用了圆润的设计,很大程度避免了用户在使用时发生不必要的磕碰。烫金机正面采用斜面设计,使得操作更加便捷舒适,摁键设置不用半蹲操作。并且外观还获得了2021年的日本GOOD DESIGN奖。 操作面板采用经济性和操作性适中的10字符*2行LCD液晶屏+按键的方式,操作直观,方便快捷。",
                "title": "高速高品质 定制化专属,兄弟HAK180烫金机让你的文印店抢占先机",
                "url": "https://new.qq.com/omn/20220713/20220713A04IN600.html",
                "source": "web"
            },
            {
                "content": "作为高端文印设备,烫金机并没有太高的“知名度”,大部分人可能从未听过,而且它售价较为昂贵,一般只会在高端文印店(或工厂)才能见到。不过,由烫金机实现的作品,相信大家都接触过,甚至是“得到过”,比如入户门上的金色福字、商务会议的邀请函、礼品店/花店的祝福贺卡、高档酒店/餐厅的菜单酒单,以及代表荣誉和认可的获奖奖状等等。 去年底,Brother在进博会发布HAK180烫金机,作为Brother旗下新品类,烫金机是其在打印机、一体机、标签机、条码机、扫描仪等之后,布局的又一办公文印设备品。作为一款主要针对高端文印店推出的产品,HAK180的问世,令烫金品在文印店中即可完成,无需再像以前跑到制作工厂去定制,简化流程提升效率;对于烫金需求方而言,也就是企业、学校、花店等,无需频繁的确认,减少了制作流程,向文印店提出需求后,在文印店中就可完成,简单的烫金需求甚至可以做到“立等可取”,一改了传统需要在“需求方,供应商,制作工厂”间频繁沟通、确认、修改的流程,HAK180让烫金流程更省时、更省力、更省沟通。那么,烫金机究竟如何工作,长相又如何,且随着笔者一同去认识这款产品! 我们先观看一段视频,了解下烫金机的用途 细分市场需求,灵巧机身,任性安置 近年来,随着文印市场逐渐呈现精细化发展趋势,高端文印的需求逐渐增加,大势之下兄弟HAK180烫金机应运而生。烫金机,顾名思义,可以简单理解为,在纸张表面烫印一层金色,当然,此“金”非彼“金”,就像上面提到的奖状、春联,只是在技术上有些特殊。 第一眼看到兄弟HAK180烫金机,如非提前知晓这是一台烫金机,可能会让人误以为是一台馈纸式扫描仪,毕竟从外观来看,兄弟HAK180烫金机与扫描仪有着相似的外观,尤其是进纸、出纸托盘的设计,都有着一定相似度。 机身顶部的进纸托盘可以存放大量用于烫印的纸张,HAK180支持多种纸张质量规格,像办公常用70g/m²的A4纸张,以及更厚更重350g/m²的A4纸张都是可以正常实现烫印的,其中90g/m²纸张可以同时存放44张,350g/m²纸张可以同时存放12张,并可实现纸张自动、连续进纸烫金(如文章起始视频所示),这得益于其采用的“多页连续烫金”技术,可以处理批量烫印任务。 兄弟HAK180烫金机还支持“无版烫金”,整个烫印过程无需提前制版。",
                "title": "无版烫金+连续烫印?论一台优秀烫金机的自我修养!兄弟HAK180烫金机评测",
                "url": "https://www.163.com/dy/article/HBO219SA05118VMB.html",
                "source": "web"
            },
            {
                "content": "Brother烫金机HAK180能为礼品袋、贺卡、邀请函等进行烫金,是打造定制礼物的得力“助手”。 烫金机HAK180采用无版烫印技术,工序流程大幅简化,商家只需先将定制化图案通过激光打印机打印好,再放入烫金机中,即可实现一键烫金。产品支持厚度在90g/m²~350g/m²的普通纸、薄纸、再生纸、厚纸等纸张类型上烫印,且支持多页连续烫金,告别一张张手送烫金的繁琐过程。此外,HAK180可以选择金色、哑金、银色、哑银、红色五种颜色,通过烫金工艺加工后的礼袋、贺卡图案清晰美观,色彩鲜艳夺目,为定制礼盒画龙点“金”。",
                "title": "浪漫满溢,Brother多款产品打造情人节定制体验",
                "url": "https://baijiahao.baidu.com/s?id=1793471814109162991&wfr=spider&for=pc",
                "source": "web"
            },
            {
                "content": "使用本 Brother 设备之前 注释说明 商标 重要注释 Brother 设备简介 使用设备前 操作面板概述 触摸式液晶显示屏概述 设置屏幕概述  导航触摸屏 访问Brother Utilities (Windows) 卸载Brother 软件和驱动程序 (Windows) Brother 设备上的 USB/以太网端口位置 纸张处理 装入纸张 将纸张装入纸盒 将A4、Letter 或 Executive 尺寸的纸张装入纸盒 #1  将A3、Ledger 或 Legal 尺寸的纸张装入纸盒 #1  将相片纸装入纸盒 #1 将信封装入纸盒 #1 将纸张装入进纸托板 非打印区域 纸张设置 更改纸张尺寸和纸张类型 更改检查纸张尺寸设置 根据任务设置默认纸盒 更改纸盒优先顺序 适用的纸张和其他打印介质 处理和使用打印介质 选择正确的打印介质 用于每项操作的纸张类型和尺寸 纸张方向和纸盒容量 通过打印机驱动程序使用用户自定义纸张 纸张重量和厚度 打印 从计算机打印 (Windows) 打印照片 (Windows) 打印文档 (Windows) 取消打印作业 (Windows) 在单张纸上打印多个页面 (N 合 1) (Windows) 打印海报 (Windows) 自动在纸张两面打印 (自动双面打印) (Windows) 自动打印成小册子 (Windows) 以灰度模式打印彩色文档 (Windows) 防止打印脏污和卡纸 (Windows) 使用预设打印配置文件 (Windows) 创建或删除打印配置文件 (Windows) 更改默认打印设置 (Windows) 打印设置 (Windows) 从计算机打印 (Mac) 打印照片 (Mac) 打印文档 (Mac) 自动在纸张两面打印 (自动双面打印) (Mac) 在单张纸上打印多个页面 (N 合 1) (Mac) 以灰度模式打印彩色文档 (Mac) 防止打印脏污和卡纸 (Mac) 打印选项 (Mac) 直接打印 USB 闪存盘中的数据 兼容的 USB 闪存盘 直接打印 USB 闪存盘中的照片 在Brother 设备上打印 USB 闪存盘中的照片",
                "title": "目录",
                "url": "https://support.brother.com/g/s/id/htmldoc/printer/hl4000dw/sch/html/sitemap.html",
                "source": "web"
            },
            {
                "content": "兄弟(中国)连续参展四年并带来全球首发新品HAK180烫金机 打印奖状激励学子们再创佳绩、举办婚宴打印自己设计的请柬、新春佳节打印专属春联……本届进博会上,兄弟中国公司带来了全球首发新品HAK180烫金机,搭载了“多页连续烫金”和“无版烫金”技术,让烫印流程大幅简化。 所谓“无版烫金”,解决了传统制版烫印工序繁琐、周期长的缺点,能够随时烫印、即烫即取。不仅如此,用户使用激光打印机在纸张上打印出想要的内容,然后放入烫金机中,就能实现一键烫印,省去繁杂的软件编辑、电脑连接过程,进一步简化了操作流程。 连续四届参展进博会,兄弟集团在现场达成了商用绣花机、打印机、标签机等多笔大额意向订单,这让董事长兼总经理尹炳新成为进博会的忠实拥趸。 “我们的个人用户销售一直做得不错,但进博会让我们打开了企业大客户和政府部门用户的市场。”尹炳新透露了第三方组织做的最新市场调研,近年来,20岁和50岁两个年龄段的用户比例大大提高,而参与进博会也让兄弟中国发现了新的商机。 首届进博会上,兄弟中国展示了众多产品及数十年来的技术创新历程;第二届进博会则重点打造400平方米的“创·艺”空间,通过产品向观众传达“匠心独运”之意;第三届进博会,兄弟中国把办公、行业、家庭、娱乐四大使用场景搬上了展台。 这个曾经以缝纫机闻名的老牌企业在中国市场不断推出新产品:激光打印机、多功能一体机、标签打印机、扫描仪、便携式打印机等,其中,印有凯蒂猫和史努比卡通形象的标签机、“马卡龙”色系的糖果趣印标签打印机等,得到了年轻女性用户的喜爱。 最新发布的烫金机配备的“省膜模式”,能够极大地节约耗材,这也传承了兄弟公司一贯秉持的绿色环保理念。从2006年起,兄弟中国在上海和北京公司的办公楼附近都认领了大型公园;2012年起,兄弟中国持续组织志愿者前往内蒙古阿拉善,与牧民共同防沙植树,并协助种植与开发经济作物肉苁蓉,助力阿拉善的荒漠化防治。",
                "title": "无版“一键烫金”:省事省时省成本",
                "url": "http://baijiahao.baidu.com/s?id=1715921686026370255&wfr=spider&for=pc",
                "source": "web"
            },
            {
                "content": "说明书 使用说明书 标题说明发布日期 (版本)文件 (大小) 使用说明书 有关产品的基本信息。 2021-10-11 (04)下载 (5.75MB) 重要事项—网络安全说明: 网络实用程序的默认登陆密码信息 2022-12-05 (04)下载 (0.34MB) 快速向导 标题说明发布日期 (版本)文件 (大小) 快速设置指导手册 有关产品安装。 2021-07-29 (02)下载 (0.59MB) 快速设置指导手册 (Touch Panel Display) 此说明书对触摸屏显示器进行了简要说明。 2016-09-14 (01)下载 (1.80MB) 软件向导 标题说明发布日期 (版本)文件 (大小) 使用说明书(BRAdmin Professional 4) 有关BRAdmin Professional 4 的更多信息。 2026-02-12 (06)下载 (1.39MB) 使用说明书(BRAdmin Professional 4 for Microsoft Azure) 有关Microsoft Azure 的BRAdmin Professional 4 的更多信息。 2023-05-30 (02)下载 (0.68MB) 其他 标题说明发布日期 (版本)文件 (大小) 产品安全指南 介绍有关安全和正确操作的信息。 2023-09-06 (03)下载 (1.72MB) 开放源代码许可备注 (英文) 这是Brother所提供开源内容的解释说明。 2016-07-01 (1.00)下载 (0.03MB) 用户指南(条形码扫描枪 PA-BR-001) (英文) 有关选配件条形码扫描枪的基本信息。 2016-05-09 (01)下载",
                "title": "说明书",
                "url": "https://support.brother.com/g/b/manualtop.aspx?c=cn&lang=zh&prod=p950nwcheas",
                "source": "web"
            },
            {
                "content": "Contact Us Product Registration Visit www.brother.com.sg 106 Results 1 Basic operations and sewing [Video instructions]  2 Various sewing and application [Video instructions]  3 How to adjust the thread tension  4 How to use the foot controller with the machine  5 Combination of fabric, thread and needle 6 The stitch is not sewn correctly 7 How do I wind the bobbin?  8 Tips for sewing thin fabrics  9 How do I sew with the twin needle? For better results when sewing stretch fabrics Tips for sewing an even seam allowance  The bobbin thread cannot be pulled up.  Basic procedure to sew stitches  Tips for sewing thick fabrics  Winding and Installing the Bobbin [Video instructions]  How to use the Narrow Zipper Foot. (Optional accessory : SA208/F079) [Video instructions]",
                "title": "FAQs & Troubleshooting",
                "url": "https://support.brother.com/g/b/faqlist.aspx?c=sg&lang=en&prod=hf_inova80eas&tabid=2",
                "source": "web"
            },
            {
                "content": "基本性能 搭载新的28把刀库,促进了大型工件的工序集约。 此外,工作台最大载重500kg,Z轴移动量扩大, 因此可广泛应用于多种生产体制。 加工范围 28把刀库、最大载重500kg、Z轴移动量扩大 从大型工件到多品种少批量生产的应对能力得到进一步提升 对应大型工件以外,可以加工多个小型工件, 也可以放置多种夹具实现多品种小批量的生产。 宽敞的加工区域,满足不断变化的工厂需求, 助力提升工厂的柔性化生产能力。  Z轴移动量扩大  Z轴移动量的扩大,工作台面到主轴端面的距离向上向下扩展,实现了Z轴方向更大的加工区域,并且提升了刀具的可达性。 Z轴移动量 300mm  380mm  从工作台面到主轴端面的距离  180mm～480mm  150mm～530mm  工作台载重增加  工作台最大载重增加至500kg。扩大了夹具的选择范围,可实现工序集约和灵活的夹具设计。  最大载重 500kg * * 需要变更参数设定。  可搭载大型摇篮式夹具  根据用途,备有150、250、350mm的高立柱。可搭载回转直径540mm的摇篮式夹具,实现大型部件的多面加工。  搭载28把刀库  除14把、21把规格以外,还可搭载保留高速换刀功能的圆盘式28把刀库。进一步的应对大型工件的完整加工和多品种少量加工等。  最大刀具重量 4kg  生产效率 通过机电一体化开发 优化机床控制,减少时间浪费  依托BT30机床轻巧、低惯性的特点和本公司开发的NC装置, 发挥Brother机床的最大性能,实现高生产效率。  无停顿ATC  通过主轴启动/停止、Z轴升降、刀库动作的高速化/优化,实现高速刀具更换。可以最短时间更换最大3kg的刀具,更换最大4kg的重型刀具也只略微增加换刀时间。  14/21把刀库 (标准刀具) Chip-Chip 1.3s / Tool-Tool 0.6s 28把刀库 (标准刀具) Chip-Chip 1.4s / Tool-Tool 0.7s 28把刀库 (重刀具) Chip-Chip 1.4s / Tool-Tool 0.8s  同步动作控制  在换刀的同时进行XY轴、附加轴的定位,减少了非切削时间。  高加减速主轴  低惯性主轴、高加减速主轴马达实现了主轴启动/停止的高速化。  主轴启动/停止时间 0.15s 以下 * * 高扭矩规格  优化加速度设定 XY轴  利用XY轴的优化加速度设定功能,可根据工作台载重实现优化的加速度设定。   加工能力",
                "title": "基本性能",
                "url": "https://www.brother.cn/machinetool/w1000zd2/feature/index",
                "source": "web"
            },
            {
                "content": "手动进纸 如果想从手动进纸槽进行打印,请转到情况 A: 从手动进纸槽打印. 如果不想从手动进纸槽进行打印,请转到情况 B: 从纸盒(纸盒1)打印. 情况A: 从手动进纸槽进行打印. 展开纸张支撑翼板以防止纸张从出纸托板中滑落,或者出纸后立即取走打印出的纸张。 请执行以下操作中的一项: 如果您的设备没有手动进纸槽盖,请转到步骤3. 如果您的设备有手动进纸槽盖,请打开手动进纸槽盖。 用双手滑动手动进纸槽的纸张导块,调整至所用纸张的宽度。 用双手将一张纸放入手动进纸槽,直至纸张的前缘触碰到进纸辊。 当感觉到设备进纸时请松开双手。将纸张以打印面向上的方式放入手动进纸槽。 设备将吸住纸张直至您发送打印数据到设备。 将打印数据发送至设备前,请执行以下操作: 在标签上打印时: 打开后盖 (面朝上后出纸托板)。 在信封上打印时: 打开后盖 (面朝上后出纸托板),按下后盖内的两侧绿色锁定杆 。点击这里查看详情. 将打印出文档。如果仍出现错误信息,请转到步骤7. 放入手动进纸槽中的纸张尺寸可能与您在打印驱动中所选的纸张尺寸略有不同。请检查纸张尺寸。点击这里查看如何检查或更改纸张尺寸的详细信息. 如果想从手动进纸槽进纸并在标签或信封上打印,点击这里查看如何在标签和信封上打印的详细信息. 确保您所使用的纸张符合Brother推荐的纸张规格。点击这里查看推荐纸张的详细信息.点击这里查看您可使用的纸张类型. 装入与当前驱动设置相同尺寸的纸张。 将打印出文档。如果您想更改纸张来源,请转到情况 B中的步骤2. 情况B: 从纸盒(纸盒1)进行打印. 取消打印作业。 按下Go键4秒左右直到LED指示灯亮起,松开此键。 再次按下Go键。当取消打印作业时Ready和ErrorLED指示灯将闪烁。 确保手动进纸槽中未放置纸张。 若在手动进纸槽中放置纸张,即使在打印机驱动程序中选择了其他纸张来源,文档也将从手动进纸槽进行打印。 请执行以下操作中的一项: 如果您仅想为下一次打印临时更改设置,请转到选项 1. 如果您想为所有打印作业更改默认纸张来源(纸盒),请转到选项 2. 选项1: 仅下一次打印临时更改设置 Windows 用户/Macintosh用户 Windows 用户: 注: 由于操作系统不同,操作步骤及屏幕显示可能也不同。 从您使用的应用程序选择打印菜单。 (使用的应用程序不同,有关选择打印菜单的步骤也不同.) 点击属性. 点击基本(Basic)选项卡并从纸张来源(Paper Source)下拉列表中选择纸盒1(Tray1). 点击确定(OK)将打印数据发送至设备。",
                "title": "手动进纸",
                "url": "https://support.brother.com/g/b/faqendbranchprintable.aspx?c=cn&lang=zh&prod=hl2250dn_eu_as&faqid=faq00002216_001&printable=true",
                "source": "web"
            }
        ]
    }
    result = node(init_state)
    logger.info(json_tool(result))