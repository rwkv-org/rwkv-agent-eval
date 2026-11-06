已完整阅读 bank/own/SPEC.md、build/codex2/sef.prompt，并按 bank/judge.py 的实际实现逐题独立求解。范围仅 own-se-091—own-se-110；没有删除有效题目，没有修改判分器或本批以外的题目，没有 Git 提交。

全批共性修复：把首轮 required_tools 中的 read 改为 bash。这里的 bash 是现有判分器支持的“查看类”入口，read、grep、glob、bash 任一个均可满足；直接写 read 实际只接受 read，与 SPEC 的替代规则不符。搜索轮仍要求 web_search，本地轮仍禁止 web_search/web_fetch。下表的搜索词均按回放器的大小写不敏感子串规则实际检查，三种全部命中；本地题列出的搜索词仅用于检查误搜时的存档覆盖，不代表正确解法应联网。

| id | 结论 | 一句话原因（含独立求解结果与修复） | 三种合理搜索词；存档证据 |
|---|---|---|---|
| own-se-091 | 已修 | 水位控制器 MC-42 使用 RP2040，厂商标称 SRAM 为 264 kB，已修查看工具替代并补小数、全角及英文无连字符写法。 | `RP2040 片上 SRAM 容量` / `RP2040 on-chip SRAM vendor` / `树莓派 RP2040 RAM`；首条 Raspberry Pi 厂商摘要开头即列 264kB。 |
| own-se-092 | 已修 | A5 为 148×210 mm，按短边唯一选择 PT-28，已修工具判据并补中文数词、小数及等值厘米写法。 | `ISO A5 dimensions` / `A5 纸张 短边` / `A5 paper size mm`；首条 OpenJDK MediaSize.ISO 摘要明确 A5 尺寸，多条一致。 |
| own-se-093 | 已修 | SQLite→DB-19→WA-731 的本地签署关联正确且公共许可不能给出内部编号，仅修查看工具替代。 | `SQLite license` / `SQLite 商用 许可` / `SQLite public domain`；正确证据在 deps/release.csv、compliance/decisions.md，禁止联网仍保留。 |
| own-se-094 | 已修 | orchard-uplink 前导 6 字节加 PNG 签名 8 字节得偏移 14，已修工具与数字写法、撤去第二轮未在题面禁止的联网限制并补可搜索发现的短规范存档。 | `PNG 签名 长度` / `PNG signature length` / `PNG chunk file signature bytes`；原长页答案约 @46046，新 W3C PNG-Structure 短页答案 @440，搜索返回的带查询参数完整链接亦已 fetch 存档。 |
| own-se-095 | 已修 | brief 选 BR-62，14:20 UTC 加东京全年 UTC+9 为同日 23:20，已修工具替代并补时刻写法。 | `Tokyo UTC offset June 2026` / `东京 时区 夏令时` / `Japan standard time UTC`；timeanddate 摘要同时说明 +9 与 2026 无时钟变化，其他摘要一致。 |
| own-se-096 | 已修 | Cedar Foods→cedar-legacy 的合同 Content-Type 为 application/x-cedar-ledger，不能拿网上 text/csv 覆盖，仅修查看工具替代。 | `CSV MIME type` / `CSV 媒体类型` / `RFC 4180 text csv`；正确证据在 vendors.csv、export.toml、contract.md，联网禁止判据保留。 |
| own-se-097 | 已修 | BIPM 新 SI 定义于 2019 年生效而非 2018 年表决，故选 SI-19，已修工具替代并补年份写法。 | `摩尔 SI 新定义 生效年份` / `BIPM mole redefinition effective date` / `SI mole definition implementation`；首条 EURAMET 托管 BIPM 报告摘要明确 20 May 2019，INTI 等资料一致。 |
| own-se-098 | 已修 | tomllib 自 Python 3.11 加入，启用且最低合规 runner 为 PY-11，已修工具与版本写法并撤去第二轮题面未禁止的联网限制。 | `tomllib Python introduced version` / `Python tomllib 标准库 版本` / `tomllib added version documentation`；首条 docs.python.org/3.11/library/tomllib.html 摘要开头即有 New in version 3.11。 |
| own-se-099 | 已修 | WC-84→BK-27→R3 的已批准座管夹环扭矩为 5.2 N·m，已修查看工具替代并补尾零、乘号及繁体数词写法。 | `seatpost clamp torque` / `座管 夹环 扭矩` / `bicycle torque manufacturer`；正确证据在三份本地维修文件，不采用外部其他品牌的不同扭矩。 |
| own-se-100 | 已修 | 希腊字母 24 个，排除禁用 RK-24 与容量不足 RK-21 后最便宜为 RK-25、空余 1 格，已用两份单值报告校验 ID 和数量以消除“一”及 one 的子串放水并修工具判据。 | `modern Greek alphabet letter count` / `现代希腊 字母 数量` / `Greek alphabet how many letters`；首条现代希腊语手册与 EPFL 摘要均明确 24，末尾 sigma 变体不额外计数。 |
| own-se-101 | 已修 | EPUB 注册媒体类型 application/epub+zip 对应本地 UP-83，IANA 摘要支持且无需猜 ZIP 泛型，仅修查看工具替代。 | `EPUB registered media type` / `EPUB MIME type` / `电子书 EPUB 媒体类型`；IANA application/epub+zip 注册记录在第 4 条摘要中，全文短于 2400 字符。 |
| own-se-102 | 已修 | Pluto、wall-2026 对应 SK-38、批准标题“冰境来客”和队列 Q-CYAN，已补繁体标题、修首轮工具并取消可从上下文回答的第二轮重复读取要求。 | `Pluto IAU classification` / `冥王星 矮行星` / `Pluto dwarf planet`；正确证据全在 catalog.csv、labels.md、print.csv，第二轮新增只读快照约束且无工具调用也可答。 |
| own-se-103 | 已修 | LG-74 的 2.5 国际海里按每海里精确 1852 米换算为 4630 米，已修工具替代并补小数、Unicode 分组空格及公里写法。 | `international nautical mile metres` / `国际海里 多少米` / `nautical mile exact length`；NIST 资料存档摘要与美国气象学会摘要均给 1852 米，旧国别海里值已由本地说明排除。 |
| own-se-104 | 已修 | 公历世纪年须能被 400 整除才闰年，故仅 DA-73 的 2000-02-29 有效，已修查看工具替代并补年份写法。 | `公历 世纪年 闰年 规则` / `Gregorian leap year century rule` / `1900 2000 2100 leap years`；加拿大 NRC 与 Microsoft 摘要规则一致，未把 Excel 的 1900 兼容行为当公历。 |
| own-se-105 | 已修 | RB-26 使用本地标定 230 mL 的 house cup，3×230=690 mL，已修查看工具替代并补小数、全角和升写法。 | `house cup milliliters` / `量杯 毫升 换算` / `cup volume milliliter`；正确证据在 batch.md、calibration.md，外部英美杯制不能替代 HC-9。 |
| own-se-106 | 已修 | N17→reed-b→11 字节的带填充 Base64 为 16 字符，加 7 字符前缀得 23 并选 TX-24，已修工具与数字写法且第二轮改写填充数量报告，实际必须为 1。 | `RFC 4648 Base64 padding` / `Base64 分组 填充 规则` / `base64 length 11 bytes`；RFC 4648 正文 @9626 给分组规则、约 @11495 给余 16 bit 时一个等号，均小于 15000。 |
| own-se-107 | 已修 | tungsten 的元素符号 W 对应纯金属 MT-47，WC 是化合物且不合要求，NIST 等摘要支持，仅修查看工具替代。 | `tungsten chemical symbol` / `钨 元素符号` / `Wolfram tungsten symbol`；NIST WebBook 短摘要开头直接写 Formula: W，与其他摘要一致。 |
| own-se-108 | 已修 | Hall B→MU-41 的签署 rider 覆盖 442 Hz 默认值而取 443 Hz，已修查看工具替代并补尾零、全角及英文无连字符写法。 | `concert pitch orchestra A4` / `乐团 定音 音高` / `orchestra tuning standard`；正确证据是本地 program.csv、defaults.md、riders.md，外部标准不能替代本场附约。 |
| own-se-109 | 已修 | 马丘比丘在秘鲁，对应本地国家报价 QT-36，UNESCO 秘鲁遗产清单摘要明确列出该遗址，仅修查看工具替代。 | `马丘比丘 所在国家` / `Machu Picchu country UNESCO` / `Machu Picchu location`；第 4 条 UNESCO 摘要仅约 290 字符，按 Peru 遗产清单明确归属，多来源一致。 |
| own-se-110 | 已修 | Netherlands→EU-N→documents 基础路由 RT-18→approved 覆盖 RT-44，withdrawn 的 RT-63 无效且第二轮报告依赖此前选择，仅修查看工具替代。 | `Netherlands ISO 3166 code` / `荷兰 国家代码` / `Netherlands country code NL`；正确答案来自五份本地文件，不能从公共国家代码推出内部路由。 |

