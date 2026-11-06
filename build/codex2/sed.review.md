# own-se-055～own-se-072 审查报告

已完整阅读 `bank/own/SPEC.md`、`build/codex2/sed.prompt`，逐题阅读全部题面、判据、reference、files 和搜索存档，并核对已有页面正文；本批初始 files 均为空，没有代码修复、终端脚本或受保护测试。以下答案由存档中的正式标题、发布记录、组织历史或联系地址独立核对，没有发现需要纠正的事实答案或无法成立的题目。

`@N` 为 `web_tool.py fetch --grep` 显示的存档正文位置；未列正文位置的答案可直接从搜索结果标题或摘要取得。每题另用三个合理的中英文查询模拟回放匹配，修订后 54/54 命中；表中保留实际查询，查询时不使用已知答案编号或年份。

| id | 结论 | 一句话原因 | 三个搜索回放探针（均命中） |
|---|---|---|---|
| own-se-055 | 已修 | IEC 等存档一致指向 ISO/IEC 20000-1；补充分册写法、千位分隔和常用横线，修复正确回答“20000 第1部分”等被误杀的问题。 | ISO IEC service management system requirements 2018 standard；服务管理体系要求 2018 标准编号；Information technology Service management Part 1 ISO |
| own-se-056 | 已修 | ISO 报告与认可机构资料一致指向 ISO/IEC 17025；补充“一七〇二五／一七零二五”等中文数字写法。 | testing calibration laboratories competence 2017 standard；检测校准实验室通用要求 标准号；ISO IEC laboratory competence requirements |
| own-se-057 | 已修 | 多家标准机构一致指向 ISO/IEC 19770-1；补充“19770 Part 1”、中文分册表述及标点变体，仍拒绝错误的第2部分。 | IT asset management system requirements 2017 ISO；IT资产管理体系 要求 标准；ISO ITAM systems requirements |
| own-se-058 | 已修 | NIST 对照资料及标准机构摘要一致指向 ISO/IEC 23894；补充中文数字编号写法，题面已明确区分 AI 风险管理指南与管理体系要求。 | AI risk management guidance 2023 ISO；人工智能 风险管理 指南 标准号；ISO IEC artificial intelligence risk guidance |
| own-se-059 | 已修 | ISO 正文分别确认产品质量模型 25010、使用质量模型 25019（标题及编号均在 @1220 前）；补充编号别写法，并让第二轮合并两轮结果写入 TSV，修复原先两问可独立作答的问题。 | SQuaRE product quality model 2023 ISO；SQuaRE quality-in-use model 2023 ISO；软件使用质量模型 2023 标准 |
| own-se-060 | 已修 | RFC Editor 原文 @52、@90 确认 RFC 8259 及 2017年12月；补存可打开的官方原文并补充中文数字编号，保留搜索要求。 | JSON data interchange format 2017 RFC；JSON 数据交换 RFC 编号；IETF JavaScript Object Notation December 2017 |
| own-se-061 | 已修 | RFC Editor 的 STD 97 记录 @524、@646 确认 HTTP Semantics 为 RFC 9110、2022年6月；补存官方发布记录并补充中文数字编号。 | HTTP Semantics RFC June 2022；HTTP 语义 标准 RFC；IETF HTTP semantics 2022 number |
| own-se-062 | 已修 | RFC Editor 正文 @499、@534 确认 RFC 8446、2018年8月，排除搜索中后续 RFC 的干扰；补存官方页面并补充中文数字编号。 | TLS 1.3 original specification RFC；传输层安全 1.3 标准；IETF TLS August 2018 |
| own-se-063 | 已修 | IETF 正文确认 RFC 6455、December 2011（日期 @171）；补充月份标点和中文编号，取消第二轮重复搜索要求，允许复用首轮摘要已经给出的发布日期。 | WebSocket Protocol original RFC；WebSocket RFC publication month year；WebSocket 协议 RFC 发布日期 |
| own-se-064 | 已修 | IETF QUIC 工作组首条摘要直接列出基础传输 RFC 9000 与 TLS 保护 RFC 9001；补充编号别写法，并让第二轮把前轮编号一起写入清单，允许复用现成证据。 | QUIC transport specification RFC；Using TLS to Secure QUIC RFC；QUIC TLS 安全 规范 编号 |
| own-se-065 | 已修 | W3C 发布邮件 @422、@631 确认 WCAG 2.2 首次成为 Recommendation 在2023年；补充“二千二十三／两千二十三”，保留“首次”口径以区分后续更新。 | WCAG 2.2 first recommendation year；无障碍指南 2.2 推荐标准 年份；Web Content Accessibility Guidelines 2.2 W3C release |
| own-se-066 | 已修 | 固定版 W3C 正文 @148、@146 分别确认 Level 2 为2021-04-08、Level 1 为2019-03-04；补充英文月份连字符日期，并要求第二轮合并两版日期登记，修复多轮依赖。 | WebAuthn Level 2 W3C Recommendation date；WebAuthn Level 1 W3C Recommendation date；网络认证 二级 W3C 推荐标准 日期 |
| own-se-067 | 已修 | W3C SVG 1.1 第二版正文摘要及勘误记录一致确认2011-08-16；补充“16-Aug-2011”等常见日期写法，版次和 Recommendation 口径明确。 | SVG 1.1 Second Edition Recommendation date；可缩放矢量图形 1.1 第二版 发布日期；W3C SVG Second Edition Recommendation |
| own-se-068 | 已修 | W3C 引用记录、ITU 和 OASIS 摘要一致确认 XML 1.0 第五版日期2008-11-26；补充“26-Nov-2008”等常见日期写法。 | XML 1.0 Fifth Edition Recommendation date；XML 第五版 W3C 发布日期；W3C Extensible Markup Language fifth edition publication |
| own-se-069 | 已修 | ITU 官方沿革 @1604 与联合国资料一致确认前身成立于1865年；补存官方沿革及电报相关搜索，修复只搜“International Telegraph Union establishment”返回空结果的问题。 | ITU founding year；国际电信联盟 成立 年份；International Telegraph Union establishment |
| own-se-070 | 已修 | ILO 官方资料确认1919年成立、日内瓦总部（正文 @1440、@5803）；用 web_tool 重建优先返回官方来源的搜索存档，并让第二轮合并成立年份和总部写入记录，允许复用首轮证据。 | ILO establishment year official history；ILO headquarters city；国际劳工组织 总部 城市 |
| own-se-071 | OK | WMO 官方历史和公约生效纪念资料一致确认1950年，题面明确以公约生效为成立口径，可与1873年前身、1947年公约通过和1951年专门机构身份区分。 | WMO convention entry into force establishment；世界气象组织 公约 成立 年份；World Meteorological Organization established year |
| own-se-072 | 已修 | IAEA 官方联系正文 @484、@584 确认 Vienna 与邮编1400；原先仅问城市容易凭常识猜中，现改为核实城市和邮编并填入通讯录，重建英文官方搜索并存档首条联系页面，明确区分信箱100。 | IAEA headquarters city；国际原子能机构 总部 城市；International Atomic Energy Agency location |

