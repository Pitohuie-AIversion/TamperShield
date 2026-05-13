# TamperShield Evidence Report

## Summary

- Total differences: 69
- By severity: {"medium": 60, "high": 9}
- By category: {"layout": 12, "page": 9, "text": 25, "paragraph": 23}
- By diff type: {"layout_changed": 12, "page_added": 2, "text_modified": 25, "paragraph_added": 19, "paragraph_deleted": 4, "page_deleted": 7}
- Requires manual review: 0
- Requires table compare: 0

## Metadata

- baseline_file: data\base_docs\1.-合同协议书-宁波东方理工大学（暂名）校园建设项目永久校区1号地块及2号地块-二期（东生活组团-1）工程监理2023.8.17.docx
- baseline_file_type: docx
- baseline_page_count: 44
- candidate_file: data\base_docs\1.-合同协议书-宁波东方理工大学（暂名）校园建设项目永久校区1号地块及2号地块-二期（东生活组团-1）工程监理-1-39.pdf
- candidate_file_type: pdf
- candidate_page_count: 39
- difference_count: 69

## Evidence by Candidate Page

### Candidate Page 1

#### ev-00001-layout_changed

- Diff type: layout_changed
- Category: layout
- Severity: medium
- Candidate page: 1
- Baseline page: 1
- Candidate element: None
- Baseline element: None
- Message: Page alignment confidence is low and needs review.

Metadata:

```json
{
  "alignment_reason": "Best baseline page only reached the low confidence threshold.",
  "alignment_score": 0.6968325791855203,
  "baseline_index": 0,
  "baseline_page_number": 1,
  "candidate_index": 0,
  "candidate_page_number": 1,
  "expected_baseline_index": 0,
  "forward_baseline_skip": 0,
  "is_forward_sequence_match": true,
  "search_window": 2
}
```

### Candidate Page 2

#### ev-00002-page_added

- Diff type: page_added
- Category: page
- Severity: high
- Candidate page: 2
- Baseline page: None
- Candidate element: None
- Baseline element: None
- Message: Candidate document contains an added page; see page_issue_category metadata for review context.

Review context:

- Page issue category: likely_toc_or_cover_format_noise
- Suggested review severity: medium
- Classification reason: Page text and page position suggest table-of-contents or cover formatting differences.

Page profile:

- Text length: 333
- Is blank: False
- Element count: 33
- Element type counts: {"paragraph": 33}
- Text preview: 目 录 第一部分 合同协议书 第二部分 通用条款 1、总则 2、委托人权利、义务与责任 3、监理人权利、义务与责任 4、监理期限、监理费用及付款方式 5、违约责任 6、合同的转让与分包 7、不可抗力 8、合同的解除 9、履约保证 10、争议

Metadata:

```json
{
  "alignment_reason": "No baseline page in the search window reached the low confidence threshold.",
  "alignment_score": 0.293953488372093,
  "baseline_cursor": 1,
  "candidate_index": 1,
  "candidate_page_number": 2,
  "classification_reason": "Page text and page position suggest table-of-contents or cover formatting differences.",
  "page_issue_category": "likely_toc_or_cover_format_noise",
  "page_profile": {
    "element_count": 33,
    "element_type_counts": {
      "paragraph": 33
    },
    "is_blank": false,
    "text_length": 333,
    "text_preview": "目 录 第一部分 合同协议书 第二部分 通用条款 1、总则 2、委托人权利、义务与责任 3、监理人权利、义务与责任 4、监理期限、监理费用及付款方式 5、违约责任 6、合同的转让与分包 7、不可抗力 8、合同的解除 9、履约保证 10、争议"
  },
  "search_window": 2,
  "suggested_review_severity": "medium"
}
```

### Candidate Page 3

#### ev-00003-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 3
- Baseline page: 4
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.9649 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "第一部分 合同协议书 委托人（全称）：宁波东方理工大学（暂名） 监理人（全称）：同舟国际工程管理有限公司 代建人（全称）：深圳市润置城市建设管理有限公司 根据《中华人民共和国民法典》、《中华人民共和国建筑法》及其他有关法律、 法规，遵循平等",
  "candidate_text_preview": "第一部分 合同协议书 委托人（全称）：宁波东方理工大学（暂名） 监理人（全称）：同舟国际工程管理有限公司 代建人（全称）：深圳市润置城市建设管理有限公司 根据《中华人民共和国民法典》、《中华人民共和国建筑法》及其他有关法律、法 规，遵循平等",
  "similarity": 0.9649122807017544,
  "threshold": 0.98
}
```

#### ev-00004-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 3
- Baseline page: 4
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=30, baseline=27.

Metadata:

```json
{
  "baseline_count": 27,
  "candidate_count": 30,
  "element_type": "paragraph"
}
```

### Candidate Page 4

#### ev-00005-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 4
- Baseline page: 5
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.9648 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "(a) 本合同书 (b) 通用条款 (c) 专用条款 (d) 合同附件 (e) 双方在回标后至定标前的下列来往文件： （若文件中含与原采购文件相悖的条款，除非得到委托人书面认可外，均不能成为 合同文件的组成部分。） (f) 采购文件，包括：",
  "candidate_text_preview": "(c) 专用条款 (d) 合同附件 (e) 双方在回标后至定标前的下列来往文件： （若文件中含与原采购文件相悖的条款，除非得到委托人书面认可外，均不能成为 合同文件的组成部分。） (f) 采购文件，包括： (1) 投标须知 (2) 技术要求",
  "similarity": 0.96484375,
  "threshold": 0.98
}
```

#### ev-00006-paragraph_deleted

- Diff type: paragraph_deleted
- Category: paragraph
- Severity: medium
- Candidate page: 4
- Baseline page: 5
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=24, baseline=25.

Metadata:

```json
{
  "baseline_count": 25,
  "candidate_count": 24,
  "element_type": "paragraph"
}
```

### Candidate Page 5

