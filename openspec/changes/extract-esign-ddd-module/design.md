# 电子签署 DDD 模块设计

## 1. 当前事实与证据

分析基线：`yuxiaor-pms` `master@fb6b634b7a7383903a7c2672502fd4b631236717`。

| 事实 | 证据 |
|---|---|
| 根模块当前为 `yuxiaor-server`、`yuxiaor-schedule`、`yuxiaor-api`、`yuxiaor-risk-control` | `yuxiaor-pms/pom.xml` |
| 电子签署核心实现集中在 `service/elcsignature`，约68个文件 | `yuxiaor-pms/yuxiaor-server/src/main/java/com/dream/yuxiaor/service/elcsignature/` |
| PDF、签署流程和供应商辅助类集中在 `helper/esign`，约19个文件 | `yuxiaor-pms/yuxiaor-server/src/main/java/com/dream/yuxiaor/helper/esign/` |
| E签宝/平安远程适配集中在 `service/remote/elcsignature`，约27个文件 | `yuxiaor-pms/yuxiaor-server/src/main/java/com/dream/yuxiaor/service/remote/elcsignature/` |
| 公寓实名入口包括 `/api/v1/certification` 与 `/local/company/auth/**` | `CertificationController.java`、`CompanyCertificationService.java`、`YxrCompanyAuthServiceImpl.java` |
| 签署主体本地契约位于 `/local/company-subsidiary/**` | `YxrCompanySubsidiaryService.java`、`CompanySubsidiaryOutService.java` |
| 个人/租客刷脸契约位于 `/local/faceAuth/**` 与 `/local/renterFaceSign/**` | `PersonFaceAuthService.java`、`PersonFaceAuthServiceImpl.java`、`IRenterFaceSignService.java`、`RenterFaceSignServiceImpl.java` |
| 港澳台证件映射位于 `EsignChannelUtil` 与 `IdCardTypeEnums`，支持回乡证、台胞证并按 `M` 前缀区分澳门 | `EsignChannelUtil.java` 第182-198、662-684行；`IdCardTypeEnums.java` |
| 企业/个人用户实名包含 `service/orgsign/FlatmateSignService.java` | `/local/flatmate-realname-auth/**` 实现 |
| 供应商回调位于 `/api/elcsign/{realName,faceAuth,contractSign,willingSignReject,orgAuth}` | `EsignatureCallBackController.java` |
| 意愿签署入口位于 `/api/v1/contract-willing-sign/**` 与 `/local/contractSignMethod/**` | `CompanyContractWillingSignController.java`、`IContractSignMethodService.java` |
| 服务器依赖外部电子签 API：`elc-signature-api`、`yuxiaor-e-signature-api` | `yuxiaor-server/pom.xml` 第142-154行 |
| 相关测试约80个，覆盖意愿签署、回调、主体、PDF、刷脸、实名和性能基线 | `yuxiaor-server/src/test/java/` |

### 当前耦合特征

仅统计 `service/elcsignature`、`helper/esign`、`service/remote/elcsignature` 的 import，可观察到：

- 182 个 `com.dream.yuxiaor.service.*` 导入；
- 106 个 `entity.*` 导入；
- 102 个 `utils.*` 导入；
- 76 个 `model.*` 导入；
- 72 个 `mappers.*` 导入；
- 152 个外部 `com.yuxiaor.pms.esign.*` 导入。

这说明不能做简单文件搬移。若新模块直接依赖 server，会形成 Maven 循环；若一次性移动全部共享实体，会破坏合同、公寓、租客上下文。因此设计重点是用端口和防腐层切断依赖，而不是机械搬目录。

## 2. 目标架构

### 2.1 模块定位

新增：

```text
yuxiaor-pms/yuxiaor-esign/
├── pom.xml
└── src/main/java/com/dream/yuxiaor/esign/
   ├── subject/       # 签署主体与实名上下文
   ├── face/          # 刷脸认证上下文
   ├── contractsign/  # 合同签署、盖章、意愿签署上下文
   └── shared/        # 上下文内值对象、端口和公共策略
```