汇总：**OK 1题，已修17题，已删0题，有风险0题，共18题，全部保留。** 本批仍为搜索问答；中文11题、英文7题，简单8题、中等7题、较难3题，单轮13题、双轮5题。

最常见的问题是**判据对合理别写法覆盖不足**：虽然原题列举了很多形式，仍会拒绝中文数字、分册表述、月份缩写连字符日期及部分标点写法；其次是**多轮依赖弱、强制重复搜索**，以及个别搜索存档没有覆盖前身实体词或优先返回非官方来源。没有新增 output_excludes，也没有用答案字数限制筛选正确回复。

所有改动过的题均已单题运行 `python3 bank/check_own.py bank/own/cases/<id>.json`；最终再对本批18题统一运行，结果 **18/18通过**。另直接调用现有 judge/check_own 做了 **241项断言**：参考解、合理别写法、错误编号/日期、空操作、只有搜索调用、未搜索、五个清单的缺失/空白/任一事实错误，以及 bash 写文件和 CRLF 均作了正反核验。新增 TSV 文件明确规定表头、行序、分隔符及登记格式，最终回复措辞不设限制。

本批没有可执行参考修复或受保护程序测试，因此没有需要在 Debian 上重跑的代码行为；文件判据沿用 judge 的 CRLF 和尾部空白兼容逻辑，已验证。未运行实际 RWKV/DeepSeek Harness，也未声称验证模型完成率。规则层仍只能证明调用过搜索，不能证明模型实际依据了哪条来源；contains 类事实判据也不能识别所有矛盾叙述，这是现有判分器的共同边界，未通过添加排除词制造新的误杀。

仅修改本批 cases、六个本批 web-archive 存档及本报告；补页和重建搜索均通过 `bank/web_tool.py`，未手改存档，未执行 Git commit。