#### ev-00007-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 5
- Baseline page: 6
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.9570 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "委托人：（盖章） 监理人 ：同舟国际工程管理有限公司（盖 章） 法定代表人或其委托代理人： 法定代表人或其委托代理人： （签字） （签字） 地址： 浙江省宁波市镇海区庄市 地址：浙江省慈溪市宗汉街道新华村香楝树 街道同心路568 号开元新青",
  "candidate_text_preview": "委托人：（盖章） 监理人：同舟国际工程管理有限公司（盖章） 法定代表人或其委托代理人： 法定代表人或其委托代理人： （签字） （签字） 地址：浙江省宁波市镇海区庄市 地址：浙江省慈溪市宗汉街道新华村香楝树 街道同心路568 号开元新青年广 ",
  "similarity": 0.9569752281616688,
  "threshold": 0.98
}
```

### Candidate Page 6

#### ev-00008-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 6
- Baseline page: 7
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.9756 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "第二部分 通用条款 1、 总则 1.1 定义 下列词语或措辞，除特别说明外，在本合同中均具有以下赋予的含义： 1.1.1 “项目”是指特别条款中指定的并为之建造的工程项目，即“宁波东方理工大学 （暂名）校园建设项目永久校区 1 号地块及 2",
  "candidate_text_preview": "第二部分 通用条款 1、 总则 1.1 定义 下列词语或措辞，除特别说明外，在本合同中均具有以下赋予的含义： 1.1.1 “项目”是指特别条款中指定的并为之建造的工程项目，即“宁波东方理工大学（暂 名）校园建设项目永久校区1 号地块及2 号",
  "similarity": 0.9755784061696658,
  "threshold": 0.98
}
```

### Candidate Page 7

#### ev-00009-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 7
- Baseline page: 8
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.8849 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "2、委托人权利、义务与责任 2.1 委托人权利： 2.1.1 委托人有依法选定项目总监理人，以及与其订立施工合同的权利。 2.1.2 委托人有对工程规模、设计标准、规划设计、生产工艺设计和设计使用功能要求 的认定权，以及对工程设计变更的审批",
  "candidate_text_preview": "2、委托人权利、义务与责任 2.1 委托人权利： 2.1.1 委托人有依法选定项目总监理人，以及与其订立施工合同的权利。 2.1.2 委托人有对工程规模、设计标准、规划设计、生产工艺设计和设计使用功能要求的 认定权，以及对工程设计变更的审批",
  "similarity": 0.8848837209302326,
  "threshold": 0.98
}
```

#### ev-00010-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 7
- Baseline page: 8
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=34, baseline=28.

Metadata:

```json
{
  "baseline_count": 28,
  "candidate_count": 34,
  "element_type": "paragraph"
}
```

### Candidate Page 8

#### ev-00011-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 8
- Baseline page: 9
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.7546 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "2.2.1 委托人按合同约定的期限和方式向监理人支付款项。 2.2.2 按《专用条款》的约定向监理人提供开展监理工作所需的工程资料。 2.2.3 委托人应负责项目建设外部关系的协调，为监理工作提供外部条件。外部关系是 指与项目建设相关的各级",
  "candidate_text_preview": "2.2.4 在合理期限内就监理人书面提交的要求作出决定给予书面回复。 2.2.5 授权一名熟悉工程情况、能在规定时间内作出决定的现场代表（在《专用条款》中 约定），负责与监理人联系。更换现场代表，要提前通知监理人。 2.2.6 委托人将授予",
  "similarity": 0.7546174142480211,
  "threshold": 0.98
}
```

#### ev-00012-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 8
- Baseline page: 9
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=33, baseline=30.

Metadata:

```json
{
  "baseline_count": 30,
  "candidate_count": 33,
  "element_type": "paragraph"
}
```

### Candidate Page 9

#### ev-00013-layout_changed

- Diff type: layout_changed
- Category: layout
- Severity: medium
- Candidate page: 9
- Baseline page: 10
- Candidate element: None
- Baseline element: None
- Message: Page alignment confidence is low and needs review.

Metadata:

```json
{
  "alignment_reason": "Best baseline page only reached the low confidence threshold.",
  "alignment_score": 0.7106756059824652,
  "baseline_index": 9,
  "baseline_page_number": 10,
  "candidate_index": 8,
  "candidate_page_number": 9,
  "expected_baseline_index": 9,
  "forward_baseline_skip": 0,
  "is_forward_sequence_match": true,
  "search_window": 2
}
```

### Candidate Page 10

#### ev-00014-layout_changed

- Diff type: layout_changed
- Category: layout
- Severity: medium
- Candidate page: 10
- Baseline page: 11
- Candidate element: None
- Baseline element: None
- Message: Page alignment confidence is low and needs review.

Metadata:

```json
{
  "alignment_reason": "Best baseline page only reached the low confidence threshold.",
  "alignment_score": 0.6351028216164515,
  "baseline_index": 10,
  "baseline_page_number": 11,
  "candidate_index": 9,
  "candidate_page_number": 10,
  "expected_baseline_index": 10,
  "forward_baseline_skip": 0,
  "is_forward_sequence_match": true,
  "search_window": 2
}
```

### Candidate Page 11

#### ev-00015-layout_changed

- Diff type: layout_changed
- Category: layout
- Severity: medium
- Candidate page: 11
- Baseline page: 12
- Candidate element: None
- Baseline element: None
- Message: Page alignment confidence is low and needs review.

Metadata:

```json
{
  "alignment_reason": "Best baseline page only reached the low confidence threshold.",
  "alignment_score": 0.5011467889908257,
  "baseline_index": 11,
  "baseline_page_number": 12,
  "candidate_index": 10,
  "candidate_page_number": 11,
  "expected_baseline_index": 11,
  "forward_baseline_skip": 0,
  "is_forward_sequence_match": true,
  "search_window": 2
}
```

### Candidate Page 12

#### ev-00016-layout_changed

- Diff type: layout_changed
- Category: layout
- Severity: medium
- Candidate page: 12
- Baseline page: 13
- Candidate element: None
- Baseline element: None
- Message: Page alignment confidence is low and needs review.

Metadata:

```json
{
  "alignment_reason": "Best baseline page only reached the low confidence threshold.",
  "alignment_score": 0.5705361790733993,
  "baseline_index": 12,
  "baseline_page_number": 13,
  "candidate_index": 11,
  "candidate_page_number": 12,
  "expected_baseline_index": 12,
  "forward_baseline_skip": 0,
  "is_forward_sequence_match": true,
  "search_window": 2
}
```

### Candidate Page 13

#### ev-00017-layout_changed