每个子上下文内部采用：

```text
domain/
  model/          # 聚合、实体、值对象、领域异常
  service/        # 纯领域策略
  repository/     # 仓储接口
application/
  command/        # 写用例
  query/          # 读用例
  callback/       # 供应商回调用例
  port/in/        # 兼容门面调用的入站接口
  port/out/       # 供应商、外部上下文、文件、事件、时钟等出站端口
infrastructure/
  persistence/    # MyBatis仓储实现、mapper接口、XML
  vendor/         # E签宝、君子签、平安、支付宝刷脸适配
  messaging/      # MQ事件与消费适配
  file/           # PDF、上传、下载适配
  config/         # 模块内配置装配
adapter/
  legacy/         # 旧 FQCN 兼容门面
  mapper/         # 领域模型与DTO/legacy模型转换
```

### 2.2 Maven 依赖方向

```text
yuxiaor-api
    ↑
yuxiaor-esign
    ↑
yuxiaor-server
```

规则：

1. `yuxiaor-server` 依赖 `yuxiaor-esign`。
2. `yuxiaor-esign` 依赖 `yuxiaor-api`、`elc-signature-api`、`yuxiaor-e-signature-api`、`pms-server-parent` 等外部库。
3. `yuxiaor-esign` 不依赖 `yuxiaor-server`。
4. `yuxiaor-server` 实现模块定义的跨上下文出站端口。
5. 启动类仍扫描 `com.dream.yuxiaor`，模块 Bean 被当前单体加载。

### 2.3 DDD 依赖方向

```text
adapter/legacy ─→ application/port/in ─→ application/use case
                                          │
                                          ↓
                                       domain
                                          ↑
                              infrastructure 实现 port/out
                                          ↑
                        yuxiaor-server 提供跨上下文端口实现
```

约束：

- domain 不感知 Spring Web、MyBatis、Feign、Redis、MQ、供应商 DTO。
- application 可编排事务和用例，但技术细节只出现在端口。
- infrastructure 可依赖技术组件，但不得包含业务决策。
- adapter 只做协议、DTO 和异常转换，不写业务规则。
- 兼容门面保留旧 FQCN 和方法签名，内部委托新用例。

## 3. 限界上下文与聚合设计

### 3.1 SignSubject / 签署主体与实名

聚合根：`SignSubject`。

覆盖：

- 公寓/企业实名；
- 公司签署主体、个人签署主体；
- C端企业/个人实名；
- 电子签署账号ID映射；
- 主体实名、驳回、作废、删除和默认主体规则；
- 租客身份证、护照、港澳来往大陆通行证、台湾来往大陆通行证映射。

关键值对象：

- `SubjectId`
- `CompanyId`
- `CertificateType`
- `ElectronicSignAccountId`
- `SubjectAuthStatus`
- `SubjectType`

核心不变量：

1. 同一公司下有效签署主体的业务唯一性规则保持不变。
2. 电子签署账号ID与主体类型、原始ID的生成/反解规则保持不变。
3. 证件类型映射必须保持既有枚举值和香港/澳门/台湾区分逻辑。
4. 主体状态只能按既有状态机推进。
5. 供应商账号删除、默认主体重算和事务提交后动作保持原顺序。

### 3.2 FaceAuthentication / 刷脸认证

聚合根：`FaceAuthentication`。

覆盖：

- 个人/租客刷脸URL发起；
- 支付宝刷脸初始化和结果确认；
- TAPP结果查询；
- 刷脸配置和最大次数；
- 刷脸回调；
- 合同/账单跳过认证的既有兼容行为。

关键值对象：

- `FlowId`
- `FaceScene`
- `FaceMode`
- `FaceAuthStatus`
- `QuotaSnapshot`

核心不变量：

