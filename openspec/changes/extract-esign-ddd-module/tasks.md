# 任务清单

> 当前仅处于严格模式 Open 阶段，以下任务未开始实施。四件套确认后才进入独立 Design/实现计划。

- [x] 1. 契约与行为基线
  - [x] 1.1 在目标项目从 `master@fb6b634b7a` 创建严格模式隔离 worktree，确认工作区干净且不带用户未提交修改。
  - [x] 1.2 抓取并保存HTTP/Feign契约快照，覆盖 `yuxiaor-api` 中 company auth、face auth、renter face sign、contract sign method、company subsidiary、flatmate sign 相关接口和 server 中电子签署 controller。
  - [x] 1.3 梳理旧FQCN、Spring Bean type/name、`@Async`、MQ binding、事务提交后动作清单，形成兼容映射表。
  - [x] 1.4 运行现有相关测试基线：`cd yuxiaor-pms && mvn -s settings-work.xml -pl yuxiaor-server test -P dev,env-actuator -Denforcer.skip=true -Dtest='*Esign*,*WillingSign*,*Face*,*Flatmate*,*Subsidiary*,*Certification*'`。
  - [x] 1.5 记录基线结果、失败/跳过测试和不可复现环境，后续迁移不得改变既有失败集合。
    - 已用新克隆 `yuxiaor-e-signature`、本地匹配 `acc-bill-api` 快照恢复生产编译，并将相关测试适配到当前 JUnit 4 / Mockito 2.15 基线。
    - 最终原命令进入 Surefire：476 run / 12 failures / 7 errors / 2 skipped；完整失败/错误清单与日志哈希记录在 `yuxiaor-server/src/test/resources/esign-baseline/existing-test-baseline.md`。

- [x] 2. 新增模块骨架与分层门禁
  - [x] 2.1 修改 `yuxiaor-pms/pom.xml`，增加 `yuxiaor-esign` module。
  - [x] 2.2 新增 `yuxiaor-pms/yuxiaor-esign/pom.xml`，声明 JDK 8、`yuxiaor-api`、`elc-signature-api`、`yuxiaor-e-signature-api`、Spring/MyBatis/测试所需最小依赖，不依赖 `yuxiaor-server`。
  - [x] 2.3 创建 `com.dream.yuxiaor.esign.{subject,face,contractsign,shared}` 及各自 domain/application/infrastructure/adapter 目录。
  - [x] 2.4 增加模块层依赖测试，禁止 domain 导入 Spring Web/MyBatis/Feign/Redis/MQ/供应商SDK，禁止模块导入 server 内部 service/mapper/entity。
  - [x] 2.5 修改 `yuxiaor-pms/yuxiaor-server/pom.xml` 依赖 `yuxiaor-esign`。
  - [x] 2.6 验证：`cd yuxiaor-pms && mvn -s settings-work.xml -pl yuxiaor-esign,yuxiaor-server -am validate -P dev,env-actuator -Denforcer.skip=true`。