- Diff type: layout_changed
- Category: layout
- Severity: medium
- Candidate page: 13
- Baseline page: 15
- Candidate element: None
- Baseline element: None
- Message: Page alignment confidence is low and needs review.

Metadata:

```json
{
  "alignment_reason": "Best baseline page only reached the low confidence threshold.",
  "alignment_score": 0.5686080947680158,
  "baseline_index": 14,
  "baseline_page_number": 15,
  "candidate_index": 12,
  "candidate_page_number": 13,
  "expected_baseline_index": 13,
  "forward_baseline_skip": 1,
  "is_forward_sequence_match": true,
  "search_window": 2
}
```

### Candidate Page 14

#### ev-00018-layout_changed

- Diff type: layout_changed
- Category: layout
- Severity: medium
- Candidate page: 14
- Baseline page: 16
- Candidate element: None
- Baseline element: None
- Message: Page alignment confidence is low and needs review.

Metadata:

```json
{
  "alignment_reason": "Best baseline page only reached the low confidence threshold.",
  "alignment_score": 0.6411727214786488,
  "baseline_index": 15,
  "baseline_page_number": 16,
  "candidate_index": 13,
  "candidate_page_number": 14,
  "expected_baseline_index": 15,
  "forward_baseline_skip": 0,
  "is_forward_sequence_match": true,
  "search_window": 2
}
```

### Candidate Page 15

#### ev-00019-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 15
- Baseline page: 17
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.7770 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "分包其监理工作时，分包单位的资质应事先经委托人审查和批准。 7、不可抗力 7.1 如果因为不可抗力原因使本合同无法继续履行时，任何一方书面通知对方14 天后 有权终止本合同。合同终止时委托人应支付监理人当月的监理服务费；终止后各 自的损失由",
  "candidate_text_preview": "6、合同的转让与分包 6.1 合同的转让 6.1.1 无委托人的书面同意，监理人不得将本合同内的任何监理工作予以转让。否则委 托人将视监理人违约，部分或全部没收其履约保证金。 6.2 合同的分包 6.2.1 无委托人的书面同意，监理人不得将",
  "similarity": 0.7770392749244713,
  "threshold": 0.98
}
```

#### ev-00020-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 15
- Baseline page: 17
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=29, baseline=28.

Metadata:

```json
{
  "baseline_count": 28,
  "candidate_count": 29,
  "element_type": "paragraph"
}
```

### Candidate Page 16

#### ev-00021-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 16
- Baseline page: 18
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.8311 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "8.1.7 监理人员二次出现“吃、拿、卡、拖”等渎职行为的，委托人有权解除合同。 8.1.8 一方因违反法律法规或地方政府规定而致被采取强制措施限制履约权利、强令解 散的，对方有权解除合同。 8.1.9 一方因债权人占有该方或其任何附属公司",
  "candidate_text_preview": "改正要求后逾期仍继续其违约事项或仍未能消除违约影响或采取补救措施的，或限 期改正后又发生同类违约事项的，委托人有权解除合同。 8.1.4 发生监理人转包或挂靠行为，委托人有权解除合同。 8.1.5 发生重大质量事故（指直接经济损失50 万元",
  "similarity": 0.8310991957104558,
  "threshold": 0.98
}
```

#### ev-00022-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 16
- Baseline page: 18
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=33, baseline=29.

Metadata:

```json
{
  "baseline_count": 29,
  "candidate_count": 33,
  "element_type": "paragraph"
}
```

### Candidate Page 17

#### ev-00023-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 17
- Baseline page: 19
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.7632 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "11.1 知识产权 11.1.1 监理人编制的与本工程有关的所有文件，此等知识产权为委托人所有。 11.2 通知 11.2.1 本合同的有关通知应为书面形式，并以在合同中写明的地点签收时视为送达。通 知由人员传递，或传真通讯，但要求书面回执",
  "candidate_text_preview": "10.1.2 在监理合同争议的协商、诉讼期内，除提交诉讼的争议事项外，监理合同仍应继续 履行，双方应保证工程建设的正常进行。 11、 其他 11.1 知识产权 11.1.1 监理人编制的与本工程有关的所有文件，此等知识产权为委托人所有。 1",
  "similarity": 0.7632311977715878,
  "threshold": 0.98
}
```

#### ev-00024-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 17
- Baseline page: 19
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=9, baseline=6.

Metadata:

```json
{
  "baseline_count": 6,
  "candidate_count": 9,
  "element_type": "paragraph"
}
```

### Candidate Page 18

#### ev-00025-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 18
- Baseline page: 20
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.9173 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "第三部分 专用条款 一、总则 1. 合同文件及解释 1.1 合同附件： 1.2 附件1：建设工程项目廉政合同 1.3 附件2：《报价清单表》 1.4 附件3：采购人要求 1.5 附件4：关于指挥长职责承诺书 1.6 附件5：安全管理协议书 ",
  "candidate_text_preview": "第三部分 专用条款 一、总则 1. 合同文件及解释 1.1 合同附件： 1.2 附件1：建设工程项目廉政合同 1.3 附件2：《报价清单表》 1.4 附件3：采购人要求 1.5 附件4：关于指挥长职责承诺书 1.6 附件5：安全管理协议书 ",
  "similarity": 0.91725768321513,
  "threshold": 0.98
}
```

#### ev-00026-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 18
- Baseline page: 20
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=28, baseline=25.

Metadata:

```json
{
  "baseline_count": 25,
  "candidate_count": 28,
  "element_type": "paragraph"
}
```

### Candidate Page 19

