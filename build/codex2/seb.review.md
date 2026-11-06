审查范围：own-se-019～own-se-036，共18题。完整阅读 SPEC.md、seb.prompt、judge.py 和 check_own.py，逐题读取题面、全部 files（本批均为空）、搜索存档及相关正文后独立核对答案；以下位置按存档纯文本计算。搜索词栏以分号分隔三组独立查询，均按实际回放的“最多关键词命中、平局取较早记录”规则检查。

| id | 结论 | 独立求解、证据及处理原因 | 三组合理搜索词 |
| --- | --- | --- | --- |
| own-se-019 | 已修 | OEIS、AMS 摘要一致给出精确值9.80665 m/s²；补齐小数逗号、尾零及单位连写，原判据会拒绝`9.80665000 m/s²`等正确表达。 | 标准重力加速度 精确值；standard gravity exact value；NIST gravity acceleration conventional |
| own-se-020 | 已修 | NIST、IUPAC 定义均给出9,192,631,770 Hz及Cs-133；补齐数字分组、LaTeX、科学记数与核素写法，第二轮改为依赖刚查到的定义并允许复用首轮证据。 | SI second definition frequency；国际单位制 秒 定义 频率；caesium isotope SI time unit |
| own-se-021 | 已修 | BIPM、IUPAC 对指定频率的光效均给出683 lm/W；补齐`683.0`、`6.83 × 10²`及单位连写，避免将同值不同表示误判。 | 坎德拉 单色辐射 光效；candela definition luminous efficacy；540 THz SI luminous efficacy |
| own-se-022 | 已修 | NIST、IUPAC 均给出e=1.602176634×10⁻¹⁹ C，题面所问系数正确；补齐尾零、小数逗号及科学记数变体。 | 元电荷 精确值；elementary charge SI exact；charge e coulomb definition |
| own-se-023 | 已修 | NASA 任务资料及AGU报道均指向1986年天王星最近接近；补齐“一千九百八十六”及英文无连字符等合理年份表达。 | 旅行者2号 天王星 飞掠 年份；Voyager 2 Uranus closest approach year；Uranus flyby NASA date |
| own-se-024 | 已修 | JPL、LPI 摘要均支持1801年及Giuseppe Piazzi；补齐中英文年份写法，第二轮不再重复指明事件并允许沿用首轮已有的发现者资料。 | 谷神星 发现 年份；Ceres discovery date；who discovered Ceres |
| own-se-025 | 已修 | 巴黎天文台、IEC 摘要一致给出149,597,870,700米；补齐细空格、LaTeX分组、科学记数和精确的亿/万计数写法。 | 天文单位 精确 米 2012；astronomical unit definition 2012；IAU au exact metres |
| own-se-026 | 已修 | ESA摘要确认着陆目标Titan，ESA科学成果正文@1918及原始研究摘要确认放射成因氩-40；补齐卫星及核素别名，并允许第二轮复用已出现的同位素资料。 | 惠更斯 着陆 卫星；Huygens Titan radiogenic argon GCMS；ESA Titan atmosphere outgassing isotope |
| own-se-027 | 已删 | 原答案74本身正确且见于RSC、大学元素表，但题面已给W、钨、tungsten后只问固定原子序数，记忆性过强、检索考点过弱，故同时删除cases文件和对应存档，不另造替代题。 | 钨 原子序数；tungsten atomic number；W wolfram atomic number |
| own-se-028 | 已修 | NIST SRM1751证书及SP260-157均给出ITS-90镓熔点29.7646 °C，未混用旧温标29.7723 °C；补齐等值尾零及单位连写。 | NIST SRM 1751 melting point；ITS-90 镓 熔点；gallium fixed point Celsius |
| own-se-029 | 已修 | 原始命名论文、RSC及RACI摘要均支持artificial；补齐`man made`、`artificially made`、human-made等同义表达，保留自然与人工的事实区分。 | 锝 名称 词源；technetium etymology meaning；technetium Greek name origin |
| own-se-030 | 已修 | IUPAC1997最终建议给出rutherfordium，CCDC正文@8656及IUPAC摘要确认纪念Ernest Rutherford；移除只答符号`Rf`即可通过的漏洞，第二轮改为追问前轮名称并允许复用证据。 | IUPAC 1997 104 元素 命名；Names and symbols of transfermium elements 1997；rutherfordium named after physicist |
| own-se-031 | 已修 | IUCN及物种介绍均支持Ambystoma mexicanum；改为同时检查属名（或上下文明确的A.缩写）和种加词，兼容斜体、下划线、换行及不同空格，单独属名或种加词均不能通过。 | 美西螈 学名；axolotl scientific name；墨西哥钝口螈 物种 |
| own-se-032 | 已修 | OZCAM及Mammal Diversity Database均给出Ornithorhynchidae；原关键词遗漏题面直接提供的`Ornithorhynchus anatinus`查询，已用web_tool补存真实搜索，并统一题面与中英文科名判据。 | 鸭嘴兽 分类 科；platypus family taxonomy；Ornithorhynchus anatinus taxonomic classification |
| own-se-033 | 已修 | Kew首条记录明确接受Sequoiadendron giganteum，ITIS佐证且旧名标作异名；改为同时检查属名/缩写与种加词，修复下划线斜体及Unicode空格误杀。 | 巨杉 邱园 接受学名；giant sequoia Kew accepted name；Sequoiadendron POWO accepted species |
| own-se-034 | 已修 | 国新办及中科院资料支持2020雪面8848.86米、2005岩石面8844.43米；补齐数字写法，保留年份与测量口径区分，第二轮允许复用首轮搜索已给出的历史值。 | 珠穆朗玛峰 2020 雪面 高程；Mount Everest 2020 China Nepal snow height；2005 珠峰 岩石面 高程 |
| own-se-035 | 已修 | 原题即使限定Thames Head仍有来源口径差异，已限定Thames Rivers Trust具名文章的346 km，并补存真实搜索及正文（长度@2049、源头@2204），同时补齐数字写法。 | Thames Rivers Trust The Thames River Basin length；泰晤士 河流 信托 长度；Thames River Basin Trust source length |
| own-se-036 | 已修 | EPA指定表格的全湖Water Area在正文@870列82,100平方公里，区别于31,700平方英里和127,700平方公里流域面积；补齐分组、尾零及`8.21 × 10⁴`等写法。 | EPA Lake Superior water area square kilometres；苏必利尔湖 环保署 水域面积；Superior Physical Features Great Lakes EPA water area |