汇总：OK 0 道，已修 20 道，已删 0 道，有风险 0 道，共 20 道；没有发现答案错误、不能消解的题意歧义或必须删除的题目。保留 13 道联网题与 7 道本地题，中文 12 道、英文 8 道，easy 9 道、medium 8 道、hard 3 道，2 轮题 5 道；全部后续轮都复用首轮选出的对象或计算结果。

最常见的问题是查看类工具误杀（20 道），其次是数字 token 判据漏收尾零、紧连单位、中文或全角写法，以及数量 1 的过短子串放水；另有上下文缓存仍强制重读、未明确要求却禁止再次联网、长页面答案靠后。全部题的 output_excludes 和 expected_number 均未使用，因此没有旧值顺带解释被排除或默认 40 字符长度限制的问题。外部事实中虽有 A5、元素符号、国家归属等常识，整题仍须读本地非公开 ID、配置或关联表，单报常识不能通过；搜索轮也保留 web_search 约束。

验证：每次修改题目后均运行该题的 python3 bank/check_own.py，最后只传本批 20 个文件整批运行，结果 20/20 cases pass the self-check（包含参考答案通过及空回复、无工具的空操作不通过）。另直接调用实际 judge 验证 112 组合理答案/查看工具组合、20 组错误回答对照、102 第二轮缓存无调用回答、5 组缺报告对照与 6 组错误数量/格式对照，均符合预期。100、106 的报告会拒绝 0、21 或错误填充数，不能再靠回复中偶然出现的“一”过关。

执行边界：本批没有待修代码、Shell 脚本或 protected_tests，参考写入均为普通 UTF-8 文本，不依赖 BSD/GNU 差异，也不依赖 git/jq/curl/gawk；未宣称实际跑过 Debian 容器或 RWKV。规则只能确认工具调用和指定事实/文件，不能证明模型实际读完每一个文件或理解整个网页；本次没有越范围改动共享判分器。实际修改为本批 20 个 cases、own-se-094 的 web-archive，以及本报告；补页与补搜索全部经 bank/web_tool.py 完成，没有手改存档。
