---
name: "zero-doc-spec-coding"
description: "Zero-Doc Spec Coding 实践助手：将 PRD 转化为无文档的结构化测试契约，支持新需求转化、遗留代码逆向和契约驱动的重构。"
---

# Zero-Doc Spec Coding 助手

本 Skill 旨在辅助你实践 **Zero-Doc Spec Coding (零文档契约)** 方法论。它摒弃了传统的“先写文档/注释，再写代码”的低效模式，直接将业务意图（PRD 或需求）转化为严格结构化的测试代码（Test-as-Spec）。

**核心主张：我们不维护任何静态的注释或文档，我们只维护活的测试断言。**

## 核心工作流：PRD -> 测试契约 -> 实现代码

当用户提供需求、PRD 或一段遗留代码时，请遵循以下规则生成测试契约：

### 1. 结构化标签约束

你必须使用项目主流的测试框架（如 Jest/Vitest/PyTest），并在测试用例的描述块中严格植入以下标签：

*   **`@UseCase` (海平面用例)**：定义在最外层的 `describe` 块中。
    *   **命名约束 (重要)**：UseCase 的命名**必须是动名词（Gerund）或动宾结构（Verb-Noun）**，以明确表达动态的“业务意图”（例如：`RegisteringUser`、`ProcessOrder`、`ResettingPassword`），**严禁使用静态名词**（如 `UserRegistration`、`OrderSystem`）。
    *   格式：`describe('@UseCase [动名词/动宾结构]: [中文目标描述]', () => { ... })`
*   **`@MSS` (主成功场景)**：定义在 `it` 块中，描述必须 100% 满足的快乐路径。
    *   格式：`it('@MSS-[序号]: [中文期望行为]', () => { ... })`
*   **`@Ext` (扩展/异常流程)**：定义在 `it` 块中，描述错误处理和边界情况。
    *   格式：`it('@Ext-[序号]: [中文异常/分支行为]', () => { ... })`

### 2. 严禁生成独立说明文档

*   **不要写任何 JSDoc 或大段的块注释来描述业务流。**
*   **不生成静态 Markdown 文档**：除了可能用于维护系统能力层级的索引文件（如 `README_SPECS.md`）外，不要在项目内生成任何平铺的 Markdown 需求说明书。
*   业务规则必须且只能通过 `@MSS` 和 `@Ext` 的测试描述（`it` 块）以及内部的 `expect/assert` 断言来体现。
*   测试代码中的变量命名需具备极强的自解释性，充当隐性文档。

### 3. 代码生成示例

```typescript
// 好的 Zero-Doc Spec 示例：意图与断言合一
describe('@UseCase RegisteringUser: 用户使用邮箱和密码注册新账户', () => {
    
    // @MSS: Main Success Scenario (主成功流程)
    it('@MSS-1: 提交有效信息应成功创建账户并返回成功消息', async () => {
        const result = await register('test@example.com', 'StrongPass123!');
        
        // 核心断言：状态变更与返回值即业务契约
        expect(result.status).toBe('success');
        expect(await findUser('test@example.com')).toBeDefined();
    });

    // @Extensions: 异常与分支流程
    it('@Ext-2a: 邮箱格式无效应拒绝并报错', async () => {
        const result = await register('invalid-email', 'StrongPass123!');
        expect(result.error).toBe('InvalidEmail');
    });

    it('@Ext-2b: 邮箱已被占用应拒绝并报错', async () => {
        await register('existing@example.com', 'Pass1'); // Setup
        const result = await register('existing@example.com', 'Pass2');
        expect(result.error).toBe('EmailAlreadyExists');
    });
});
```

## 适用场景指令

### 场景一：新功能开发 (PRD 转契约)
**用户指令**：提供一份 PRD 或口头需求。
**你的动作**：
1. 提取需求中的核心业务目标，设计出符合“动名词/动宾结构”的用例名称（如 `CreateOrder`）。
2. 输出包含 `@UseCase`、`@MSS`、`@Ext` 标签的结构化测试代码骨架（只包含断言，不包含具体的实现逻辑）。
3. 如果适用，建议用户将该用例补充到系统的 `README_SPECS.md` 能力地图中。
4. 提示用户：“请审查上述测试契约，如果确认无误，我将开始生成实现代码。”

### 场景二：遗留系统治理 (代码逆向契约)
**用户指令**：提供一段没有文档的遗留代码，要求“提取 Spec”或“重构”。
**你的动作**：阅读代码，反向推导出它的 `@UseCase`（动名词命名）、`@MSS` 和 `@Ext`，并输出一份重构后的测试用例文件。这份测试文件将作为后续安全重构的“行为快照”。

### 场景三：需求变更 (修改契约)
**用户指令**：“将密码长度要求从 8 位改为 12 位”。
**你的动作**：找到对应的测试文件，修改相关 `@Ext` 测试用例中的期望值（断言）。修改测试后，再定位到实现代码并进行相应的逻辑修复，确保测试重新通过。