#### ev-00027-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 19
- Baseline page: 21
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.8858 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "3.1 监理人任命的总指挥是高良波，总监理工程师是田昌军。项目团队的具体架构及 人员名单详见附件3 采购人要求。 3.2 项目团队需配备的办公设备及检测仪器：详见表【拟投入本采购项目的办公及检 测设备配备表】 3.3 其他为满足监理工作监理",
  "candidate_text_preview": "3.2 项目团队需配备的办公设备及检测仪器：详见表【拟投入本采购项目的办公及检测 设备配备表】 3.3 其他为满足监理工作监理人应该具备的检测仪器。 3.4 以上仪器设备必须为满足工作需要的合格产品，检测设备、仪器均保证在检定有效 期之内。",
  "similarity": 0.8858218318695107,
  "threshold": 0.98
}
```

#### ev-00028-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 19
- Baseline page: 21
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=30, baseline=28.

Metadata:

```json
{
  "baseline_count": 28,
  "candidate_count": 30,
  "element_type": "paragraph"
}
```

### Candidate Page 20

#### ev-00029-layout_changed

- Diff type: layout_changed
- Category: layout
- Severity: medium
- Candidate page: 20
- Baseline page: 22
- Candidate element: None
- Baseline element: None
- Message: Page alignment confidence is low and needs review.

Metadata:

```json
{
  "alignment_reason": "Best baseline page only reached the low confidence threshold.",
  "alignment_score": 0.7212276214833759,
  "baseline_index": 21,
  "baseline_page_number": 22,
  "candidate_index": 19,
  "candidate_page_number": 20,
  "expected_baseline_index": 21,
  "forward_baseline_skip": 0,
  "is_forward_sequence_match": true,
  "search_window": 2
}
```

### Candidate Page 21

#### ev-00030-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 21
- Baseline page: 23
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.8471 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "附件1 建设工程项目廉政合同 工程项目名称：宁波东方理工大学（暂名）校园建设项目永久校区1 号地块及2 号地块-二 期（东生活组团-1）工程监理。 工程项目地址：宁波市镇海区清水浦片区，北临风华路，南至滨江路，东至宁波绕城高速。 委托人名称",
  "candidate_text_preview": "附件1 建设工程项目廉政合同 工程项目名称：宁波东方理工大学（暂名）校园建设项目永久校区1 号地块及2 号地块-二 期（东生活组团-1）工程监理。 工程项目地址：宁波市镇海区清水浦片区，北临风华路，南至滨江路，东至宁波绕城高速。 委托人名称",
  "similarity": 0.8471337579617835,
  "threshold": 0.98
}
```

#### ev-00031-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 21
- Baseline page: 23
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=31, baseline=22.

Metadata:

```json
{
  "baseline_count": 22,
  "candidate_count": 31,
  "element_type": "paragraph"
}
```

### Candidate Page 22

#### ev-00032-layout_changed

- Diff type: layout_changed
- Category: layout
- Severity: medium
- Candidate page: 22
- Baseline page: 24
- Candidate element: None
- Baseline element: None
- Message: Page alignment confidence is low and needs review.

Metadata:

```json
{
  "alignment_reason": "Best baseline page only reached the low confidence threshold.",
  "alignment_score": 0.5189873417721519,
  "baseline_index": 23,
  "baseline_page_number": 24,
  "candidate_index": 21,
  "candidate_page_number": 22,
  "expected_baseline_index": 23,
  "forward_baseline_skip": 0,
  "is_forward_sequence_match": true,
  "search_window": 2
}
```

### Candidate Page 23

#### ev-00033-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 23
- Baseline page: 25
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.8688 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "第六条 本责任书的有效期为双方签署之日起至该工程项目竣工验收合格时止。 甲方单位：（盖章） 乙方单位：同舟国际工程管理有限公司（盖 章） 法定代表人： 法定代表人： 地址：浙江省宁波市镇海区庄市街道 地址：浙江省慈溪市宗汉街道新华村香楝树西",
  "candidate_text_preview": "甲方单位：（盖章） 乙方单位：同舟国际工程管理有限公司（盖章） 法定代表人： 法定代表人： 地址：浙江省宁波市镇海区庄市街道 地址：浙江省慈溪市宗汉街道新华村香楝树西 同心路568 号开元新青年广场2 号楼 路49 号 电话：0574-86",
  "similarity": 0.868824531516184,
  "threshold": 0.98
}
```

#### ev-00034-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 23
- Baseline page: 25
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=18, baseline=15.

Metadata:

```json
{
  "baseline_count": 15,
  "candidate_count": 18,
  "element_type": "paragraph"
}
```

### Candidate Page 24

#### ev-00035-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 24
- Baseline page: 27
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.9503 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "附件2 报价清单表 1、供应商根据采购人提供的清单编制完整的竞争性磋商报价清单。供应商 在打印响应文件和编辑商务标书电子版时，须认真事先检查，以保证竞争性磋 商报价清单的完整性。对于不完整的竞争性磋商报价清单，采购人有权拒绝或 予以废标。 ",
  "candidate_text_preview": "附件2 报价清单表 1、供应商根据采购人提供的清单编制完整的竞争性磋商报价清单。供应商 在打印响应文件和编辑商务标书电子版时，须认真事先检查，以保证竞争性磋商 报价清单的完整性。对于不完整的竞争性磋商报价清单，采购人有权拒绝或予以 废标。 ",
  "similarity": 0.9503051438535309,
  "threshold": 0.98
}
```

#### ev-00036-paragraph_deleted

- Diff type: paragraph_deleted
- Category: paragraph
- Severity: medium
- Candidate page: 24
- Baseline page: 27
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=47, baseline=48.

Metadata:

```json
{
  "baseline_count": 48,
  "candidate_count": 47,
  "element_type": "paragraph"
}
```

### Candidate Page 25