核验：改动前18/18题均通过原自检，说明原自检不能代替答案及判据审查；每道保留题修改后均单独运行了`python3 bank/check_own.py bank/own/cases/<id>.json`，最终仅传本批保留文件再次检查，17/17通过（参考回放通过、空回答无工具的整题回放失败）。另直接调用实际judge检查64个正确答案变体、47个错误答案反例和17个首轮完全不搜索的反例，均符合预期；保留题51组查询全部命中非空搜索结果，删除题的三组查询也已对原存档检查。五道第二轮均可利用前轮资料作答，不再要求为已获得的信息重复调用工具。

存档核验：全部保留题的答案均可从搜索标题/摘要或已存正文直接获得，未使用`answer_derived`跳过证据检查；有效答案均位于前15000字符内，正文证据已用`web_tool.py fetch --grep`核对。035补入的信托文章搜索记录在上述三组查询下均优先返回该具名来源；032补入的物种学名查询不会再返回空结果。032、035的新增存档全部由`web_tool.py search/fetch`产生，原存档记录未手改。[Thames Rivers Trust原文](https://www.thamesriverstrust.org.uk/the-thames-river-basin/)给346 km，而[奥斯纳布吕克大学存放的Twin2Go流域资料](https://www.twin2go.uni-osnabrueck.de/images/stories/CaseStudies/fact_sheet_thames.pdf)给330 km，因此035修复采用明确来源限定，没有将争议值都塞进同一答案判据。

判分边界：本批没有`output_excludes`、`expected_number`或输出长度上限，因而不存在旧值顺带提及被排除或默认40字符上限的问题；数字及短词判据保留token匹配。本批没有代码、终端脚本、受保护测试或参考修复，Debian与BSD工具差异检查不适用，也未声称运行过Debian容器或RWKV模型实测。保留题仍受共享judge的字面匹配能力限制：它不能识别否定/矛盾陈述，也不能证明一次搜索调用确实用于得出答案；精确事实仍可能被模型记住，故不应把通过率直接等同于真实检索理解能力。这里只修本批数据，没有修改共享判分器。

汇总：OK 0题，已修17题，已删1题，有风险0题；“有风险0”指未留下已定位且未处理的本批特定缺陷，上述共享判分边界仍存在。保留17题、22轮，均为外部信息-网络查询；按原标注为easy 7题、medium 7题、hard 3题，中文10题、英文7题，多轮5题。最常见的问题是正确答案的字面变体不全，其次是5道多轮题强制重复搜索；另有来源未限定导致答案不唯一、搜索关键词遗漏合理实体写法、只答符号即可过关，以及纯记忆性考点过弱。未执行git commit。
