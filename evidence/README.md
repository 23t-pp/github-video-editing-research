# 证据数据怎么读

- `statistics.json`：汇总口径；身份统计与源码审查统计分开。
- `search/queries.json`：查询id、检索分支、实际取回数、服务端total_count、incomplete_results、原始响应文件。缺精确时间的条目只记录研究日期，不补造时间。
- `search/raw/`：28份GitHub公开仓库搜索响应。默认排序、一页30条，不是全网结果。
- `catalog.json`：按数字id合并的557个仓库；query_ids说明每个项目从哪些关键词找到。只有26个被选入重点源码审查。
- `reviewed-projects.json`：统一的26项审查；包含模板性质、节拍方式、依赖、Windows判断、限制与证据链接。
- `repository-snapshots.json`：重点仓库的SHA、星数、push日期、归档状态、API许可识别与人工许可记录。
- `reviews/`：各分支结构化报告，含排除与去重理由。
- `dedup-decisions.json`：同仓命中、旧地址、来源家族、本机已有能力等不同类型的去重判断。
- `exclusions.json`：排除或降级理由；不表示所有这些项目都做过源码审查。
- `local-audit.json`：只读本机观察的脱敏摘要。原工程未公开，第三方不能仅凭这里在线重验。
- `validation.json`：研究交付自身的验证。这里的脚本通过不代表剪辑候选软件通过测试。
- `source-path-validation.json`：115条证据路径都在对应固定提交的目录树中，目录树均未截断。
- `probes/`：旧仓库地址重定向、衍生家族元数据，以及重点文件的最近提交日期。已去掉不必要的提交作者邮箱。

原始响应保留GitHub返回的公开仓库信息；不会包含本次登录凭据。原始元数据和人工判断分开保存，便于以后更新而不改写旧证据。

`evidence_level`的E2表示静态代码检查。运行验证需要单独记录软件版本、环境、输入、命令与输出，本次未对新候选做这一层。