#### ev-00037-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 25
- Baseline page: 28
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.9016 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "日期： 年 月 日 附件3 采购人要求 采购人提供的设计图纸等技术资料包括： 按规定提供 监理工作规范和规程包括：国家、建设部、项目所在地（浙江省）颁发的监理法规等。 项目管理机构组成表 本项目 任职 姓名 职称 专业 执业或职业资格证明 ",
  "candidate_text_preview": "附件3 采购人要求 采购人提供的设计图纸等技术资料包括： 按规定提供 监理工作规范和规程包括：国家、建设部、项目所在地（浙江省）颁发的监理法规等。 项目管理机构组成表 本项目 任职 姓名 职称 专业 执业或职业资格证明 人 数 备 注 证书",
  "similarity": 0.9016393442622951,
  "threshold": 0.98
}
```

#### ev-00038-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 25
- Baseline page: 28
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=68, baseline=59.

Metadata:

```json
{
  "baseline_count": 59,
  "candidate_count": 68,
  "element_type": "paragraph"
}
```

### Candidate Page 26

#### ev-00039-layout_changed

- Diff type: layout_changed
- Category: layout
- Severity: medium
- Candidate page: 26
- Baseline page: 29
- Candidate element: None
- Baseline element: None
- Message: Page alignment confidence is low and needs review.

Metadata:

```json
{
  "alignment_reason": "Best baseline page only reached the low confidence threshold.",
  "alignment_score": 0.7258566978193146,
  "baseline_index": 28,
  "baseline_page_number": 29,
  "candidate_index": 25,
  "candidate_page_number": 26,
  "expected_baseline_index": 28,
  "forward_baseline_skip": 0,
  "is_forward_sequence_match": true,
  "search_window": 2
}
```

### Candidate Page 27

#### ev-00040-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 27
- Baseline page: 30
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.8019 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "16 安全监理工程师 17 资料员 拟投入本项目的办公及检测设备配备表 序号 名称 数量 备注 1 全站仪 壹套 根据工程需要增加 2 水准仪 壹套 根据工程需要增加 3 经纬仪 壹套 根据工程需要增加 4 激光测距仪 五套 根据工程需要增",
  "candidate_text_preview": "拟投入本项目的办公及检测设备配备表 序号 名称 数量 备注 1 全站仪 壹套 根据工程需要增加 2 水准仪 壹套 根据工程需要增加 3 经纬仪 壹套 根据工程需要增加 4 激光测距仪 五套 根据工程需要增加 5 激光垂准仪 贰套 根据工程需",
  "similarity": 0.8018575851393189,
  "threshold": 0.98
}
```

#### ev-00041-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 27
- Baseline page: 30
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=20, baseline=16.

Metadata:

```json
{
  "baseline_count": 16,
  "candidate_count": 20,
  "element_type": "paragraph"
}
```

### Candidate Page 28

#### ev-00042-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 28
- Baseline page: 31
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.7556 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "13 扫描仪 壹套 根据工程需要增加 14 数码相机 贰套 根据工程需要增加 15 游标卡尺 贰套 根据工程需要增加 16 靠尺 贰套 根据工程需要增加 17 刻度放大镜 贰套 根据工程需要增加 18 钢筋保护层测定仪 壹套 根据工程需要增",
  "candidate_text_preview": "18 钢筋保护层测定仪 壹套 根据工程需要增加 19 插座检测仪 壹套 根据工程需要增加 20 超声波测厚仪 壹套 根据工程需要增加 21 钳型电流表 壹套 根据工程需要增加 22 万用电表 壹套 根据工程需要增加 23 厚度测试仪 壹套 ",
  "similarity": 0.7555555555555555,
  "threshold": 0.98
}
```

#### ev-00043-paragraph_deleted

- Diff type: paragraph_deleted
- Category: paragraph
- Severity: medium
- Candidate page: 28
- Baseline page: 31
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=9, baseline=13.

Metadata:

```json
{
  "baseline_count": 13,
  "candidate_count": 9,
  "element_type": "paragraph"
}
```

### Candidate Page 29

#### ev-00044-layout_changed

- Diff type: layout_changed
- Category: layout
- Severity: medium
- Candidate page: 29
- Baseline page: 33
- Candidate element: None
- Baseline element: None
- Message: Page alignment confidence is low and needs review.

Metadata:

```json
{
  "alignment_reason": "Best baseline page only reached the low confidence threshold.",
  "alignment_score": 0.7118110236220473,
  "baseline_index": 32,
  "baseline_page_number": 33,
  "candidate_index": 28,
  "candidate_page_number": 29,
  "expected_baseline_index": 31,
  "forward_baseline_skip": 1,
  "is_forward_sequence_match": true,
  "search_window": 2
}
```

### Candidate Page 30

#### ev-00045-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 30
- Baseline page: 34
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.8385 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "附件5 安全管理协议书 甲方：宁波东方理工大学（暂名） 乙方：同舟国际工程管理有限公司 丙方：深圳市润置城市建设管理有限公司 2022 年12 月,甲方委托丙方对宁波东方理工大学（暂名）校 园建设项目（以下简称本项目）进行全过程代建，由甲方",
  "candidate_text_preview": "附件5 安全管理协议书 甲方：宁波东方理工大学（暂名） 乙方：同舟国际工程管理有限公司 丙方：深圳市润置城市建设管理有限公司 2022 年12 月,甲方委托丙方对宁波东方理工大学（暂名）校 园建设项目（以下简称本项目）进行全过程代建，由甲方",
  "similarity": 0.8385155466399198,
  "threshold": 0.98
}
```

#### ev-00046-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 30
- Baseline page: 34
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=23, baseline=19.

Metadata:

```json
{
  "baseline_count": 19,
  "candidate_count": 23,
  "element_type": "paragraph"
}
```

### Candidate Page 31

#### ev-00047-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 31
- Baseline page: 35
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.8542 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "期限暂定开始服务时间为2023 年8 月1 日，结束服务时间为2025 年 12 月31 日，具体开始时间以委托人通知为准。 第三条 权利义务 1．甲方为本项目建设单位，对该项目乙方管理工作或成果具有 最终决策权。甲方的任何批准、不批准或修",
  "candidate_text_preview": "1．甲方为本项目建设单位，对该项目乙方管理工作或成果具有 最终决策权。甲方的任何批准、不批准或修改、建议皆不会减轻乙方 应承担的责任。 2．丙方作为该项目的代建单位，与甲方在本项目中共同行使甲 方的权利。 3．乙方为本项目的监理单位，丙方可",
  "similarity": 0.8541846419327006,
  "threshold": 0.98
}
```

#### ev-00048-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 31
- Baseline page: 35
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=25, baseline=24.

Metadata:

```json
{
  "baseline_count": 24,
  "candidate_count": 25,
  "element_type": "paragraph"
}
```

### Candidate Page 32

#### ev-00049-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 32
- Baseline page: 36
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.8611 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "方进行处理，对问题严重甚至不服从管理的乙方，有权解除合同， 并由乙方承担一切经济责任。 6．甲方管理人员不得违章指挥，发现乙方管理人员违章指挥及 作业人员违章作业时，有权制止。 7．甲方不得提出不符合建设工程安全生产法律、法规和强制性 标准",
  "candidate_text_preview": "作业人员违章作业时，有权制止。 7．甲方不得提出不符合建设工程安全生产法律、法规和强制性 标准规定的要求，不得压缩合同约定的工期。 8．甲方不得明示或者暗示乙方购买、租赁、使用不符合安全施 工要求的安全防护用具、机械设备、施工机具及配件、消",
  "similarity": 0.8610837438423645,
  "threshold": 0.98
}
```

