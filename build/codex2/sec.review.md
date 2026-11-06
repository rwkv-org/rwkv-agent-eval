# own-se-037—own-se-054 审查报告

已完整阅读 `bank/own/SPEC.md`、`build/codex2/sec.prompt`，逐题阅读全部题面、判据、参考回复、搜索存档，并用存档证据独立核对答案；同时检查了 `bank/judge.py`、`bank/check_own.py` 和搜索回放的实际选路规则。下表结论按最终状态互斥计数，“有风险”题也已修复发现的具体别名或搜索问题。

搜索验证中的 S0/S1/S2 是该题存档内从零开始的搜索条目序号，按实际回放规则计算命中数并处理平局。保留题使用修后存档，删除题使用审前存档；每题列出三条中英文候选查询。以下事实均以存档为依据，来源链接用于追溯。

| id | 结论 | 独立核对与处理原因 | 三条模拟查询及回放结果 |
| --- | --- | --- | --- |
| own-se-037 | 已修 | [大英博物馆](https://www.britishmuseum.org/collection/egypt/explore-rosetta-stone)及其他摘要均确认法国士兵于 **1799** 年重新发现石碑，补齐 `seventeen hundred…`、`one thousand seven hundred…` 等正确年份写法。 | `罗塞塔石碑 重新发现 年份` → S0；`Rosetta Stone discovery year French soldiers` → S0；`罗塞塔石碑 法国 发现` → S0。 |
| own-se-038 | 已修 | [WorldCat 原版书目](https://search.worldcat.org/zh-cn/title/Sketch-of-the-Analytical-Engine-invented-by-Charles-Babbage-...-with-notes-by-the-translator.-Extracted-from-the-'Scientific-Memoirs-'-etc/oclc/1063166722)与 BnF、研究摘要均支持 **1843** 年，补齐 `eighteen hundred…`、`one thousand eight hundred…` 等年份写法。 | `Ada Lovelace notes publication year` → S0；`洛夫莱斯 分析机 笔记 出版` → S0；`Analytical Engine notes Ada published` → S0。 |
| own-se-039 | 已修 | [UNESCO ICDH](https://www.unescoicdh.org/eng/sub.php?menukey=289&mod=view&no=121346&search=4&listCnt=10&code1=00000004&code2=00000075)和吉尼斯摘要均确认船长为 **Juan Sebastián Elcano**，补存 Victoria／维多利亚／維多利亞搜索入口并接受 `El Cano`、`del Cano` 等名字写法。 | `麦哲伦 维多利亚号 1522 返航 船长` → S1；`Victoria captain returned Spain 1522` → S1（原为空）；`Magellan expedition circumnavigation captain` → S0。 |
| own-se-040 | 已修 | 诺贝尔官网确认第一次为 **1903** 年物理学奖、第二次为 **1911** 年化学奖，首轮摘要已包含两个年份，故取消追问强制重复搜索并补齐英文长写及 `一九○三`。 | `居里夫人 第一次 诺贝尔奖 年份` → S0；`Marie Curie second Nobel award year` → S2；`居里 第二次 获奖` → S2。 |
| own-se-041 | OK | [BBC 搜索存档](https://www.bbc.co.uk/programmes/p0btb364)与沉船研究摘要共同确认 **Weddell Sea／威德尔海**，现有英中海名写法及搜索入口足以完成题目。 | `Endurance sank 1915 sea` → S0；`沙克尔顿 坚忍号 沉没 海域` → S0；`Shackleton ship sinking where` → S0。 |
| own-se-042 | 已删 | [央视年表](https://big5.cctv.com/gate/big5/www.cctv.com/history/special/C14156/20050614/101227.shtml)支持 **1433−1407＝26 年**，但实测错答“相差一百二十六年”可命中“二十六”而通过，当前判据无法兼顾自由中文数词短答与防误放，故删除 case 和存档。 | `郑和 首航 第七次 回国 年份` → S0；`Zheng He first seventh voyages return years` → S0；`郑和 第一次 第七次 返国` → S0。 |
| own-se-043 | 有风险 | 出版物、图书馆及研究摘要均支持作者 **Mary Shelley**，已补倒置书目名 `Shelley, Mary` 和婚前姓名等写法，但作者身份属于常见文学知识，仍可能凭记忆回答后用任意搜索调用满足工具判据。 | `Frankenstein author 1818` → S0；`科学怪人 作者` → S1；`Who wrote The Modern Prometheus Frankenstein` → S0。 |
| own-se-044 | 已修 | [中国作家网](http://www.chinawriter.com.cn/n1/2017/1212/c403994-29700404.html)、光明日报及书目摘要均支持原作首版 **1967** 年，补齐英文完整基数词年份写法。 | `百年孤独 首次出版 年份` → S0；`One Hundred Years of Solitude original publication` → S0；`García Márquez Cien años first published` → S0。 |
| own-se-045 | 已修 | 剧本及[馆藏说明](https://researchworks.oclc.org/archivegrid/collection/data/970006364)确认法语舞台首演 **1953**、伦敦英语首演 **1955**，已明确舞台演出、补年份写法、允许来源复用，并补录“英文”入口避免中文追问平局选中法语资料。 | `Waiting for Godot original French premiere year` → S0；`等待戈多 英文首演 年份` → S2（原错误选 S0）；`Godot first English production London` → S1。 |
| own-se-046 | 有风险 | [戛纳官网](https://www.festival-cannes.com/en/p/kaige-chen/)与 BnF 目录确认导演 **陈凯歌／Chen Kaige**，已接受目录中的 `Chen, Kaige` 等写法，但这是常见导演知识，调用过搜索不足以证明利用了搜索内容。 | `霸王别姬 导演` → S0；`Farewell My Concubine director` → S0；`1993 Concubine filmmaker` → S0。 |
| own-se-047 | 已修 | [格什温官网](https://gershwin.com/publications/rhapsody-in-blue/)与国会图书馆确认 **1924** 年首演且钢琴独奏为 **George Gershwin 本人**，去除首轮姓名提示、允许复用资料、保留追问要求姓名，并补存官方正文和年份写法。 | `蓝色狂想曲 首演 年份` → S0；`Rhapsody in Blue first performance year` → S0；`Rhapsody in Blue premiere piano soloist` → S0。 |
| own-se-048 | 有风险 | 出版物介绍及[馆藏目录](https://www.loc.gov/resource/asianscd.2004551302v27/?sp=6)支持通用署名 **Murasaki Shikibu／紫式部**，已补 `源氏物語` 和中文“作者”搜索入口，但作者身份常见且无需串联信息，仍有记忆作答风险。 | `源氏物语 作者` → S1；`The Tale of Genji author` → S0；`源氏物語 作者` → S1（原为空）。 |
| own-se-049 | 已修 | [世界田联](https://worldathletics.org/competitions/world-athletics-championships/world-athletics-championships-oregon-2022-7137279/news/news/abebe-bikila-1960-olympic-marathon-victory)与 IOC 摘要均确认 **Abebe Bikila／阿贝贝·比基拉**，补录 marathon／马拉松／赤脚等不依赖已知答案姓名的搜索入口。 | `1960 罗马 赤脚 马拉松 冠军` → S1；`1960 Olympics barefoot marathon winner` → S1；`赤脚 马拉松 奥运会 冠军` → S1（原为空）。 |
| own-se-050 | 已修 | [世界田联](https://worldathletics.org/news/news/el-guerroujs-patience-pays-off)和 BBC 资料确认 **Hicham El Guerrouj** 与前辈 **Paavo Nurmi**，首轮结果已提供后者，故允许追问复用来源，并去掉第二轮独立给出的年份、国籍和项目线索以加强上下文依赖。 | `2004 Athens 1500m 5000m champion` → S0；`雅典 2004 中长跑 双冠` → S0；`previous Olympic 1500m 5000m double Finnish runner` → S1。 |
| own-se-051 | 已修 | IOC 赛果及[央视资料](http://news.cctv.com/china/20070803/113409.shtml)均确认金牌为 **陈静／Jing Chen**，补录“首尔／首爾／漢城”等搜索入口并取得官方赛果摘要。 | `1988 汉城 乒乓球 女单 冠军` → S0；`1988 Seoul Olympics table tennis women gold` → S0；`1988 首尔 奥运会 女子单打 金牌` → S1（原为空）。 |
| own-se-052 | 已删 | 南非橄榄球官方资料支持 1995 决赛 **15–12**、2019 决赛 **32–12**，故净胜分之差为 **17**，但错答“一百一十七分”仍命中“十七”并通过，故删除 case 和存档。 | `1995 Rugby World Cup final score` → S0；`2019 South Africa England rugby final result` → S1；`南非 橄榄球 1995 2019 决赛 比分` → S0（需再查 2019）。 |
| own-se-053 | 已删 | [IOC 资料](https://www.olympics.com/en/news/this-week-in-olympic-history-july-15-21-nadia-comaneci-scores-the-first-perfect-10-in-gymnastics)确认首次满分为 **高低杠**、全届共 **7 次**，原吉尼斯摘要的“further seven”另有矛盾，且即使统一 IOC 来源后错答“十七次”仍可通过，故删除 case 和存档。 | `科马内奇 1976 首个满分 项目` → 原 S1；`Nadia Comaneci 1976 perfect tens total` → 原 S0；`1976 奥运会 体操 首个10分` → 原为空（前两条命中）。 |
| own-se-054 | 已删 | [世界田联](https://worldathletics.org/news/news/stunning-rudisha-14091-world-record-in-london)和 ABC 支持 **1:41.01−1:40.91＝0.10 秒**，但在补充数值写法后，错答“缩短了零点一五秒”仍可命中“零点一”并通过，故删除 case 和存档。 | `鲁迪沙 2012 800米 新旧纪录` → S0；`David Rudisha 2012 previous world record` → S0；`London 2012 800 world record improvement` → S0。 |

保留题的每轮关键答案均在搜索摘要中可读到，至少有一条证据位于所用结果列表的前三条，相关事实均在前约 15000 字符范围内；未强制 `web_fetch`。047 新增官方正文同时给出首演年和独奏者，`web_tool.py fetch --grep` 报告的行起点为 **@553**。045 的存档对首演具体日有不同说法，但年份均为 1953，题目只问舞台首演年份。

四道删题的核心原因是 `judge.contains_token` 把汉字排除在词界之外：完整词模式仍把较大中文数字中的子串当成答案。轮判据没有正则或自定义解析入口；`expected_number` 与 `output_contains_any` 同时设置是 AND，无法表达“阿拉伯数字正确或中文数词正确”，且前者不解析中文。改成仅收阿拉伯数字或精确整句会误杀合理写法，排除特定错数又会误伤含纠错说明的正确长答，因此在不修改本批以外文件的范围内删除了这四题。

所有题的初始 `files` 和整题文件判据均为空，均无代码修复、Shell 脚本、受保护测试或本地文件产物，Debian／BSD 工具差异和参考代码修复检查不适用；所有轮判据均未使用 `output_excludes` 或 `expected_number`，没有旧值顺带提及误伤或默认 40 字符限长问题。保留题首轮仍要求 `web_search`；五道原多轮题均检查过上下文关系，其中保留的四道已允许复用先前资料。

验证结果：原始 **18/18** 通过自检；每道修改题均单独重跑 `python3 bank/check_own.py bank/own/cases/<id>.json` 通过；删除后又仅传入本批保留文件，结果 **14/14** 通过。额外直接调用实际判分函数，**21 个正确写法全部通过、18 个典型错答全部被拒绝、14 个首轮正确答案在无工具时全部被拒绝**；按真实选路算法验证的 **42 条保留题搜索词全部命中**，并确认 045 的中英文追问进入正确资料。未实际运行 RWKV 7B；三道常识题的风险是题材与规则能力的判断，不能视为已测得模型会背答案。

最终汇总：**OK 1 道、已修 10 道、已删 4 道、有风险 3 道，共 18 道**；保留 **14 道**，删除 **042、052、053、054** 的 cases 与 web-archive 文件。保留题为 **8 easy、6 medium、0 hard**，**8 中文、6 英文、4 道双轮**，本批的 hard 覆盖因此空缺；本次按审查范围没有补造替代题。最常见的问题是答案别名和年份数字写法遗漏，其次是多轮强制重复搜索、搜索匹配关键词漏掉自然查询，以及中文短数字判据误放；常见作者／导演知识仍有记忆作答风险。仅修改或删除本批题目、对应存档，并新增本报告，未 git commit。
