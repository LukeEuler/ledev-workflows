# Java Review Rules

重点检查：

- `null` 边界、Optional 使用、集合空值和 NPE 风险。
- checked/unchecked exception 是否被错误吞掉或包装导致调用方无法处理。
- 事务边界、回滚条件、幂等、重复提交和部分失败。
- 线程安全、共享 mutable state、Executor 生命周期、锁和异步回调。
- try-with-resources、连接、流、文件句柄和客户端关闭。
- equals/hashCode/compareTo 契约、集合 key 稳定性和排序一致性。
- 泛型擦除、类型转换、反射和序列化兼容性。
- Spring/DI 配置、bean lifecycle、profile、配置默认值和环境差异。
- 时间、时区、BigDecimal 精度、rounding mode 和 money-like 计算。
- 单元测试、集成测试、mock 边界和事务/异步场景验证。