#### ev-00050-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 32
- Baseline page: 36
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=25, baseline=24.

Metadata:

```json
{
  "baseline_count": 24,
  "candidate_count": 25,
  "element_type": "paragraph"
}
```

### Candidate Page 33

#### ev-00051-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 33
- Baseline page: 37
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.9005 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "责任单位按要求落实整改工作。 8．及时组织或参加安全专题会议，对项目安全风险和隐患，提 出整改建议和要求。 9．乙方若疏于管理或安全制度措施不落实导致出现各类安全隐 患或存在其他违约行为，丙方有权代表甲方对其进行处以违约金、 追究损失等，相",
  "candidate_text_preview": "9．乙方若疏于管理或安全制度措施不落实导致出现各类安全隐 患或存在其他违约行为，丙方有权代表甲方对其进行处以违约金、追 究损失等，相关违约金、补偿金等全部款项归属甲方所有。协助、配 合安全事故的调查处理工作。 10．负责安全事故的调查处理工",
  "similarity": 0.900523560209424,
  "threshold": 0.98
}
```

#### ev-00052-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 33
- Baseline page: 37
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=25, baseline=24.

Metadata:

```json
{
  "baseline_count": 24,
  "candidate_count": 25,
  "element_type": "paragraph"
}
```

### Candidate Page 34

#### ev-00053-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 34
- Baseline page: 38
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.8655 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "改等。 8．应在监理日报中向甲方、丙方报告当天的安全文明施工问题， 并附记录照片； 9．按照甲方、丙方要求设置专职安全监理工程师。 10．乙方应当按照法律、法规和工程建设强制性标准及监理委 托合同实施监理，对所监理工程的施工安全生产进行监督",
  "candidate_text_preview": "9．按照甲方、丙方要求设置专职安全监理工程师。 10．乙方应当按照法律、法规和工程建设强制性标准及监理委托 合同实施监理，对所监理工程的施工安全生产进行监督检查，并对施 工安全生产承担监理责任。 11．乙方应当审查施工组织设计中的安全技术措",
  "similarity": 0.8655387355298308,
  "threshold": 0.98
}
```

#### ev-00054-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 34
- Baseline page: 38
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=25, baseline=24.

Metadata:

```json
{
  "baseline_count": 24,
  "candidate_count": 25,
  "element_type": "paragraph"
}
```

### Candidate Page 35

#### ev-00055-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 35
- Baseline page: 39
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.8295 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "19．检查施工现场各种安全标志和安全防护设施是否符合强制 性标准要求，并审查安措费的使用情况。 20．至少每周组织所有参建各方进行一次工程安全文明施工专 项检查。 21．乙方应派专人对施工现场安全生产情况进行巡视检查，对 发现的各类安全隐患",
  "candidate_text_preview": "项检查。 21．乙方应派专人对施工现场安全生产情况进行巡视检查，对发 现的各类安全隐患，应书面通知总承包方、分包单位，并督促其立即 整改；情况严重的，监理单位应及时下达工程暂停令，要求总承包方、 分包单位停工整改，并同时报告甲方、丙方。安全",
  "similarity": 0.8295254833040422,
  "threshold": 0.98
}
```

#### ev-00056-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 35
- Baseline page: 39
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=25, baseline=24.

Metadata:

```json
{
  "baseline_count": 24,
  "candidate_count": 25,
  "element_type": "paragraph"
}
```

### Candidate Page 36

#### ev-00057-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 36
- Baseline page: 40
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.8386 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "复制、使用或以任何方式披露给第四方，除法律、法规要求披露的 情形除外。 第五条 其他约定 1．如因不可抗力，或非合作方所能控制或所能预见事件的发生， 包括但不限于自然灾害、战争、罢工、政府行为、社会骚乱等情况， 而不能履行其义务的，经三方协",
  "candidate_text_preview": "包括但不限于自然灾害、战争、罢工、政府行为、社会骚乱等情况， 而不能履行其义务的，经三方协商一致，可终止本协议的履行。 2．本协议未尽事宜三方可另行协商确定，若协商不成，任何一 方可向甲方所在地有管辖权的人民法院起诉。 3．本协议自甲乙丙三",
  "similarity": 0.8385899814471243,
  "threshold": 0.98
}
```

#### ev-00058-paragraph_deleted

- Diff type: paragraph_deleted
- Category: paragraph
- Severity: medium
- Candidate page: 36
- Baseline page: 40
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=11, baseline=14.

Metadata:

```json
{
  "baseline_count": 14,
  "candidate_count": 11,
  "element_type": "paragraph"
}
```

### Candidate Page 37

#### ev-00059-layout_changed

- Diff type: layout_changed
- Category: layout
- Severity: medium
- Candidate page: 37
- Baseline page: 42
- Candidate element: None
- Baseline element: None
- Message: Page alignment confidence is low and needs review.

Metadata:

```json
{
  "alignment_reason": "Best baseline page only reached the low confidence threshold.",
  "alignment_score": 0.7159590043923866,
  "baseline_index": 41,
  "baseline_page_number": 42,
  "candidate_index": 36,
  "candidate_page_number": 37,
  "expected_baseline_index": 40,
  "forward_baseline_skip": 1,
  "is_forward_sequence_match": true,
  "search_window": 2
}
```

### Candidate Page 38

#### ev-00060-text_modified

- Diff type: text_modified
- Category: text
- Severity: medium
- Candidate page: 38
- Baseline page: 43
- Candidate element: None
- Baseline element: None
- Message: Page text similarity 0.8620 is below threshold 0.9800.

Metadata:

```json
{
  "baseline_text_preview": "六、合作中严格落实《项目EHS 管理行为标准》、《项目EHS 管理状态标 准》等安全文明施工标准要求，保证安全文明施工措施费专款专用，积极争创 安全文明施工标准化工地，营造“安全、干净、整洁”的工作环境。 七、严格落实职业危害告知、日常监测",
  "candidate_text_preview": "明施工标准化工地，营造“安全、干净、整洁”的工作环境。 七、严格落实职业危害告知、日常监测、个体防护以及职业健康体检等制度 措施，尊重、引导项目自身员工依法享有的EHS 的权益和义务，为员工提供符合 国家标准或行业标准的劳动保护用品，保护员",
  "similarity": 0.861995753715499,
  "threshold": 0.98
}
```