1. `flowId` 是回调幂等键。
2. 成功回调只允许扣减一次公寓刷脸服务次数。
3. 失败/取消不得触发成功状态。
4. 认证结果必须回写到正确场景：合同、租客签署或账单。
5. Redis缓存键与过期语义在兼容门面中保持不变。

### 3.3 ContractSigning / 合同签署与盖章

聚合根：`ContractSigning`，下辖主合同与附加协议任务。

覆盖：

- 签署方式决策：刷脸、手签、意愿、自动；
- PDF准备策略；
- 主合同/附加协议签署流程；
- 公寓批量意愿签署；
- 租客意愿签署；
- 供应商签署、盖章、文件回传；
- 拒签和死信补偿；
- 合同签署状态查询。

关键值对象：

- `ContractFileKey`
- `ContentRevision`
- `SigningFlowId`
- `SignerRole`
- `SigningChannel`
- `SigningStatus`

核心不变量：

1. flowId 绑定签署时的内容版本，不跨版本复用。
2. 主合同和附加协议状态独立推进，整体任务状态由二者推导。
3. 回调按合同类型路由到既有处理器，不能重复更新合同或附件。
4. 拒签原因、空白原因、状态时间戳保持现有语义。
5. 远端流程恢复和本地状态补偿必须先校验合同与主体归属。

## 4. 端口设计

### 4.1 入站端口

为旧调用方提供稳定用例接口：

- `StartCompanyRealNameUseCase`
- `StartSubjectRealNameUseCase`
- `StartTenantRealNameUseCase`
- `ResolveSignMethodUseCase`
- `StartFaceAuthenticationUseCase`
- `QueryFaceAuthenticationResultUseCase`
- `StartWillingSignUseCase`
- `SignContractUseCase`
- `HandleSigningCallbackUseCase`
- `RejectWillingSignUseCase`
- `RecoverSigningFlowUseCase`

兼容层可将 `EsignatureApi`、`CompanyContractWillingSignService`、`TenantContractWillingSignService`、`ContractSignMethodService`、`PersonFaceAuthService`、`RenterFaceSignService`、`FlatmateSignService` 等旧接口委托到上述用例。

### 4.2 出站端口

| 端口 | 用途 | 实现位置 |
|---|---|---|
| `ElectronicSignVendorGateway` | 账号、实名、刷脸、签署、盖章、流程查询、删除 | module infrastructure/vendor |
| `SignSubjectRepository` | 签署主体与电子签账号持久化 | module infrastructure/persistence 或 server 适配器 |
| `FaceAuthenticationRepository` | 刷脸状态、流水、幂等键 | module infrastructure/persistence |
| `WillingSignTaskRepository` | 意愿签署任务、批次、拒签、快照 | module infrastructure/persistence |
| `ContractContextPort` | 合同、附件、附加协议、内容版本读取与签署状态推进 | yuxiaor-server 适配器 |
| `CompanyContextPort` | 公寓资料、实名状态、服务次数、配置读取/扣减 | yuxiaor-server 适配器 |
| `TenantContextPort` | 租客、用户、C端企业信息与实名状态 | yuxiaor-server 适配器 |
| `FileStoragePort` | PDF和签署文件上传/下载 | module infrastructure/file |
| `PdfRenderPort` | HTML/模板渲染与签署页处理 | module infrastructure/file |
| `EventPublisherPort` | 应用事件、MQ、领域事件 | module infrastructure/messaging |
| `CallbackVerifier` | 供应商回调验签 | module infrastructure/vendor |
| `ClockPort` / `IdGeneratorPort` | 时间与ID隔离 | module infrastructure |

### 4.3 数据所有权

#### 模块拥有写入权

- `t_company_willing_sign`
- `t_company_willing_sign_task`
- `t_tenant_contract_willing_sign`
- `t_tenant_contract_sign_snapshot`
- 刷脸认证状态/流水表
- 迁移完成后确认仅由电子签署上下文写入的主体实名局部表

#### 共享上下文拥有，模块仅通过端口访问