- [ ] 3. 签署主体与实名上下文
  - [x] 3.1 建立SignSubject聚合、证件类型值对象、主体状态机和账号ID映射领域模型，先写港澳台/护照/身份证映射领域测试。
    - 已完成首批：纯 JDK SignSubject/CertificateType/ElectronicSignAccountId/SubjectAuthStatus 领域模型，覆盖港澳台/护照/身份证映射和 4/3/6/7/8 账号前缀；模块测试 16/16 绿。
  - [ ] 3.2 抽取公寓实名、签署主体实名、C端企业/个人实名、主体驳回/作废/删除用例端口。
  - [ ] 3.3 将 `EsignChannelUtil` 中账号ID、渠道、账号创建、实名URL、证件类型映射拆到模块端口与infrastructure适配器。
  - [ ] 3.4 为合同、公寓、租客上下文建立出站端口，并在 `yuxiaor-server` 提供适配器；共享表写入先经端口收敛。
  - [ ] 3.5 迁移 `service/orgsign/FlatmateSignService`、`service/certification`、`service/elcsignature/realname` 中业务规则到用例，保留兼容门面。
    - 第二批已完成：`CompanyStatusCheckEventProcess` 与 `CompanySubsidiaryStatusEventProcess` 变更为兼容监听器，核心守卫与账号创建决策迁移至 `MaintainCompanyAccountUseCase`；既有 `ElectronicSignAccountNormalFlowTest` 4/4 绿。
    - 第三批已完成：公寓/签署主体/租客企业/业主个人 4 个实名回调处理器改为兼容门面，路由与状态传播决策迁移至 `HandleSubjectRealNameCallbackUseCase`，server 侧状态、事件、默认主体和用户同步副作用集中在 `SubjectRealNameCallbackServerAdapter`；模块 27/27、回调 characterization 10/10、回归 14/14、联合 validate 绿。
    - 第四批已完成：`FlatmateSignService.getPSRealNameUrl` 与 `revokePSFlatmateSign` 改为兼容门面，C 端个人实名资格、缓存复用、流程创建、撤销与本地状态清理决策迁移至 `StartPersonalRealNameUseCase` / `RevokePersonalRealNameUseCase`；server 侧身份、供应商账号、Redis TTL 和状态事件副作用集中在 `EsignPersonalRealNameServerAdapter`；模块 41/41、门面 6/6、相关回归 20/20、联合 validate 绿。
    - 第五批已完成：`FlatmateSignService.getRealNameUrl` 与 `revokeFlatmateSign` 改为兼容门面，C 端企业资料守卫、认证中缓存复用、供应商通过推进和撤销顺序迁移至 `ManageEnterpriseRealNameUseCase`；server 侧企业资料、供应商 URL、20 天认证缓存和本地状态写入集中在 `EsignEnterpriseRealNameServerAdapter`；模块 57/57、企业实名 characterization 9/9、相关回归 29/29、联合 validate 绿。
    - 第六批已完成：`CertificationAPI.getCertification` 保持 `REQUIRES_NEW` 门面，实名开关、城方/电子合同免计费、余额不足、本地/第三方结果和扣费决策迁移至 `AuthorizeCertificationUseCase`；server 侧服务次数扣减集中在 `EsignCertificationAuthorizationServerAdapter`；模块 65/65、实名 characterization 6/6、相关回归 35/35、联合 validate 绿。
    - 第七批已完成：主体驳回、取消认证与作废守卫迁移至 `ManageSubjectLifecycleUseCase`；`rejectCompanySubsidiary`、`unAuth`、`voidCompanySubsidiary` 保持事务门面，server 侧本地状态、解绑、默认主体重算与事务提交后供应商删除集中在 `EsignSubjectLifecycleServerAdapter`；模块 75/75、生命周期门面 5/5、既有 void 11/11、相关回归 59/59、联合 validate 绿。
    - 第八批已完成：`EsignChannelUtil` 中公寓、租客刷脸、租客个人、业主个人的账号 ID 编码/反解/类型判断切换到 `SubjectAccountIdentityPort`，由模块领域 `ElectronicSignAccountId` 提供唯一映射；模块 80/80、账号 ID 门面 4/4、相关回归 63/63、联合 validate 绿。
    - 第九批已完成：公寓账号组装决策收敛到 `CompanyAccountAssemblyPolicy` 与 `AssembleCompanyAccountUseCase`，server 侧供应商 DTO 转换使用同一字段回退规则；模块 85/85、组装 characterization 2/2、相关回归 65/65、联合 validate 绿。
    - 第十批已完成：公寓主体/签署信息共享表读取收敛到 `EsignCompanySubjectContextService`，`EsignSubjectServerAdapter` 不再直接访问 `CompanySubsidiaryMapper`；模块 85/85、相关回归 65/65、联合 validate 绿。
  - [ ] 3.6 迁移/新增主体、实名、港澳台映射测试，并运行模块测试。