#### ev-00061-paragraph_added

- Diff type: paragraph_added
- Category: paragraph
- Severity: medium
- Candidate page: 38
- Baseline page: 43
- Candidate element: None
- Baseline element: None
- Message: paragraph element count changed: candidate=17, baseline=15.

Metadata:

```json
{
  "baseline_count": 15,
  "candidate_count": 17,
  "element_type": "paragraph"
}
```

### Candidate Page 39

#### ev-00062-page_added

- Diff type: page_added
- Category: page
- Severity: high
- Candidate page: 39
- Baseline page: None
- Candidate element: None
- Baseline element: None
- Message: Candidate document contains an added page; see page_issue_category metadata for review context.

Review context:

- Page issue category: likely_page_number_residue
- Suggested review severity: low
- Classification reason: Short page text appears to contain only page-number residue.

Page profile:

- Text length: 11
- Is blank: False
- Element count: 1
- Element type counts: {"paragraph": 1}
- Text preview: 第39页,共1237页

Metadata:

```json
{
  "alignment_reason": "No baseline page in the search window reached the low confidence threshold.",
  "alignment_score": 0.0,
  "baseline_cursor": 43,
  "candidate_index": 38,
  "candidate_page_number": 39,
  "classification_reason": "Short page text appears to contain only page-number residue.",
  "page_issue_category": "likely_page_number_residue",
  "page_profile": {
    "element_count": 1,
    "element_type_counts": {
      "paragraph": 1
    },
    "is_blank": false,
    "text_length": 11,
    "text_preview": "第39页,共1237页"
  },
  "search_window": 2,
  "suggested_review_severity": "low"
}
```

## Evidence Without Candidate Page

#### ev-00063-page_deleted

- Diff type: page_deleted
- Category: page
- Severity: high
- Candidate page: None
- Baseline page: 2
- Candidate element: None
- Baseline element: None
- Message: Baseline page is missing from the candidate document; see page_issue_category metadata for review context.

Review context:

- Page issue category: likely_toc_or_cover_format_noise
- Suggested review severity: medium
- Classification reason: Page text and page position suggest table-of-contents or cover formatting differences.

Page profile:

- Text length: 44
- Is blank: False
- Element count: 2
- Element type counts: {"paragraph": 2}
- Text preview: 监理人（全称）：同舟国际工程管理有限公司 代建人（全称）：深圳市润置城市建设管理有限公司

Metadata:

```json
{
  "alignment_reason": "Baseline page was not matched by any candidate page.",
  "alignment_score": 0.0,
  "baseline_index": 1,
  "baseline_page_number": 2,
  "classification_reason": "Page text and page position suggest table-of-contents or cover formatting differences.",
  "page_issue_category": "likely_toc_or_cover_format_noise",
  "page_profile": {
    "element_count": 2,
    "element_type_counts": {
      "paragraph": 2
    },
    "is_blank": false,
    "text_length": 44,
    "text_preview": "监理人（全称）：同舟国际工程管理有限公司 代建人（全称）：深圳市润置城市建设管理有限公司"
  },
  "suggested_review_severity": "medium"
}
```

#### ev-00064-page_deleted

- Diff type: page_deleted
- Category: page
- Severity: high
- Candidate page: None
- Baseline page: 3
- Candidate element: None
- Baseline element: None
- Message: Baseline page is missing from the candidate document; see page_issue_category metadata for review context.

Review context:

- Page issue category: likely_toc_or_cover_format_noise
- Suggested review severity: medium
- Classification reason: Page text and page position suggest table-of-contents or cover formatting differences.

Page profile:

- Text length: 1817
- Is blank: False
- Element count: 32
- Element type counts: {"paragraph": 32}
- Text preview: 目 录 第一部分 合同协议书................................................1 第二部分 通用条款...............................................

Metadata:

```json
{
  "alignment_reason": "Baseline page was not matched by any candidate page.",
  "alignment_score": 0.0,
  "baseline_index": 2,
  "baseline_page_number": 3,
  "classification_reason": "Page text and page position suggest table-of-contents or cover formatting differences.",
  "page_issue_category": "likely_toc_or_cover_format_noise",
  "page_profile": {
    "element_count": 32,
    "element_type_counts": {
      "paragraph": 32
    },
    "is_blank": false,
    "text_length": 1817,
    "text_preview": "目 录 第一部分 合同协议书................................................1 第二部分 通用条款..............................................."
  },
  "suggested_review_severity": "medium"
}
```

#### ev-00065-page_deleted

- Diff type: page_deleted
- Category: page
- Severity: high
- Candidate page: None
- Baseline page: 14
- Candidate element: None
- Baseline element: None
- Message: Baseline page is missing from the candidate document; see page_issue_category metadata for review context.

Review context:

- Page issue category: unknown_needs_manual_review
- Suggested review severity: high
- Classification reason: Unmatched page does not match deterministic low-noise page categories.

Page profile:

- Text length: 855
- Is blank: False
- Element count: 27
- Element type counts: {"paragraph": 27}
- Text preview: 4.3.6 监理费以人民币的形式办理转账结算。 4.3.7 每次付款前监理人须向委托人提供与应付监理费等额的增值税专用发票。否则， 委托人、委托人有权延期付款且不承担延期付款责任。 5、违约责任 5.1 合同双方之任何一方不能全面履行合同条

Metadata:

```json
{
  "alignment_reason": "Baseline page was not matched by any candidate page.",
  "alignment_score": 0.0,
  "baseline_index": 13,
  "baseline_page_number": 14,
  "classification_reason": "Unmatched page does not match deterministic low-noise page categories.",
  "page_issue_category": "unknown_needs_manual_review",
  "page_profile": {
    "element_count": 27,
    "element_type_counts": {
      "paragraph": 27
    },
    "is_blank": false,
    "text_length": 855,
    "text_preview": "4.3.6 监理费以人民币的形式办理转账结算。 4.3.7 每次付款前监理人须向委托人提供与应付监理费等额的增值税专用发票。否则， 委托人、委托人有权延期付款且不承担延期付款责任。 5、违约责任 5.1 合同双方之任何一方不能全面履行合同条"
  },
  "suggested_review_severity": "high"
}
```