- `Company`、公寓服务次数、公司配置；
- `AptContract`、合同附件、附加协议；
- `Flatmate`、`UserFlatmate`、`UserAccount`；
- `PersonIdentity` 等被智能设备/门禁等上下文复用的身份表。

迁移期间如果共享表仍被旧代码访问，必须先通过端口收敛电子签署相关写入，再删除旧直连路径，避免双写。

## 5. 对外契约冻结清单

### 5.1 应用/回调路由

- `GET /api/v1/certification`
- `GET /api/elcsign/time`
- `POST /api/elcsign/realName`
- `POST /api/elcsign/faceAuth`
- `POST /api/elcsign/contractSign`
- `POST /api/elcsign/willingSignReject`
- `POST /api/elcsign/orgAuth`
- `POST /api/v1/contract-willing-sign/url`
- `POST /api/v1/contract-willing-sign/batch-url`
- `GET  /api/v1/contract-willing-sign/tasks`
- `GET  /api/v1/contract-willing-sign/status`
- `GET  /api/v1/contract-willing-sign/statistics`
- `GET  /api/v1/contract-willing-sign/personal-subjects`

### 5.2 本地 HTTP / Feign 契约

- `/local/company/auth/saveOrAuth`
- `/local/company/auth/getAuthUrl`
- `/local/faceAuth/getRenterFaceSignUrl`
- `/local/faceAuth/personFaceAuthUrl`
- `/local/faceAuth/setFaceAuthMode`
- `/local/faceAuth/setMaxLimitNum`
- `/local/faceAuth/getFaceAuthResultOld`
- `/local/faceAuth/getFaceResult4Tapp`
- `/local/faceAuth/getFaceAuthConf`
- `/local/faceAuth/setContractSkipAuthed`
- `/local/renterFaceSign/getSignMethod`
- `/local/renterFaceSign/handleFaceSignSuccess`
- `/local/renterFaceSign/getPersonFaceAuthUrl`
- `/local/contractSignMethod/getSignMethodByContract`
- `/local/contractSignMethod/startWillingSign`
- `/local/contractSignMethod/startWillingSignUrl`
- `/local/contractSignMethod/getWillingSignStatus`
- `/local/company-subsidiary/getSubsidiaryWithCompany`
- `/local/company-subsidiary/rejectCompanySubsidiary/{subsidiaryId}`
- `/local/company-subsidiary/delCompanySubsidiary/{subsidiaryId}`
- `/local/flatmate-realname-auth/genQRCode`
- `/local/flatmate-realname-auth/getFlatmateSign/{userId}`
- `/local/flatmate-realname-auth/submitFlatmateSign`
- `/local/flatmate-realname-auth/revokeFlatmateSign/{userId}`
- `/local/flatmate-realname-auth/revokePSFlatmateSign/{userId}`
- `/local/flatmate-realname-auth/getRealNameUrl/{userId}`
- `/local/flatmate-realname-auth/getPSRealNameUrl/{userId}`
- `/local/flatmate-realname-auth/personVerify`

所有相关嵌套 Feign client 的 service name 均保持 `yuxiaor-server`。

## 6. 关键技术决策

### 6.1 不做简单搬移，先建立兼容门面

直接移动旧类会造成 controller、合同服务、公寓服务等大量调用方编译失败。迁移策略：

1. 在新模块建立 application use case 和端口；
2. 旧 FQCN 先变成兼容门面，委托 use case；
3. 调用方逐批切换或继续使用兼容门面；
4. 行为基线稳定后删除重复实现。

这样可以保证每个阶段可编译、可测试、可回滚。

### 6.2 拆解 `EsignChannelUtil`

`EsignChannelUtil` 同时承担账号ID生成、渠道选择、供应商调用、证件映射、实名URL、刷脸和账号删除，是当前最大耦合点。目标拆为：

