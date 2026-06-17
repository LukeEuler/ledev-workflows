# Python Review Rules

重点检查：

- 异常是否被过宽捕获、吞掉或转换后丢失上下文；错误路径是否可诊断。
- `None`、空集合、truthy/falsy 判断是否混淆有效值和缺失值。
- 可变默认参数、浅拷贝、全局状态和缓存是否引入跨调用污染。
- 文件、网络连接、临时目录、锁和数据库游标是否正确关闭或使用 context manager。
- async/await、task cancellation、timeout、blocking I/O 和事件循环边界是否正确。
- 类型标注、dataclass/Pydantic/model schema 是否和运行时输入输出一致。
- 时间时区、浮点/Decimal、JSON 序列化、路径编码和 locale 是否存在兼容风险。
- 包导入、副作用 import、相对导入、可选依赖和入口脚本是否在目标运行环境可用。
- SQL/命令执行/反序列化/模板渲染是否存在注入或不可信输入风险。
- 测试是否覆盖异常路径、边界输入、并发/异步行为、fixture 隔离和回归场景。