#### ev-00066-page_deleted

- Diff type: page_deleted
- Category: page
- Severity: high
- Candidate page: None
- Baseline page: 26
- Candidate element: None
- Baseline element: None
- Message: Baseline page is missing from the candidate document; see page_issue_category metadata for review context.

Review context:

- Page issue category: likely_short_signature_or_date_page
- Suggested review severity: low
- Classification reason: Short page text contains signature, stamp, representative, or date markers.

Page profile:

- Text length: 27
- Is blank: False
- Element count: 4
- Element type counts: {"paragraph": 4}
- Text preview: 电话： 年 月 日 丙方监督单位：（盖章） 年 月 日

Metadata:

```json
{
  "alignment_reason": "Baseline page was not matched by any candidate page.",
  "alignment_score": 0.0,
  "baseline_index": 25,
  "baseline_page_number": 26,
  "classification_reason": "Short page text contains signature, stamp, representative, or date markers.",
  "page_issue_category": "likely_short_signature_or_date_page",
  "page_profile": {
    "element_count": 4,
    "element_type_counts": {
      "paragraph": 4
    },
    "is_blank": false,
    "text_length": 27,
    "text_preview": "电话： 年 月 日 丙方监督单位：（盖章） 年 月 日"
  },
  "suggested_review_severity": "low"
}
```

#### ev-00067-page_deleted

- Diff type: page_deleted
- Category: page
- Severity: high
- Candidate page: None
- Baseline page: 32
- Candidate element: None
- Baseline element: None
- Message: Baseline page is missing from the candidate document; see page_issue_category metadata for review context.

Review context:

- Page issue category: likely_attachment_start_page_needs_manual_review
- Suggested review severity: high
- Classification reason: Page text suggests an attachment or commitment document start.

Page profile:

- Text length: 171
- Is blank: False
- Element count: 6
- Element type counts: {"paragraph": 6}
- Text preview: 附件4 关于指挥长职责承诺书 致宁波东方理工大学（暂名）： 由我司承建的宁波东方理工大学（暂名）校园建设项目永久校区 1 号地块 及 2 号地块 - 二期（东生活组团 -1 ）工程监理 ，我司承诺指挥长职责如下： 1. 指挥长是企业高层管理

Metadata:

```json
{
  "alignment_reason": "Baseline page was not matched by any candidate page.",
  "alignment_score": 0.0,
  "baseline_index": 31,
  "baseline_page_number": 32,
  "classification_reason": "Page text suggests an attachment or commitment document start.",
  "page_issue_category": "likely_attachment_start_page_needs_manual_review",
  "page_profile": {
    "element_count": 6,
    "element_type_counts": {
      "paragraph": 6
    },
    "is_blank": false,
    "text_length": 171,
    "text_preview": "附件4 关于指挥长职责承诺书 致宁波东方理工大学（暂名）： 由我司承建的宁波东方理工大学（暂名）校园建设项目永久校区 1 号地块 及 2 号地块 - 二期（东生活组团 -1 ）工程监理 ，我司承诺指挥长职责如下： 1. 指挥长是企业高层管理"
  },
  "suggested_review_severity": "high"
}
```

#### ev-00068-page_deleted

- Diff type: page_deleted
- Category: page
- Severity: high
- Candidate page: None
- Baseline page: 41
- Candidate element: None
- Baseline element: None
- Message: Baseline page is missing from the candidate document; see page_issue_category metadata for review context.

Review context:

- Page issue category: likely_attachment_start_page_needs_manual_review
- Suggested review severity: high
- Classification reason: Page text suggests an attachment or commitment document start.

Page profile:

- Text length: 284
- Is blank: False
- Element count: 9
- Element type counts: {"paragraph": 9}
- Text preview: 附件6 供方EHS 诚信承诺书 宁波东方理工大学（暂名）： 根据《中华人民共和国安全生产法》、《中华人民共和国环境保护法》、 《中华人民共和国职业病防治法》、《国家安全监管总局办公厅关于进一步加 强安全生产诚信体系建设的通知》（安监总厅[2

Metadata:

```json
{
  "alignment_reason": "Baseline page was not matched by any candidate page.",
  "alignment_score": 0.0,
  "baseline_index": 40,
  "baseline_page_number": 41,
  "classification_reason": "Page text suggests an attachment or commitment document start.",
  "page_issue_category": "likely_attachment_start_page_needs_manual_review",
  "page_profile": {
    "element_count": 9,
    "element_type_counts": {
      "paragraph": 9
    },
    "is_blank": false,
    "text_length": 284,
    "text_preview": "附件6 供方EHS 诚信承诺书 宁波东方理工大学（暂名）： 根据《中华人民共和国安全生产法》、《中华人民共和国环境保护法》、 《中华人民共和国职业病防治法》、《国家安全监管总局办公厅关于进一步加 强安全生产诚信体系建设的通知》（安监总厅[2"
  },
  "suggested_review_severity": "high"
}
```

#### ev-00069-page_deleted

- Diff type: page_deleted
- Category: page
- Severity: high
- Candidate page: None
- Baseline page: 44
- Candidate element: None
- Baseline element: None
- Message: Baseline page is missing from the candidate document; see page_issue_category metadata for review context.

Review context:

- Page issue category: likely_short_signature_or_date_page
- Suggested review severity: low
- Classification reason: Short page text contains signature, stamp, representative, or date markers.

Page profile:

- Text length: 28
- Is blank: False
- Element count: 3
- Element type counts: {"paragraph": 3}
- Text preview: 承诺单位主要负责人签字： 承诺单位（盖章）： 年 月 日

Metadata:

```json
{
  "alignment_reason": "Baseline page was not matched by any candidate page.",
  "alignment_score": 0.0,
  "baseline_index": 43,
  "baseline_page_number": 44,
  "classification_reason": "Short page text contains signature, stamp, representative, or date markers.",
  "page_issue_category": "likely_short_signature_or_date_page",
  "page_profile": {
    "element_count": 3,
    "element_type_counts": {
      "paragraph": 3
    },
    "is_blank": false,
    "text_length": 28,
    "text_preview": "承诺单位主要负责人签字： 承诺单位（盖章）： 年 月 日"
  },
  "suggested_review_severity": "low"
}
```