- [ ] 4. 刷脸认证上下文
  - [ ] 4.1 建立FaceAuthentication聚合和FlowId幂等键，先写成功、失败、取消、重复回调、次数不足、结果查询测试。
  - [ ] 4.2 抽取刷脸URL、支付宝刷脸、TAPP结果、配置、最大次数和服务次数扣减端口。
  - [ ] 4.3 迁移 `PersonFaceAuthServiceImpl`、`RenterFaceSignServiceImpl`、`FaceAuthRealNameCallBackProcess` 业务逻辑到application use case。
  - [ ] 4.4 保留本地REST适配层的路由和签名，将其内部实现改为调用use case；不得改变 `/local/faceAuth/**`、`/local/renterFaceSign/**` 契约。
  - [ ] 4.5 迁移刷脸状态/流水mapper与XML到模块owned持久化，验证MyBatis扫描和数据源不变。

- [ ] 5. 合同签署、盖章与意愿签署上下文
  - [ ] 5.1 建立ContractSigning聚合、ContentRevision、任务状态机和签署方式决策领域模型，先写状态机与内容版本测试。
  - [ ] 5.2 抽取PDF准备、文件存储、合同上下文、供应商签署、事件发布、流程恢复端口。
  - [ ] 5.3 分批迁移 `helper/esign`、`service/elcsignature/contractsign`、`service/remote/elcsignature` 中PDF、签署、盖章、平安同步和回调处理逻辑。
  - [ ] 5.4 迁移公寓批量意愿签署、租客意愿签署、拒签、DLQ告警和补偿逻辑，保留任务表单一写入方。
  - [ ] 5.5 将 `/api/elcsign/**` 回调controller和 `/api/v1/contract-willing-sign/**` controller的依赖切换到兼容门面或use case，冻结注解和路由。
  - [ ] 5.6 迁移既有意愿签署、回调、PDF、性能基线测试到模块或联合测试位置，并补充缺失的幂等/拒签/内容版本测试。

- [ ] 6. 旧实现收敛与兼容清理
  - [ ] 6.1 将server中电子签署调用方切换到兼容门面或application端口，保持旧调用行为不变。
  - [ ] 6.2 删除已由模块替代的旧业务实现、重复mapper访问和无效依赖；仅删除电子签署路径，不触碰非本范围业务。
  - [ ] 6.3 检查Spring容器中相关Bean无重复主实现，`@Async`、线程池、MQ binding、事务后动作与基线一致。
  - [ ] 6.4 保持 `yuxiaor-api` 对外契约文件无契约性diff；如出现必须回退并重新设计。

- [ ] 7. 验证与严格门禁
  - [ ] 7.1 模块测试：`cd yuxiaor-pms && mvn -s settings-work.xml -pl yuxiaor-esign test -P dev,env-actuator -Denforcer.skip=true`。
  - [ ] 7.2 联合编译：`cd yuxiaor-pms && mvn -s settings-work.xml -pl yuxiaor-esign,yuxiaor-server -am clean validate compile -P dev,env-actuator -Denforcer.skip=true`。
  - [ ] 7.3 联合测试：`cd yuxiaor-pms && mvn -s settings-work.xml -pl yuxiaor-esign,yuxiaor-server -am test -P dev,env-actuator -Denforcer.skip=true`。
  - [ ] 7.4 HTTP/Feign契约快照测试与迁移前基线逐项一致。
  - [ ] 7.5 分层依赖、Maven无循环、无共享表双写检查通过。
  - [ ] 7.6 执行严格模式任务级审查和Verify双阶段审查；Critical/Important归零后才可归档。

## 本地整合策略

- 严格模式确认后在 `yuxiaor-pms` 内创建 feature branch 和隔离 worktree，不混入当前根仓库或目标仓库用户修改。
- 每个阶段独立提交，保持契约基线、模块骨架、主体/实名、刷脸、合同签署、清理和验证可分别回滚。
- 迁移期间不得提交生产配置或外部环境副作用；所有Maven命令仅本地执行。
