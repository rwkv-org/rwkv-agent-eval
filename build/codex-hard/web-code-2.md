逐题审阅21题的两次 adapter steps、judge 和可见 final，并以两次 base 作对照；步号均指各 trial 的 steps 全局序号，截断内容不作为完整源码证据。
主因分布：doc-apply 12题、spec-miss 1题、think-loop-timeout 1题、no-verify-fabricate 2题、give-up-fallback 2题、cmd-error 1题、code-logic 1题、task-suspect 1题；超时和模板收尾常是前序错误未恢复的结果，不直接按 kind 定因。
最常见机制是文档规则到代码的落地失败：混淆比较器与排序 key、视图与复制、默认参数、编码计数单位及时间语义，读网页本身没有保证理解。
优先补“定位指定小节→列出可执行契约→复用标准库原语最小修复→边界反例→跑原测试”的短轨迹，覆盖 re、LoggerAdapter、Buffer、URLSearchParams、Intl、JSON Schema、cron 和 raw -z。
第二类是失去实际执行与验证闭环：写入被拒或未执行、测试明确失败，仍在 final 贴代码或编造通过；补“读真实报错→按当前源码修补→读回→复测→仅引用实际结果”的恢复样本。
第三类是多轮交付与工具恢复中断：首轮通过不代表完成后轮报告；猜缓存路径、重复抓锚点或重复失败命令后容易模板退出，补真实 spill 路径定位和失败后改变策略的样本。
多轮样本应明确首轮修复验收、次轮冻结业务模块并调用修好的函数处理输入、写出完整 JSON、运行交付验收；保留原始测试，不能抄 expected 或用文本方案代替落盘。
own-wc-073/090 存在判据问题：后轮允许新增结果文件，unchanged_files 却触发任意 write/edit 拒绝；073 的 case 检查均通过、仅此标签失败，090 另有独立解析失败，需先校准判据，不能训练模型绕过写工具。
全部 near_miss=false：按两次 adapter 的整题交付判断，均有未落盘、未验收、多轮未完成或多项语义错误；题目对称职工程师主要为 easy，日志上下文、严格整数解析及变长记录解析为 medium。
