# JavaScript and TypeScript Review Rules

重点检查：

- async/await、Promise rejection、并发请求顺序和取消/超时处理。
- `undefined`、`null`、optional chaining 和默认值是否掩盖错误。
- TypeScript 类型是否真实约束运行时；是否用 `any`、断言或宽类型绕过风险。
- 前后端运行时差异：browser、Node.js、Edge/runtime、SSR/hydration。
- 状态更新、闭包 stale value、React effect dependency 和 cleanup。
- 输入校验、XSS、CSRF、开放重定向、原型污染和敏感信息泄漏。
- JSON 序列化、Date/timezone、number precision、BigInt 和 locale。
- package/API 兼容性、tree-shaking、副作用 import 和 bundler 配置。
- 测试是否覆盖异步失败、交互状态、边界输入和回归路径。
