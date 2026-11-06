# own-se-073—own-se-090 审查报告

逐题阅读了 `bank/own/SPEC.md`、`build/codex2/see.prompt`、18份完整题目JSON、各题搜索结果的相关事实段落，并核对 `bank/judge.py`、`bank/check_own.py` 与搜索回放实现。原始18题均无本地资料文件、无受保护测试；本批没有代码修复题或Shell脚本题。未发现需要更正的事实答案，也未发现与仓库其他自造题重复的同一事实。

每题均真实补抓了至少一个原有搜索结果中的主要来源页面，修复“摘要能答，但合理继续web_fetch会404”的覆盖缺口；网页存档全部由 `bank/web_tool.py` 写入。共新增20个页面和1条真实搜索，没有手写网页或摘要。表中@N为新增页面纯文本中答案字串的位置；每题三条查询均按实际回放的“命中关键词数最多、同分取最早存档”规则验证，54/54可命中，且所需事实在所选结果正文前15000字符内。

| id | 结论 | 独立答案与一句话原因 | 存档正文证据（@N） | 三个合理查询（均已验证回放命中） |
|---|---|---|---|---|
| own-se-073 | 已修 | 独立核对为2011年；补《光明日报》开通报道正文，并为原先零命中的“北京上海高速铁路”真实补搜、增加实体匹配词。 | [2011 @25](https://epaper.gmw.cn/gmrb/html/2011-07/01/nw.D110000gmrb_20110701_7-01.htm) | `京沪高铁 正式开通 年份`；`Beijing Shanghai high speed rail opening year`；`北京上海高速铁路 何时运营` |
| own-se-074 | 已修 | 独立核对为TFU；补IATA官方代码检索正文，保留三字码完整词匹配，避免混入成都双流的CTU。 | [TFU @6065](https://www.iata.org/en/publications/directories/code-search/?airport.search=Chengdu%20Tianfu%20International%20Airport) | `成都天府机场 三字码`；`Chengdu Tianfu IATA code`；`天府国际机场 机场代码` |
| own-se-075 | 已修 | 独立核对为2018-12-25；补新华社正文及25 Dec 2018、25/12/2018等合理日期写法。 | [2018-12-25 @315](http://www.xinhuanet.com/politics/2018-12/25/c_1123903550.htm) | `杭黄高铁 开通日期`；`Hangzhou Huangshan railway opening date`；`Hanghuang high speed rail started service` |
| own-se-076 | 已修 | 独立核对为ICAO ZPPP、IATA KMG；补Navigraph两种代码正文，后轮允许直接复用前轮同时出现的KMG，取消重复搜索硬门槛。 | [ZPPP @0](https://navigraph.com/airport/ZPPP/Kunming-Changshui)；[KMG @3342](https://navigraph.com/airport/ZPPP/Kunming-Changshui) | `昆明长水机场 ICAO`；`Kunming Changshui airport code`；`长水机场 IATA 三字码` |
| own-se-077 | 已修 | 独立核对为全线2015、东段2010、相差5年；补新华社正文，后轮复用证据并以JSON检查三个数值，堵住“五十年”“十五年”也通过的漏洞。 | [2010 @227](https://www.gov.cn/xinwen/2015-12/30/content_5029633.htm)；[2015 @90](https://www.gov.cn/xinwen/2015-12/30/content_5029633.htm) | `海南环岛高铁 全线开通 年份`；`Hainan island high speed railway opening`；`海南东环高铁 开通时间` |
| own-se-078 | 已修 | 独立核对为陈嘉庚／Tan Kah Kee；补厦大官网学校简介正文，中英姓名及繁体写法已有覆盖，未发现创办人争议。 | [陈嘉庚 @1044](https://www.xmu.edu.cn/sdgl/xxjj.htm) | `厦门大学 谁创办`；`Xiamen University founder`；`XMU founded by whom` |
| own-se-079 | 已修 | 独立核对为1896年；补交大校史正文并明确按设立校史口径，排除把1897年首批开课误作创办年份的理解。 | [1896 @122](https://guobao.sjtu.edu.cn/?page_id=2) | `南洋公学 创办年份`；`Nanyang Public School founding year`；`Shanghai Jiao Tong predecessor history` |
| own-se-080 | 已修 | 独立核对为1909年；补教育部核准的兰大章程正文，所问甘肃法政学堂溯源口径清楚。 | [1909 @856](https://hudong.moe.gov.cn/srcsite/A02/zfs_gdxxzc/201408/t20140814_182107.html) | `兰州大学 始建年份`；`Lanzhou University founded year`；`LZU Gansu law school history` |
| own-se-081 | 已修 | 独立核对为西湖高等研究院、成立大会2016、大学获批2018、相差2年；补研究院与大学机构介绍，后轮复用证据并用JSON数值检查，排除2015注册日期及“十二年”等误通过。 | [Westlake Institute for Advanced Study @230](https://www.wias.org.cn/english/ABOUTUS/wap_71.shtml)；[2016 @484](https://www.nature.com/naturecareers/employer/327c90aa-265c-4cf5-b478-66e91504a239/westlake-university)；[2018 @506](https://www.nature.com/naturecareers/employer/327c90aa-265c-4cf5-b478-66e91504a239/westlake-university) | `Westlake University predecessor institute`；`西湖高等研究院 成立大会 年份`；`WIAS inauguration year Westlake approval` |
| own-se-082 | 已修 | 独立核对为2010年；补小米官方投资者关系正文，明确公司成立年，与2018上市年有区分。 | [2010 @107](https://ir.mi.com/zh-hant) | `小米公司 成立年份 官方`；`Xiaomi founded year official`；`小米 创立 时间` |
| own-se-083 | 已修 | 独立核对为深圳；补新华社报道中“在深圳创立大疆”的正文，区别香港求学经历并补Shēnzhèn等转写。 | [深圳 @327](https://www.news.cn/politics/2015-05/24/c_127834386.htm) | `DJI founded city`；`大疆 创办地点`；`DJI history founded Shenzhen` |
| own-se-084 | 已修 | 独立核对为辛弃疾／Xin Qiji；补搜索结果里的百科正文，名称所出《青玉案·元夕》及作者一致，原有中英繁体姓名写法可用。 | [辛棄疾 @4793](https://zh.m.wikipedia.org/zh-hk/%E7%99%BE%E5%BA%A6) | `百度 名称来源 宋词作者`；`Baidu name origin poet`；`百度 名字 出处` |
| own-se-085 | 已修 | 独立核对为90度；补中国气象局夏至正文，改为JSON数值校验，使90.000可通过而95无法靠“九十”子串混过。 | [90 @53](https://www.cma.gov.cn/ztbd/2025zt/24jq/xiazhi/index.html) | `夏至 太阳黄经 多少度`；`Xiazhi solar longitude`；`Chinese summer solstice ecliptic longitude` |
| own-se-086 | 已修 | 独立核对为24小时累计50毫米；补中国气象局正文，改用JSON同时校验小时数与毫米下限，堵住“五十六毫米”误通过并接受50.000等价数值。 | [50 @288](https://www.cma.gov.cn/kppd/qxkppdqxcd/201301/t20130109_201593.html) | `暴雨 24小时 下限 毫米`；`rainstorm 24 hour rainfall threshold China`；`中国气象局 暴雨等级` |
| own-se-087 | 已修 | 独立核对为3月23日；补国家气象信息中心关于每年固定纪念日的正文，区分活动启动日并补23 Mar.、March twenty-third等写法。 | [3月23 @1001](https://data.cma.cn/cmaOld/site/article/id/28955.html) | `世界气象日 日期`；`World Meteorological Day date`；`WMO meteorological day when` |
| own-se-088 | 已修 | 独立核对为1936年；国家图书馆书目、知网和出版史报道一致，补《光明日报》初版史正文。 | [1936 @150](https://epaper.gmw.cn/gmrb/html/2016-12/30/nw.D110000gmrb_20161230_1-10.htm) | `辞海 初版 哪年`；`Cihai first publication year`；`辭海 中華書局 初版年份` |
| own-se-089 | 已修 | 独立核对为天文学卷、1980年；补人民日报经央视刊发的出版史正文，后轮允许复用首轮已经提供的年份。 | [天文学 @455](http://news.cctv.com/2019/10/26/ARTIiWUofGiuhL0V4LzHgcRC191026.shtml)；[1980 @629](http://news.cctv.com/2019/10/26/ARTIiWUofGiuhL0V4LzHgcRC191026.shtml) | `中国大百科全书 第一版 最先出版卷`；`Encyclopedia of China first volume subject`；`天文学 中国大百科全书 出版年` |
| own-se-090 | 已修 | 独立核对为正式第1版1978、第7版2016、相差38年；补出版社图书页及其出版史文章，后轮复用证据并用JSON验证原始年份与差值，排除试印本、再印年及“三十八点五年”误过。 | [1978 @722](https://www.sohu.com/a/581983643_228930)；[2016 @361](https://www.cp.com.cn/book/6afc8cd8-c.html) | `现代汉语词典 第一版 出版年`；`Contemporary Chinese Dictionary seventh edition year`；`现代汉语词典 第7版 商务印书馆` |

汇总：**OK 0、已修18、已删0、有风险0，共18题，全部保留。**其中11题修改了cases内容，7题只补主要来源页面；18份存档均有补充。难度与批次标记不变：easy 8、medium 7、hard 3；中文11、英文7；两轮5题。

本批最常见的问题：

- 18/18题原先只有搜索摘要，没有任何可供继续抓取的存档正文；现已补齐主要来源，未声称搜索结果中每一个旁支链接均已存档。所有用于作答的来源均返回2xx，答案位置均小于15000。
- 5道多轮题原先强制后轮再次搜索，而首轮结果已经包含后轮事实；现允许复用证据，仍保留对前轮机场、卷名或已确认年份的依赖。
- 5题的短汉字数字会被包含匹配误放行；例如077的“五”命中“十五年”，081的“二”命中“十二年”，086的“五十”命中“五十六毫米”。同时90.000、50.000原先会因数字完整词匹配被拒。为不修改公共判分器，也不靠排除词误伤解释，本次将077、081、085、086、090的同一事实改为写入明确的JSON数值字段，以受保护Python程序按值校验。077、081、090继续同时验证两个原始年份和差值；没有把原题替换成新的事实问题。
- 日期别名仍有遗漏；075、087已增加实际复现的合理中英日期写法。079额外区分创办与首次开课，防止两种合理时间口径混用。

验证记录：

- 每道修改后均运行了 `python3 bank/check_own.py bank/own/cases/<id>.json`，最后仅传本批18个cases批量执行：**18/18通过**；参考轨迹通过、空答且不调用工具或修改文件的轨迹不通过。
- 在本机以及实际 `python:3.12-slim` Debian容器（Python 3.12.16，`--network none --read-only --tmpfs /tmp`）均运行本批自检及附加验证：各自**165项通过**，包括54条搜索回放、102项数值文件及受保护检查验证、9条日期答案变体。
- 102项数值验证覆盖JSON紧凑/缩进/键序变化、额外元数据字段、整数与等价浮点数；拒绝缺失文件、坏JSON、错误原始年份/差值/时段/下限、负值、字符串、布尔值、null和小数偏差，并验证篡改本地检查文件也无法放过错误答案。JSON字段与单位已在题面明示，未对最终自然语言回复设格式或40字符限制。
- 新增保护程序只用Python标准库json/math/sys/pathlib，不调用BSD/GNU命令，不依赖git、jq、curl、gawk或本机路径；Debian实跑已覆盖其实际判分行为。
- 所有保留的自然语言数字/短词判据仍启用完整词选项；没有新增output_excludes，没有expected_number的默认40字符长度限制。新数值字段的预期答案仅存于判据参数，题面和可读保护程序不含预填答案。

测量边界：本批要求本来就包含常识类事实，部分答案（如夏至角度、厦大创办人）可能来自模型已有知识；规则只能证明按要求调用过web_search，无法证明模型确实使用了那次搜索的证据。保留的文字包含判据也无法完全理解否定、矛盾陈述或“列举一串候选答案”。这些是当前公共规则判分的共同限制，不能把18/18自检通过解释为已排除所有语义投机；本次已修复可具体复现的短数字误过、日期误杀和重复工具门槛。

范围：只改本批cases、对应web-archive及本报告；未修改公共判分器、工具脚本或其他批次文件，未git commit。

最终汇总：**OK 0 / 已修18 / 已删0 / 有风险0**；最常见的是主要来源页面缺档，其次为短数字匹配漏洞、多轮重复搜索门槛及日期写法遗漏。公共规则无法证明证据被使用的测量边界见上文。
