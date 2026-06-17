# Go Review Rules

重点检查：

- `context.Context` 是否透传、取消是否生效、是否错误使用 `context.Background()`。
- error 是否被忽略、覆盖、吞掉；wrap 是否保留可判断原因。
- goroutine 生命周期是否可控，是否泄漏，channel 是否可能阻塞、重复 close 或 send on closed channel。
- shared map、slice、struct 是否存在 data race；锁粒度和 defer unlock 是否正确。
- nil pointer、nil slice/map、zero value 和 interface nil 判断是否正确。
- `defer` 在循环、资源释放、文件/网络连接关闭上的成本和时机。
- JSON/YAML/tag、omitempty、默认值和 backward compatibility。
- 数值转换、time.Duration、时区和 decimal/float 精度。
- table-driven tests 是否覆盖新增边界；race-sensitive 变更是否需要 `go test -race`。
