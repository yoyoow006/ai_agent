# 合同模板房源基准租金定价

- `{房源基准租金定价}` 在 `yuxiaor-pms/yuxiaor-server` 中映射 `AptContractServiceImpl.CTModel#basisRentPrice`。
- 渲染取值：`IRentPriceService#getRentPriceByResourceId(houseId, roomId)` 当前生效定价；`pricingMode=2` 取 `basisAreaPrice`，否则取 `basisPrice`。
- 输出：金额保留两位小数，固定月租单位`元/月`，按面积月租单位`元/m²·月`，并附人民币大写。
- 默认中文租客模板与默认业主模板把该行放在押金金额后；英文默认模板不包含该占位符。
- 模板编辑器四类配置 `contractTemplateParams1/2/5/6` 由 `V1_0_478_contract_template_basis_rent_price.sql` 幂等追加。