- `VendorGatewayAdapter`：只包装远端调用和结果转换；
- `AccountIdMapper`：账号ID生成/反解；
- `SigningChannelPolicy`：渠道选择；
- `CertificateTypeMapper`：身份证/护照/港澳台/台胞证映射；
- `SubjectAccountAssembler`：从各上下文快照组装供应商账号DTO；
- `RealNameFlowService`：实名URL和结果查询。

### 6.3 保持 Spring Bean 与扫描兼容

- 新模块继续使用 `com.dream.yuxiaor` 根包，当前启动类扫描无需修改。
- 兼容门面必须保持原 Bean 类型、名称和可选限定符。
- `@Async("eSignCallback")`、MQ binding、事务提交后动作和线程池语义先原样迁移，性能优化不纳入本次范围。
- 对同一业务契约禁止同时保留旧实现和新实现两个主 Bean。

### 6.4 MyBatis 迁移策略

模块-owned mapper 使用既有包前缀 `com.dream.yuxiaor.mappers.work` 和资源路径 `mappers/work/**/*.xml`，利用当前 `MasterDSConfig` 的扫描与 XML pattern 加载；必要时增加模块配置类，但不改变数据源。共享表继续留在 server，通过端口访问。

### 6.5 事务与远端调用

迁移前必须用测试确认每个用例的事务边界：

- 数据库状态更新和跨上下文端口更新是否同事务；
- 供应商调用是否在事务外；
- `@Async` 回调何时提交；
- MQ事件是否在事务提交后发送。

迁移后保持等价。若发现现有实现存在事务缺陷，只记录为独立后续变更，不在本次重构中顺手修复。

## 7. 迁移阶段

1. **契约基线**：抓取HTTP/Feign映射、关键输入输出和异常；跑现有相关测试。
2. **模块骨架**：新增Maven模块、分层目录、依赖测试和空兼容门面。
3. **主体与实名**：先迁移纯规则和供应商适配，再迁移公寓实名、签署主体、C端实名与港澳台映射。
4. **刷脸认证**：迁移状态、限额、回调与结果查询。
5. **合同签署与意愿签署**：按PDF准备、签署方式决策、任务状态机、回调处理、拒签/补偿分批迁移。
6. **旧路径收敛**：server 调用方切到兼容门面或用例端口，删除重复旧实现和无效依赖。
7. **全量验证**：模块测试、server联合测试、契约快照、分层依赖、构建和回归门禁。

## 8. 风险与对策

| 风险 | 影响 | 对策 |
|---|---|---|
| 大量旧调用方依赖旧 FQCN | 编译失败或行为漂移 | 保留兼容门面，分批切换 |
| 共享表双写 | 数据不一致 | 明确数据所有权，端口收敛写入，删除旧路径前跑契约测试 |
| 回调重复消费 | 签署状态重复推进、重复扣次数 | flowId/authId幂等测试先行 |
| PDF内容版本错配 | 签署旧文件 | 保留ContentRevision绑定和快照契约测试 |
| 供应商渠道行为差异 | 实名/签署失败 | VendorGateway防腐层保留渠道策略，不合并供应商语义 |
| 事务/异步边界漂移 | 状态不可见或重复副作用 | 先做 characterization test，迁移时不改变边界 |
| Maven循环 | 构建失败 | 模块禁止依赖server，server实现模块端口 |
| 一次性迁移过大 | 难以回滚 | 按阶段提交，每阶段可独立回滚 |

## 9. 明确不采用的设计

### 9.1 直接拆独立微服务

不采用：需要新增部署、服务发现、网关、分布式事务和运维面，且用户要求现有 controller/API/Feign不变。

### 9.2 一次性移动全部类到新模块

不采用：会引入 `yuxiaor-esign -> yuxiaor-server` 循环或迫使合同/公寓/租客上下文同时大改，风险不可控。

### 9.3 新模块继续直接依赖server service/mapper/entity

不采用：模块位置变了但耦合不变，DDD边界失败，后续无法独立测试或演进。
